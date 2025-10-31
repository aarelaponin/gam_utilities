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
from processors.form_generator import MetadataFormGenerator
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


def process_create_form(args, config):
    """Create a single form from a form definition file"""
    import json

    form_file = Path(args.create_form)
    if not form_file.exists():
        print(f"Error: Form definition file not found: {form_file}")
        sys.exit(1)

    # Load form definition
    try:
        with open(form_file, 'r') as f:
            data = json.load(f)

        # Handle different file formats
        # Format 1: Direct form definition (from form generator)
        if 'className' in data and data.get('className') == 'org.joget.apps.form.model.Form':
            form_definition = data
        # Format 2: Wrapped in CRUD export format (from Joget export)
        elif 'message' in data:
            message_str = data.get('message', '{}')
            components = json.loads(message_str).get('components', {})
            form_data = components.get('form', {})
            form_definition = form_data.get('definition', {})
        # Format 3: Already extracted form
        elif 'definition' in data:
            form_definition = data['definition']
        else:
            print("Error: Unrecognized form definition format")
            sys.exit(1)

        # Extract form properties
        form_props = form_definition.get('properties', {})
        form_id = args.form_id or form_props.get('id')
        form_name = args.form_name or form_props.get('name', form_id)
        table_name = args.table_name or form_props.get('tableName', form_id.lower())

        if not form_id:
            print("Error: Could not determine form ID. Use --form-id to specify.")
            sys.exit(1)

        print(f"Preparing to create form: {form_id}")
        print(f"  Name: {form_name}")
        print(f"  Table: {table_name}")
        print(f"  Target app: {args.app_id}")

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in form definition file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading form definition: {e}")
        sys.exit(1)

    # Load deployment config to get API credentials
    deploy_config_path = args.deploy_config or './config/master_data_deploy.yaml'
    try:
        deploy_config = utils.load_config(deploy_config_path)
    except FileNotFoundError:
        print(f"Error: Deployment configuration not found: {deploy_config_path}")
        print("Need FormCreator API credentials. Create config/master_data_deploy.yaml")
        sys.exit(1)

    deployment_config = deploy_config.get('deployment', {})

    # Allow base_url override via --port
    if args.port:
        base_url = f"http://localhost:{args.port}/jw/api"
    else:
        base_url = deployment_config.get('base_url')

    # Initialize client
    client = JogetClient(
        base_url=base_url,
        api_key=deployment_config.get('form_creator_api_key'),
        debug=args.debug
    )

    # Prepare payload for FormCreator
    payload = {
        'target_app_id': args.app_id,
        'target_app_version': args.app_version or '1',
        'form_id': form_id,
        'form_name': form_name,
        'table_name': table_name,
        'form_definition_json': json.dumps(form_definition),
        'create_api_endpoint': 'yes' if args.create_api else 'no',
        'api_name': f'api_{form_id}',
        'create_crud': 'yes' if args.create_crud else 'no'
    }

    if args.dry_run:
        print("\n[DRY RUN MODE - No actual changes will be made]")
        print(f"\nWould create form with payload:")
        print(f"  Target app: {payload['target_app_id']}")
        print(f"  Form ID: {payload['form_id']}")
        print(f"  Table: {payload['table_name']}")
        print(f"  Create API: {payload['create_api_endpoint']}")
        print(f"  Create CRUD: {payload['create_crud']}")
        return

    # Confirm
    if not args.yes:
        if not utils.confirm_action(f"\nCreate form '{form_id}' in app '{args.app_id}' on {base_url}?"):
            print("Operation cancelled")
            return

    # Create form
    print("\nSending form to FormCreator...")
    try:
        response = client.create_form(
            payload=payload,
            api_id=deployment_config.get('form_creator_api_id')
        )

        print("\n✓ Form created successfully!")
        print(f"Response ID: {response.get('id', 'N/A')}")

        if response.get('errors'):
            print(f"Warnings/Errors: {response['errors']}")

    except JogetAPIError as e:
        print(f"\n✗ Error creating form: {e}")
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


