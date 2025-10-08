#!/usr/bin/env python3
"""
Joget Data Utility - Main CLI
A configurable utility for importing data to Joget DX8 applications
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from joget_client import JogetClient, JogetAPIError
from processors.csv_processor import CSVProcessor
from processors.json_processor import JSONProcessor
from processors.metadata import MetadataProcessor
from processors.master_data_deployer import MasterDataDeployer
import utils


def process_single_endpoint(args, config):
    """Process a single endpoint with data file"""
    # Initialize client
    client = JogetClient(
        base_url=config['base_url'],
        api_key=config.get('default_api_key'),
        debug=args.debug
    )

    # Test connection if requested
    if args.test:
        print("Testing connection to Joget server...")
        if client.test_connection():
            print("✓ Connection successful")
        else:
            print("✗ Connection failed")
            sys.exit(1)
        return

    # Get endpoint configuration
    endpoint_config = None

    # Check metadata endpoints first
    if args.endpoint in config.get('metadata_endpoints', {}):
        endpoint_config = config['metadata_endpoints'][args.endpoint]
        endpoint_config['type'] = 'metadata'
    # Then check custom endpoints
    elif args.endpoint in config.get('endpoints', {}):
        endpoint_config = config['endpoints'][args.endpoint]
        endpoint_config['type'] = 'custom'
    else:
        print(f"Error: Unknown endpoint '{args.endpoint}'")
        print("\nAvailable endpoints:")
        print("  Metadata endpoints (code/name):")
        for name in config.get('metadata_endpoints', {}).keys():
            print(f"    - {name}")
        print("  Custom endpoints:")
        for name in config.get('endpoints', {}).keys():
            print(f"    - {name}")
        sys.exit(1)

    # Resolve input file path
    input_path = utils.resolve_data_path(args.input, config)

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    print(f"\nProcessing: {args.endpoint}")
    print(f"Input file: {input_path}")
    print(f"API ID: {endpoint_config['api_id']}")

    # Determine processor based on file type
    file_suffix = input_path.suffix.lower()
    if file_suffix == '.csv':
        processor = CSVProcessor()
    elif file_suffix == '.json':
        processor = JSONProcessor()
    else:
        print(f"Error: Unsupported file type: {file_suffix}")
        sys.exit(1)

    # Load and process data
    try:
        records = processor.read_file(input_path)
        print(f"Loaded {len(records)} records")
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Transform records based on endpoint type
    if endpoint_config['type'] == 'metadata':
        # Transform to code/name format
        transformed = []
        for record in records:
            if 'code' in record and 'name' in record:
                transformed.append({
                    'code': record['code'],
                    'name': record['name']
                })
            else:
                # Try to auto-detect fields
                fields = list(record.keys())
                if len(fields) >= 2:
                    transformed.append({
                        'code': str(record[fields[0]]),
                        'name': str(record[fields[1]])
                    })
    else:
        # Use field mapping for custom endpoints
        field_mapping = endpoint_config.get('field_mapping', {})
        required_fields = endpoint_config.get('required_fields', [])

        processor.field_mapping = field_mapping
        transformed = []

        for record in records:
            result = processor.transform_record(record, required_fields)
            if result:
                transformed.append(result)

    print(f"Transformed {len(transformed)} records")

    # Validation mode
    if args.validate:
        print("\nValidation complete:")
        if processor.errors:
            print("Errors found:")
            for error in processor.errors:
                print(f"  - {error}")
        else:
            print("✓ No errors found")
        return

    # Dry run mode
    if args.dry_run:
        print("\nDRY RUN MODE - No data will be posted")
        print("\nSample records (first 3):")
        for i, record in enumerate(transformed[:3], 1):
            print(f"\nRecord {i}:")
            print(utils.format_record_for_display(record))
        return

    # Confirm before posting
    if not args.yes and not utils.confirm_action(f"Post {len(transformed)} records to {args.endpoint}?"):
        print("Operation cancelled")
        return

    # Post data
    print(f"\nPosting {len(transformed)} records...")
    try:
        # Use full_path if specified, otherwise use endpoint name
        endpoint_path = endpoint_config.get('full_path', args.endpoint)

        results = client.batch_post(
            endpoint=endpoint_path,
            api_id=endpoint_config['api_id'],
            records=transformed,
            api_key=args.api_key or config.get('default_api_key'),
            stop_on_error=args.stop_on_error
        )

        utils.print_summary(results, verbose=args.verbose)

    except JogetAPIError as e:
        print(f"API Error: {e}")
        sys.exit(1)


def process_metadata_batch(args, config):
    """Process metadata batch file"""
    batch_file = Path(args.metadata_batch)

    if not batch_file.exists():
        print(f"Error: Batch file not found: {batch_file}")
        sys.exit(1)

    # Initialize processor
    data_path = args.data_dir or config['data_paths'].get('metadata', './data/metadata')
    processor = MetadataProcessor(data_path=data_path)

    # Initialize client
    client = JogetClient(
        base_url=config['base_url'],
        api_key=config.get('default_api_key'),
        debug=args.debug
    )

    # Process batch
    try:
        batch_results = processor.process_batch(batch_file)

        # Post each endpoint's data
        if not args.dry_run:
            for result in batch_results['results']:
                if result.get('success') and 'records' in result:
                    endpoint = result['endpoint']
                    api_id = result['api_id']
                    records = result['records']

                    if not args.yes and not utils.confirm_action(
                        f"Post {len(records)} records to {endpoint}?"):
                        print(f"Skipped {endpoint}")
                        continue

                    try:
                        post_results = client.batch_post(
                            endpoint=endpoint,
                            api_id=api_id,
                            records=records,
                            stop_on_error=args.stop_on_error
                        )
                        print(f"✓ {endpoint}: Posted {post_results['successful']} records")
                    except JogetAPIError as e:
                        print(f"✗ {endpoint}: API Error - {e}")

        utils.print_summary(batch_results, verbose=args.verbose)

    except Exception as e:
        print(f"Error processing batch: {e}")
        sys.exit(1)


def process_master_data_deploy(args, config):
    """Deploy master data forms and populate them with data"""
    # Load deployment configuration
    deploy_config_path = args.deploy_config or './config/master_data_deploy.yaml'

    try:
        deploy_config = utils.load_config(deploy_config_path)
    except FileNotFoundError:
        print(f"Error: Deployment configuration not found: {deploy_config_path}")
        print("Please create config/master_data_deploy.yaml or specify --deploy-config")
        sys.exit(1)

    # Override configuration with command-line arguments
    if args.forms_only:
        deploy_config['options']['populate_data'] = False
    elif args.data_only:
        deploy_config['options']['skip_existing_forms'] = True

    if args.dry_run:
        deploy_config['options']['dry_run'] = True

    if args.stop_on_error:
        deploy_config['options']['stop_on_error'] = True

    # Initialize client
    deployment_config = deploy_config.get('deployment', {})
    client = JogetClient(
        base_url=deployment_config.get('base_url', config.get('base_url')),
        api_key=deployment_config.get('form_creator_api_key'),
        debug=args.debug
    )

    # Test connection if requested
    if args.test:
        print("Testing connection to Joget server...")
        if client.test_connection():
            print("✓ Connection successful")
        else:
            print("✗ Connection failed")
            sys.exit(1)
        return

    # Initialize deployer
    logger = utils.setup_logging(deploy_config.get('logging', config.get('logging')))
    deployer = MasterDataDeployer(deploy_config, logger)

    # Confirm deployment
    target_app = deploy_config.get('target_application', {})
    app_id = target_app.get('app_id')
    app_version = target_app.get('app_version')

    print("\n" + "=" * 70)
    print("Master Data Deployment")
    print("=" * 70)
    print(f"Target Application: {app_id}")
    print(f"Target Version: {app_version}")
    print(f"Base URL: {deployment_config.get('base_url')}")

    options = deploy_config.get('options', {})
    if options.get('dry_run'):
        print("\n[DRY RUN MODE - No actual changes will be made]")

    if args.forms_only:
        print("\n[FORMS ONLY - Will not populate data]")
    elif args.data_only:
        print("\n[DATA ONLY - Will not create forms]")

    if not args.yes:
        if not utils.confirm_action("\nProceed with deployment?"):
            print("Deployment cancelled")
            return

    # Deploy
    try:
        summary = deployer.deploy_all(client)

        # Check for errors
        if summary.get('errors'):
            sys.exit(1)

    except Exception as e:
        print(f"\nDeployment failed: {e}")
        logger.error(f"Deployment error: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Joget Data Utility - Import data to Joget DX8 applications',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import single CSV file to endpoint
  %(prog)s --endpoint maritalStatus --input data.csv

  # Import JSON with dry run
  %(prog)s --endpoint customer --input customers.json --dry-run

  # Process metadata batch
  %(prog)s --metadata-batch config/metadata_batch.yaml

  # Deploy master data forms and populate
  %(prog)s --deploy-master-data

  # Deploy with custom config
  %(prog)s --deploy-master-data --deploy-config my_deploy.yaml

  # Deploy forms only (no data)
  %(prog)s --deploy-master-data --forms-only

  # Validate data without posting
  %(prog)s --endpoint account --input accounts.csv --validate

  # Use custom data directory
  %(prog)s --metadata-batch batch.yaml --data-dir /path/to/data
        """
    )

    # Main options
    parser.add_argument('--endpoint', '-e',
                       help='Endpoint name to import data to')

    parser.add_argument('--input', '-i',
                       help='Input file (CSV or JSON)')

    parser.add_argument('--metadata-batch', '-m',
                       help='Process metadata batch from YAML file')

    parser.add_argument('--deploy-master-data', '--deploy-md', action='store_true',
                       help='Deploy master data forms and populate with data')

    parser.add_argument('--deploy-config',
                       help='Path to deployment configuration file (default: config/master_data_deploy.yaml)')

    parser.add_argument('--forms-only', action='store_true',
                       help='Only create forms without populating data')

    parser.add_argument('--data-only', action='store_true',
                       help='Only populate data (assumes forms already exist)')

    # Processing options
    parser.add_argument('--dry-run', '-d', action='store_true',
                       help='Test run without posting data')

    parser.add_argument('--validate', '-v', action='store_true',
                       help='Validate data only')

    parser.add_argument('--yes', '-y', action='store_true',
                       help='Skip confirmation prompts')

    parser.add_argument('--stop-on-error', action='store_true',
                       help='Stop processing on first error')

    # Configuration options
    parser.add_argument('--config', '-c',
                       help='Path to configuration file (default: config/joget.yaml)')

    parser.add_argument('--api-key',
                       help='API key (overrides config)')

    parser.add_argument('--data-dir',
                       help='Data directory path')

    # Other options
    parser.add_argument('--test', action='store_true',
                       help='Test connection to Joget server')

    parser.add_argument('--verbose', action='store_true',
                       help='Verbose output')

    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode - logs all fields posted to endpoints')

    parser.add_argument('--list', '-l', action='store_true',
                       help='List available endpoints')

    args = parser.parse_args()

    # Load configuration
    try:
        config = utils.load_config(args.config)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Setup logging
    if args.verbose or args.debug:
        config['logging']['level'] = 'DEBUG'
    logger = utils.setup_logging(config.get('logging'))

    # Log debug mode status
    if args.debug:
        logger.debug("Debug mode enabled - all posted fields will be logged")

    # List endpoints
    if args.list:
        print("\nAvailable Endpoints:")
        print("\nMetadata Endpoints (standard code/name fields):")
        for name, details in config.get('metadata_endpoints', {}).items():
            desc = details.get('description', '')
            print(f"  {name:20} {desc}")

        print("\nCustom Endpoints:")
        for name, details in config.get('endpoints', {}).items():
            fields = ', '.join(details.get('required_fields', []))
            print(f"  {name:20} Required: {fields}")
        return

    # Process based on mode
    if args.deploy_master_data:
        process_master_data_deploy(args, config)
    elif args.metadata_batch:
        process_metadata_batch(args, config)
    elif args.endpoint and args.input:
        process_single_endpoint(args, config)
    elif args.test:
        args.endpoint = None  # Allow test without endpoint
        process_single_endpoint(args, config)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()