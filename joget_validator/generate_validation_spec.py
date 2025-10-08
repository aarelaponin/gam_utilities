#!/usr/bin/env python3
"""
Validation Specification Generator
Generates test-validation.yml from form definitions, services.yml, and test data
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from generators.spec_generator import ValidationSpecGenerator


def main():
    """Main function to run the specification generator"""

    parser = argparse.ArgumentParser(
        description='Generate validation specification from forms, mappings, and test data'
    )

    parser.add_argument(
        '--forms-dir',
        required=True,
        help='Directory containing form JSON definitions'
    )

    parser.add_argument(
        '--services',
        required=True,
        help='Path to services.yml file with field mappings'
    )

    parser.add_argument(
        '--test-data',
        required=True,
        help='Path to test-data.json file'
    )

    parser.add_argument(
        '--output',
        default='generated/test-validation.yml',
        help='Output path for generated specification (default: generated/test-validation.yml)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Validate input paths
    forms_dir = Path(args.forms_dir)
    if not forms_dir.exists() or not forms_dir.is_dir():
        print(f"Error: Forms directory not found: {forms_dir}")
        sys.exit(1)

    services_path = Path(args.services)
    if not services_path.exists():
        print(f"Error: services.yml not found: {services_path}")
        sys.exit(1)

    test_data_path = Path(args.test_data)
    if not test_data_path.exists():
        print(f"Error: test-data.json not found: {test_data_path}")
        sys.exit(1)

    # Create output directory if needed
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Validation Specification Generator")
    print("=" * 60)
    print(f"Forms Directory: {forms_dir}")
    print(f"Services YAML: {services_path}")
    print(f"Test Data: {test_data_path}")
    print(f"Output: {output_path}")
    print("-" * 60)

    try:
        # Initialize generator
        generator = ValidationSpecGenerator(
            forms_dir=str(forms_dir),
            services_yml=str(services_path),
            test_data_json=str(test_data_path),
            verbose=args.verbose
        )

        # Generate specification
        print("\nGenerating validation specification...")
        spec = generator.generate_spec()

        # Save specification
        generator.save_spec(str(output_path))

        # Print summary
        print("\n" + "=" * 60)
        print("GENERATION COMPLETE")
        print("-" * 60)

        if 'expected_state' in spec and 'tables' in spec['expected_state']:
            tables = spec['expected_state']['tables']
            print(f"Generated specifications for {len(tables)} tables:")

            total_records = 0
            for table_name, table_spec in tables.items():
                record_count = table_spec.get('record_count', 0)
                total_records += record_count
                print(f"  - {table_name}: {record_count} record(s)")

            print(f"\nTotal expected records: {total_records}")

        print(f"\nSpecification saved to: {output_path}")
        print("\nYou can now run validation with:")
        print(f"  python run_validation.py --spec {output_path}")

    except Exception as e:
        print(f"\nError generating specification: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()