def process_form_generation(args, config):
    """Generate Joget form JSON definitions from CSV files"""

    # Initialize generator
    generator = MetadataFormGenerator(logger=utils.setup_logging(config.get('logging')))

    # Paths configuration
    metadata_dir = Path(args.metadata_dir or './data/metadata')
    forms_dir = Path(args.forms_dir or './data/metadata_forms')

    if not metadata_dir.exists():
        print(f"Error: Metadata directory not found: {metadata_dir}")
        sys.exit(1)

    # Generate specific form or all forms
    if args.csv_file:
        # Generate single form
        csv_path = Path(args.csv_file)
        if not csv_path.exists():
            print(f"Error: CSV file not found: {csv_path}")
            sys.exit(1)

        # Determine output path
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = forms_dir / csv_path.with_suffix('.json').name

        print(f"\nGenerating form from: {csv_path}")
        print(f"Output: {output_path}")

        try:
            form_json = generator.generate_from_csv(csv_path)

            if args.dry_run:
                print("\n[DRY RUN] Would generate form:")
                print(f"  Form ID: {form_json['properties']['id']}")
                print(f"  Form Name: {form_json['properties']['name']}")
                print(f"  Table Name: {form_json['properties']['tableName']}")
            else:
                generator.save_form_json(form_json, output_path)
                print(f"✓ Form JSON generated successfully")
        except Exception as e:
            print(f"✗ Error generating form: {e}")
            sys.exit(1)

    else:
        # Generate all forms from metadata directory
        csv_files = sorted(metadata_dir.glob('*.csv'))

        if not csv_files:
            print(f"No CSV files found in: {metadata_dir}")
            return

        print(f"\nFound {len(csv_files)} CSV files")
        print(f"Output directory: {forms_dir}")

        # Check which forms already exist
        existing_forms = {f.stem for f in forms_dir.glob('*.json')}

        forms_to_generate = []
        for csv_file in csv_files:
            form_stem = csv_file.stem
            if form_stem in existing_forms and not args.overwrite:
                if args.verbose:
                    print(f"  ⊘ Skipping {form_stem} (already exists)")
            else:
                forms_to_generate.append(csv_file)

        if not forms_to_generate:
            print("\n✓ All forms already exist (use --overwrite to regenerate)")
            return

        print(f"\nGenerating {len(forms_to_generate)} forms...")

        if not args.yes and not utils.confirm_action(f"\nGenerate {len(forms_to_generate)} form definitions?"):
            print("Operation cancelled")
            return

        # Generate forms
        generated = 0
        failed = 0

        for idx, csv_file in enumerate(forms_to_generate, 1):
            form_name = csv_file.stem
            output_path = forms_dir / csv_file.with_suffix('.json').name

            print(f"\n[{idx}/{len(forms_to_generate)}] {form_name}")

            try:
                form_json = generator.generate_from_csv(csv_file)

                if args.dry_run:
                    print(f"  [DRY RUN] Would generate: {form_json['properties']['id']}")
                else:
                    generator.save_form_json(form_json, output_path)
                    print(f"  ✓ Generated")

                generated += 1

            except Exception as e:
                print(f"  ✗ Failed: {e}")
                failed += 1

                if args.stop_on_error:
                    print("\nStopping due to error")
                    break

        # Summary
        print("\n" + "=" * 60)
        print("Form Generation Summary")
        print("=" * 60)
        print(f"Generated: {generated}")
        print(f"Failed: {failed}")
        print(f"Output directory: {forms_dir}")


