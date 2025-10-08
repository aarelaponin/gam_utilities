#!/usr/bin/env python3
"""
Joget Registry Validator - Main CLI Entry Point
Validates whether test data has been correctly stored in the Joget MySQL database
"""

import sys
import argparse
import time
from pathlib import Path
from datetime import datetime

# Add the current directory to Python path to import modules
sys.path.insert(0, str(Path(__file__).parent))

from shared_utils.config import load_validation_config, setup_logging
from joget_validator.core.validator import RegistryValidator
from joget_validator.reports.console_reporter import ConsoleReporter
from joget_validator.reports.json_reporter import JSONReporter
from joget_validator.reports.html_reporter import HTMLReporter


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Joget Registry Validator - Validate data in Joget database against test data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic validation with default settings
  %(prog)s

  # Validate with custom paths
  %(prog)s --services /path/to/services.yml --test-data /path/to/test.json

  # Validate specific farmer
  %(prog)s --farmer farmer-001

  # Generate only JSON report
  %(prog)s --format json --output ./reports

  # Debug mode with verbose output
  %(prog)s --debug --verbose

  # Validate only specific form
  %(prog)s --form farmerBasicInfo

  # Test connections only
  %(prog)s --test-connections
        """
    )

    # Configuration options
    default_config_path = Path(__file__).parent / 'joget_validator' / 'config' / 'validation.yaml'
    parser.add_argument('--config', '-c',
                       default=str(default_config_path),
                       help='Path to validation config (default: joget_validator/config/validation.yaml)')

    parser.add_argument('--services', '-s',
                       help='Path to services.yml (overrides config)')

    parser.add_argument('--test-data', '-t',
                       help='Path to test-data.json (overrides config)')

    # Output options
    parser.add_argument('--format', '-f',
                       choices=['console', 'json', 'html', 'all'],
                       default='all',
                       help='Output format (default: all)')

    parser.add_argument('--output', '-o',
                       help='Output directory for reports (overrides config)')

    # Validation scope options
    parser.add_argument('--farmer',
                       help='Validate specific farmer by ID')

    parser.add_argument('--form',
                       help='Validate specific form only')

    parser.add_argument('--grid',
                       help='Validate specific grid only')

    # Execution options
    parser.add_argument('--test-connections',
                       action='store_true',
                       help='Test connections and configurations only')

    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='Enable verbose output')

    parser.add_argument('--debug',
                       action='store_true',
                       help='Enable debug logging')

    parser.add_argument('--quiet', '-q',
                       action='store_true',
                       help='Suppress console output (except errors)')

    args = parser.parse_args()

    try:
        # Load configuration
        config = load_validation_config(args.config)

        # Override config with command line arguments
        if args.services:
            config['data_sources']['services_yml'] = args.services
        if args.test_data:
            config['data_sources']['test_data'] = args.test_data
        if args.output:
            config['reporting']['output_directory'] = args.output

        # Setup logging
        if args.debug:
            config['logging']['level'] = 'DEBUG'
        elif args.verbose:
            config['logging']['level'] = 'INFO'
        elif args.quiet:
            config['logging']['level'] = 'ERROR'

        logger = setup_logging(config.get('logging', {}), 'joget_validator')

        if not args.quiet:
            print("Joget Registry Validator v1.0.0")
            print("=" * 50)

        # Initialize validator
        validator = RegistryValidator(
            services_config=config['data_sources']['services_yml'],
            test_data=config['data_sources']['test_data'],
            db_config=config['database'],
            validation_config=config
        )

        # Test connections if requested
        if args.test_connections:
            test_connections(validator, args.quiet)
            return

        # Perform validation
        if args.farmer:
            validate_specific_farmer(validator, args.farmer, config, args)
        elif args.form:
            validate_specific_form(validator, args.form, config, args)
        else:
            validate_all(validator, config, args)

    except KeyboardInterrupt:
        if not args.quiet:
            print("\n\nValidation interrupted by user")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def test_connections(validator: RegistryValidator, quiet: bool = False):
    """Test all connections and configurations"""
    if not quiet:
        print("Testing connections and configurations...")
        print()

    results = validator.test_connections()

    # Setup console reporter
    console_reporter = ConsoleReporter()
    console_reporter.print_connection_test_results(results)

    # Check if all tests passed
    all_passed = all(results.values())

    if not quiet:
        if all_passed:
            print("\n✓ All connection tests passed!")
        else:
            print("\n✗ Some connection tests failed!")

    sys.exit(0 if all_passed else 1)


def validate_all(validator: RegistryValidator, config: dict, args):
    """Validate all farmers"""
    if not args.quiet:
        print("Starting complete validation...")
        print()

    start_time = time.time()

    # Perform validation
    report = validator.validate_all()

    duration = time.time() - start_time

    # Generate reports
    generate_reports(report, config, args)

    if not args.quiet:
        print(f"\nValidation completed in {duration:.2f} seconds")

    # Exit with error code if validation failed
    if report.failed > 0:
        sys.exit(1)


def validate_specific_farmer(validator: RegistryValidator, farmer_id: str, config: dict, args):
    """Validate a specific farmer"""
    if not args.quiet:
        print(f"Validating farmer: {farmer_id}")
        print()

    start_time = time.time()

    # Perform validation
    farmer_result = validator.validate_specific_farmer(farmer_id)

    duration = time.time() - start_time

    if not farmer_result:
        print(f"Error: Farmer {farmer_id} not found in test data")
        sys.exit(1)

    # Generate console output
    if args.format in ['console', 'all'] and not args.quiet:
        console_reporter = ConsoleReporter(config.get('reporting', {}))
        console_reporter.print_farmer_summary(farmer_result)

    # Generate file reports if requested
    if args.format in ['json', 'all']:
        json_reporter = JSONReporter(config.get('reporting', {}))
        json_path = json_reporter.generate_farmer_json(farmer_result)
        if not args.quiet:
            print(f"JSON report saved: {json_path}")

    if not args.quiet:
        print(f"\nValidation completed in {duration:.2f} seconds")

    # Exit with error code if validation failed
    if farmer_result.status.value == 'FAILED':
        sys.exit(1)


def validate_specific_form(validator: RegistryValidator, form_name: str, config: dict, args):
    """Validate a specific form across all farmers"""
    if not args.quiet:
        print(f"Validating form: {form_name}")
        print()

    start_time = time.time()

    # Perform validation
    report = validator.validate_specific_form(form_name)

    duration = time.time() - start_time

    # Generate reports
    generate_reports(report, config, args)

    if not args.quiet:
        print(f"\nForm validation completed in {duration:.2f} seconds")

    # Exit with error code if validation failed
    if report.failed > 0:
        sys.exit(1)


def generate_reports(report, config: dict, args):
    """Generate validation reports in requested formats"""
    reporting_config = config.get('reporting', {})

    # Console output
    if args.format in ['console', 'all'] and not args.quiet:
        console_reporter = ConsoleReporter(reporting_config)
        console_reporter.generate(report)

    # JSON report
    if args.format in ['json', 'all']:
        json_reporter = JSONReporter(reporting_config)
        json_path = json_reporter.generate(report)

        # Also generate summary
        summary_path = json_reporter.generate_summary_json(report)

        if not args.quiet:
            print(f"\nJSON report saved: {json_path}")
            print(f"JSON summary saved: {summary_path}")

    # HTML report
    if args.format in ['html', 'all']:
        html_reporter = HTMLReporter(reporting_config)
        html_path = html_reporter.generate(report)

        if not args.quiet:
            print(f"HTML report saved: {html_path}")


if __name__ == '__main__':
    main()