def process_metadata_discovery(args, config):
    """
    Discover CSV files, detect relationships, and generate form definitions.

    This is Phase 1 of the metadata management workflow:
    1. Scan data/metadata/ for CSV files
    2. Detect Pattern 1 and Pattern 2 relationships
    3. Generate form JSON definitions with FK injection
    4. Save relationships.json
    """
    from processors.relationship_detector import RelationshipDetector
    from processors.form_generator import MetadataFormGenerator

    # Setup paths
    metadata_dir = Path(args.metadata_dir or config.get('metadata', {}).get('csv_path', './data/metadata'))
    forms_dir = Path(args.forms_dir or config.get('metadata', {}).get('forms_path', './data/metadata_forms'))
    relationships_file = Path(config.get('metadata', {}).get('relationships_file', './data/relationships.json'))

    if not metadata_dir.exists():
        print(f"Error: Metadata directory not found: {metadata_dir}")
        sys.exit(1)

    print("\n" + "=" * 80)
    print("PHASE 1: METADATA DISCOVERY & FORM GENERATION")
    print("=" * 80)
    print()

    # Initialize components
    logger = utils.setup_logging(config.get('logging'))
    detector = RelationshipDetector(config=config, logger=logger)
    generator = MetadataFormGenerator(config=config, logger=logger)

    # Step 1: Detect relationships
    print("Step 1: Detecting relationships...")
    print("-" * 80)
    relationships, hierarchies = detector.detect_all_relationships(metadata_dir)

    print(f"\n✓ Detected {len(relationships)} relationships:")
    pattern1_count = len([r for r in relationships if r.pattern_type == 'traditional_fk'])
    pattern2_count = len([r for r in relationships if r.pattern_type == 'subcategory_source'])
    print(f"  • Pattern 1 (Traditional FK): {pattern1_count}")
    print(f"  • Pattern 2 (Subcategory Source): {pattern2_count}")
    print(f"\n✓ Built {len(hierarchies)} hierarchies")
    print()

    # Step 2: Save relationships metadata
    print("Step 2: Saving relationships metadata...")
    print("-" * 80)
    detector.save_relationships_metadata(relationships, hierarchies, relationships_file)
    print(f"✓ Saved to: {relationships_file}")
    print()

    # Step 3: Generate forms
    print("Step 3: Generating form definitions...")
    print("-" * 80)

    csv_files = sorted(metadata_dir.glob('*.csv'))
    print(f"Found {len(csv_files)} CSV files")

    # Check which forms already exist
    existing_forms = {f.stem for f in forms_dir.glob('*.json')}
    forms_to_generate = []

    for csv_file in csv_files:
        form_stem = csv_file.stem
        if form_stem in existing_forms and not args.overwrite:
            if args.verbose:
                print(f"  ⊘ Skipping {form_stem} (already exists)")
        else:
            forms_to_generate.append(csv_file)

    if not forms_to_generate:
        print("\n✓ All forms already exist (use --overwrite to regenerate)")
        print()
        return

    print(f"\nGenerating {len(forms_to_generate)} forms...")

    if not args.yes and not args.dry_run:
        if not utils.confirm_action(f"\nGenerate {len(forms_to_generate)} form definitions?"):
            print("Operation cancelled")
            return

    # Generate forms
    generated = 0
    failed = 0
    pattern2_forms = []

    for idx, csv_file in enumerate(forms_to_generate, 1):
        form_name = csv_file.stem
        output_path = forms_dir / csv_file.with_suffix('.json').name

        print(f"\n[{idx}/{len(forms_to_generate)}] {form_name}")

        try:
            form_json = generator.generate_from_csv(csv_file)

            # Check if Pattern 2
            form_props = form_json.get('properties', {})
            is_pattern2 = 'Pattern 2' in form_props.get('description', '')

            if is_pattern2:
                pattern2_forms.append(form_name)

            if args.dry_run:
                print(f"  [DRY RUN] Would generate: {form_json['properties']['id']}")
                if is_pattern2:
                    print(f"  ⭐ Pattern 2: FK field injected")
            else:
                generator.save_form_json(form_json, output_path)
                print(f"  ✓ Generated")
                if is_pattern2:
                    print(f"  ⭐ Pattern 2: FK field injected")

            generated += 1

        except Exception as e:
            print(f"  ✗ Failed: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            failed += 1

            if args.stop_on_error:
                print("\nStopping due to error")
                break

    # Summary
    print("\n" + "=" * 80)
    print("DISCOVERY & GENERATION SUMMARY")
    print("=" * 80)
    print(f"CSV Files Scanned:        {len(csv_files)}")
    print(f"Forms Generated:          {generated}")
    print(f"Forms Failed:             {failed}")
    print(f"Pattern 2 Forms:          {len(pattern2_forms)}")
    print(f"Relationships Detected:   {len(relationships)}")
    print(f"Hierarchies Built:        {len(hierarchies)}")
    print()
    print(f"Output Locations:")
    print(f"  • Forms:         {forms_dir}")
    print(f"  • Relationships: {relationships_file}")
    print()

    if pattern2_forms:
        print("Pattern 2 Forms (FK injected):")
        for form_name in pattern2_forms:
            print(f"  • {form_name}")
        print()

    if not args.dry_run:
        print("✅ Phase 1 Complete!")
        print()
        print("Next Steps:")
        print("  1. Review generated forms in data/metadata_forms/")
        print("  2. Review relationships in data/relationships.json")
        print("  3. Run: python joget_utility.py --metadata compare")
        print("     (to compare with deployed forms in Joget)")
    else:
        print("[DRY RUN] No files were written")


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

  # Create single form (ad-hoc testing)
  %(prog)s --create-form doc_forms/subsidyApproval.json --app-id subsidyApplication --port 8888

  # Create form with overrides (dry run first)
  %(prog)s --create-form test.json --app-id myApp --port 8080 --form-id custom_id --dry-run

  # Create form without API/CRUD
  %(prog)s --create-form test.json --app-id myApp --no-create-api --no-create-crud

  # Generate form JSONs from all CSV files
  %(prog)s --generate-forms-from-csv

  # Generate single form from specific CSV
  %(prog)s --generate-form data/metadata/md99status.csv

  # Generate with custom output path
  %(prog)s --generate-form data/metadata/md99status.csv --output forms/md99status.json

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

    parser.add_argument('--metadata', choices=['discover', 'compare', 'deploy', 'all'],
                       help='Metadata management commands: discover (generate forms + relationships), '
                            'compare (diff local vs Joget), deploy (full deployment), all (run all phases)')

    parser.add_argument('--deploy-master-data', '--deploy-md', action='store_true',
                       help='Deploy master data forms and populate with data')

    parser.add_argument('--deploy-config',
                       help='Path to deployment configuration file (default: config/master_data_deploy.yaml)')

    parser.add_argument('--forms-only', action='store_true',
                       help='Only create forms without populating data')

    parser.add_argument('--data-only', action='store_true',
                       help='Only populate data (assumes forms already exist)')

    # Single form creation options
    parser.add_argument('--create-form',
                       help='Create a single form from JSON definition file')

    parser.add_argument('--app-id',
                       help='Target application ID (required with --create-form)')

    parser.add_argument('--app-version',
                       help='Target application version (default: 1)')

    parser.add_argument('--port',
                       type=int,
                       help='Joget server port (e.g., 8888, 8080)')

    parser.add_argument('--form-id',
                       help='Override form ID from definition file')

    parser.add_argument('--form-name',
                       help='Override form name from definition file')

    parser.add_argument('--table-name',
                       help='Override table name from definition file')

    parser.add_argument('--create-api', action='store_true', default=True,
                       help='Create API endpoint for the form (default: True)')

    parser.add_argument('--no-create-api', dest='create_api', action='store_false',
                       help='Do not create API endpoint')

    parser.add_argument('--create-crud', action='store_true', default=True,
                       help='Create CRUD interface for the form (default: True)')

    parser.add_argument('--no-create-crud', dest='create_crud', action='store_false',
                       help='Do not create CRUD interface')

    # Form generation options
    parser.add_argument('--generate-forms-from-csv', '--gen-forms', action='store_true',
                       help='Generate form JSONs from all CSV files in metadata directory')

    parser.add_argument('--generate-form', '--gen', dest='csv_file',
                       help='Generate form JSON from specific CSV file')

    parser.add_argument('--output', '-o',
                       help='Output path for generated form JSON (used with --generate-form)')

    parser.add_argument('--metadata-dir',
                       help='Metadata directory containing CSV files (default: ./data/metadata)')

    parser.add_argument('--forms-dir',
                       help='Forms directory for output JSONs (default: ./data/metadata_forms)')

    parser.add_argument('--overwrite', action='store_true',
                       help='Overwrite existing form JSON files')

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
    if args.metadata:
        # New metadata management workflow
        if args.metadata == 'discover':
            process_metadata_discovery(args, config)
        elif args.metadata == 'compare':
            # TODO: Implement comparison
            print("Metadata comparison not yet implemented")
            print("Coming soon: Compare local forms with Joget instance")
        elif args.metadata == 'deploy':
            # TODO: Use enhanced deployment
            print("Enhanced metadata deployment not yet implemented")
            print("Use --deploy-master-data for now")
        elif args.metadata == 'all':
            # Run all phases
            print("Running all metadata phases...")
            process_metadata_discovery(args, config)
            # TODO: Add compare and deploy
    elif args.create_form:
        # Validate required arguments
        if not args.app_id:
            print("Error: --app-id is required when using --create-form")
            sys.exit(1)
        process_create_form(args, config)
    elif args.generate_forms_from_csv or args.csv_file:
        process_form_generation(args, config)
    elif args.deploy_master_data:
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