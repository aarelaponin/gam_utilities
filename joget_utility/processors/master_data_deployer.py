#!/usr/bin/env python3
"""
Master Data Deployer
Handles deployment of master data forms and population with data
"""

import json
import logging
import time
import os
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import glob
from dotenv import load_dotenv

from .csv_processor import CSVProcessor
from .data_augmentor import DataAugmentor
from .relationship_detector import RelationshipInfo


class MasterDataDeployer:
    """Deployer for master data forms creation and population"""

    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        Initialize master data deployer

        Args:
            config: Deployment configuration dictionary
            logger: Optional logger instance
        """
        self.config = config
        self.logger = logger or logging.getLogger('joget_utility.master_data_deployer')

        # Extract configuration sections
        self.deployment_config = config.get('deployment', {})
        self.target_app = config.get('target_application', {})
        self.form_options = config.get('form_options', {})
        self.paths = config.get('paths', {})
        self.options = config.get('options', {})

        # Initialize data augmentor for Pattern 2 support
        self.augmentor = DataAugmentor(logger=self.logger)

        # Load relationships metadata if available
        self.relationships = {}
        self.relationships_by_child = {}
        self._load_relationships()

        # State tracking
        self.created_forms = []
        self.errors = []

    def _load_relationships(self):
        """Load relationships.json if available"""
        relationships_file = Path(self.config.get('metadata', {}).get('relationships_file', './data/relationships.json'))

        if relationships_file.exists():
            try:
                with open(relationships_file, 'r') as f:
                    data = json.load(f)

                # Build lookup by child form
                for rel_dict in data.get('relationships', []):
                    # Handle optional fields for backward compatibility
                    if 'parent_code_value' not in rel_dict:
                        rel_dict['parent_code_value'] = None
                    if 'fk_value_to_inject' not in rel_dict:
                        rel_dict['fk_value_to_inject'] = None

                    rel = RelationshipInfo(**rel_dict)
                    self.relationships_by_child[rel.child_form] = rel

                self.logger.info(f"Loaded {len(self.relationships_by_child)} relationships from {relationships_file}")

            except Exception as e:
                self.logger.warning(f"Could not load relationships: {e}")
        else:
            self.logger.debug(f"Relationships file not found: {relationships_file}")

    def discover_forms(self) -> List[Path]:
        """
        Discover form definition files

        Returns:
            List of form definition file paths
        """
        forms_dir = Path(self.paths.get('forms_dir', './data/metadata_forms'))
        form_pattern = self.paths.get('form_pattern', 'md*.json')

        if not forms_dir.exists():
            raise FileNotFoundError(f"Forms directory not found: {forms_dir}")

        # Get all matching form files
        pattern_path = forms_dir / form_pattern
        form_files = sorted(glob.glob(str(pattern_path)))

        if not form_files:
            raise ValueError(f"No form files found matching pattern: {pattern_path}")

        self.logger.info(f"Discovered {len(form_files)} form definition files")
        return [Path(f) for f in form_files]

    def extract_form_metadata(self, form_file: Path) -> Dict[str, Any]:
        """
        Extract metadata from form definition JSON

        Args:
            form_file: Path to form definition file

        Returns:
            Dictionary with form metadata (form_id, form_name, table_name, definition)
        """
        try:
            with open(form_file, 'r', encoding='utf-8') as f:
                form_definition = json.load(f)

            # Extract properties from form definition
            properties = form_definition.get('properties', {})

            form_id = properties.get('id', '')
            form_name = properties.get('name', '')
            table_name = properties.get('tableName', form_id)

            if not form_id:
                raise ValueError(f"Form ID not found in {form_file}")

            return {
                'file': form_file,
                'form_id': form_id,
                'form_name': form_name,
                'table_name': table_name,
                'definition': form_definition,
                'definition_json': json.dumps(form_definition)
            }

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {form_file}: {e}")
        except Exception as e:
            raise ValueError(f"Error reading {form_file}: {e}")

    def get_data_file(self, form_file: Path) -> Optional[Path]:
        """
        Find corresponding data file for a form

        Args:
            form_file: Path to form definition file

        Returns:
            Path to data file or None if not found
        """
        data_dir = Path(self.paths.get('data_dir', './data/metadata'))

        # Extract the base name pattern (e.g., md01maritalStatus from md01maritalStatus.json)
        base_name = form_file.stem

        # Look for corresponding CSV file
        data_file = data_dir / f"{base_name}.csv"

        if data_file.exists():
            return data_file

        # Try alternate patterns
        alternate_patterns = [
            f"{base_name}.json",
            f"{base_name}.CSV",  # Case variation
        ]

        for pattern in alternate_patterns:
            alt_file = data_dir / pattern
            if alt_file.exists():
                return alt_file

        self.logger.warning(f"No data file found for form {form_file.name}")
        return None

    def generate_api_name(self, form_id: str) -> str:
        """
        Generate API name from form ID

        Args:
            form_id: Form identifier

        Returns:
            Generated API name
        """
        prefix = self.form_options.get('api_name_prefix', 'api_')
        return f"{prefix}{form_id}"

    def prepare_form_creation_payload(self, form_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare payload for form creation API call

        Args:
            form_metadata: Form metadata dictionary

        Returns:
            Payload dictionary for formCreator API
        """
        api_name = self.generate_api_name(form_metadata['form_id'])

        payload = {
            'target_app_id': self.target_app.get('app_id'),
            'target_app_version': str(self.target_app.get('app_version', '1')),
            'form_id': form_metadata['form_id'],
            'form_name': form_metadata['form_name'],
            'table_name': form_metadata['table_name'],
            'form_definition_json': form_metadata['definition_json'],
            'create_api_endpoint': self.form_options.get('create_api_endpoint', 'yes'),
            'api_name': api_name,
            'create_crud': self.form_options.get('create_crud', 'yes')
        }

        return payload

    def validate_form(self, form_metadata: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate form definition

        Args:
            form_metadata: Form metadata dictionary

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required fields
        required_fields = ['form_id', 'form_name', 'table_name', 'definition']

        for field in required_fields:
            if not form_metadata.get(field):
                return False, f"Missing required field: {field}"

        # Validate JSON structure
        definition = form_metadata.get('definition', {})
        if not isinstance(definition, dict):
            return False, "Form definition must be a dictionary"

        if 'className' not in definition:
            return False, "Form definition missing className"

        if 'properties' not in definition:
            return False, "Form definition missing properties"

        return True, None

    def validate_data_file(self, data_file: Path) -> Tuple[bool, Optional[str], int]:
        """
        Validate data file

        Args:
            data_file: Path to data file

        Returns:
            Tuple of (is_valid, error_message, record_count)
        """
        try:
            processor = CSVProcessor()
            records = processor.read_file(data_file)

            if not records:
                return False, "Data file is empty", 0

            # Check for required fields (code, name)
            first_record = records[0]
            if 'code' not in first_record or 'name' not in first_record:
                # Check if we can infer fields
                if len(first_record.keys()) < 2:
                    return False, "Data file must have at least 2 columns (code, name)", 0

            return True, None, len(records)

        except Exception as e:
            return False, str(e), 0

    def create_form(self, client, form_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a single form using the client

        Args:
            client: JogetClient instance
            form_metadata: Form metadata dictionary

        Returns:
            Result dictionary with form creation details
        """
        result = {
            'form_id': form_metadata['form_id'],
            'form_name': form_metadata['form_name'],
            'file': str(form_metadata['file']),
            'success': False,
            'error': None
        }

        try:
            # Validate form if enabled
            if self.options.get('validate_forms', True):
                is_valid, error_msg = self.validate_form(form_metadata)
                if not is_valid:
                    result['error'] = f"Validation failed: {error_msg}"
                    return result

            # Prepare payload
            payload = self.prepare_form_creation_payload(form_metadata)

            # Dry run mode
            if self.options.get('dry_run', False):
                self.logger.info(f"[DRY RUN] Would create form: {form_metadata['form_id']}")
                result['success'] = True
                result['dry_run'] = True
                return result

            # Create form via API
            response = client.create_form(
                payload=payload,
                api_id=self.deployment_config.get('form_creator_api_id'),
                api_key=self.deployment_config.get('form_creator_api_key')
            )

            result['success'] = True
            result['response'] = response
            result['api_endpoint'] = f"form/{form_metadata['form_id']}/saveOrUpdate"

            self.logger.info(f"✓ Created form: {form_metadata['form_id']}")

        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"✗ Failed to create form {form_metadata['form_id']}: {e}")

        return result

    def populate_form_data(self, client, form_metadata: Dict[str, Any],
                          data_file: Path) -> Dict[str, Any]:
        """
        Populate form with data from CSV file

        Args:
            client: JogetClient instance
            form_metadata: Form metadata dictionary
            data_file: Path to data file

        Returns:
            Result dictionary with population details
        """
        result = {
            'form_id': form_metadata['form_id'],
            'data_file': str(data_file),
            'success': False,
            'records_posted': 0,
            'error': None,
            'pattern2_augmented': False
        }

        try:
            # Validate data file if enabled
            if self.options.get('validate_data', True):
                is_valid, error_msg, record_count = self.validate_data_file(data_file)
                if not is_valid:
                    result['error'] = f"Data validation failed: {error_msg}"
                    return result
                result['total_records'] = record_count

            # Check if this is a Pattern 2 form requiring data augmentation
            form_id = form_metadata['form_id']
            relationship = self.relationships_by_child.get(form_id)

            # Load data
            processor = CSVProcessor()
            records = processor.read_file(data_file)

            # PATTERN 2: Augment data with FK values if needed
            if relationship and relationship.needs_fk_injection:
                self.logger.info(f"  ⭐ Pattern 2 form detected: {form_id}")
                self.logger.info(f"     Injecting FK: {relationship.child_foreign_key} = '{relationship.fk_value_to_inject}'")

                # Validate parent exists
                if relationship.parent_csv:
                    parent_csv_path = data_file.parent / relationship.parent_csv
                    if parent_csv_path.exists():
                        if not self.augmentor.validate_parent_existence(
                            parent_csv_path,
                            relationship.fk_value_to_inject,
                            relationship.parent_primary_key
                        ):
                            result['error'] = f"Parent code '{relationship.fk_value_to_inject}' not found in {relationship.parent_csv}"
                            return result

                # Augment data
                df, augment_result = self.augmentor.augment_csv_data(data_file, relationship)

                if not augment_result.success:
                    result['error'] = f"Data augmentation failed: {augment_result.error}"
                    return result

                # Convert augmented DataFrame back to records
                records = self.augmentor.convert_dataframe_to_records(df)
                result['pattern2_augmented'] = True
                result['injected_fk'] = relationship.child_foreign_key
                result['injected_value'] = relationship.fk_value_to_inject

            # Transform to proper format (handles all fields, not just code/name)
            transformed_records = self._transform_to_full_format(records)

            if not transformed_records:
                result['error'] = "No valid records to post"
                return result

            # Dry run mode
            if self.options.get('dry_run', False):
                self.logger.info(
                    f"[DRY RUN] Would post {len(transformed_records)} records to {form_metadata['form_id']}"
                )
                result['success'] = True
                result['records_posted'] = len(transformed_records)
                result['dry_run'] = True
                return result

            # Post data to form endpoint
            endpoint = f"form/{form_metadata['form_id']}/saveOrUpdate"

            # Get form-specific API ID (queried from database in Phase 1.5)
            form_api_id = form_metadata.get('api_id')
            if not form_api_id:
                result['error'] = "No API ID found for form - cannot post data"
                self.logger.error(f"  ✗ No API ID available for {form_metadata['form_id']}")
                return result

            # Use batch posting with form-specific API ID
            post_results = client.batch_post(
                endpoint=endpoint,
                api_id=form_api_id,
                records=transformed_records,
                api_key=self.deployment_config.get('form_creator_api_key'),
                stop_on_error=self.options.get('stop_on_error', False)
            )

            result['success'] = post_results['successful'] > 0
            result['records_posted'] = post_results['successful']
            result['records_failed'] = post_results['failed']
            result['errors'] = post_results.get('errors', [])

            if result['success']:
                msg = f"✓ Posted {result['records_posted']} records to {form_metadata['form_id']}"
                if result.get('pattern2_augmented'):
                    msg += f" (Pattern 2: FK '{result['injected_fk']}' injected)"
                self.logger.info(msg)
            else:
                self.logger.error(
                    f"✗ Failed to post data to {form_metadata['form_id']}"
                )

        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"✗ Error populating {form_metadata['form_id']}: {e}")

        return result

    def _transform_to_full_format(self, records: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Transform records to full format (all fields preserved).

        For Pattern 2 forms, this includes the injected FK fields.
        For simple forms, converts all fields to strings.

        Args:
            records: Input records

        Returns:
            Transformed records with all fields as strings
        """
        transformed = []

        for record in records:
            # Convert all values to strings and filter out None
            transformed_record = {}
            for key, value in record.items():
                if value is not None:
                    # Handle pandas NA values
                    if pd.isna(value):
                        continue
                    transformed_record[key] = str(value)

            if transformed_record:
                transformed.append(transformed_record)

        return transformed

    def _transform_to_metadata_format(self, records: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Transform records to standard code/name format (legacy method).

        DEPRECATED: Use _transform_to_full_format for Pattern 2 support.

        Args:
            records: Input records

        Returns:
            Transformed records with code and name fields only
        """
        transformed = []

        for record in records:
            code_value = None
            name_value = None

            # Check for exact matches first
            if 'code' in record and 'name' in record:
                code_value = str(record['code'])
                name_value = str(record['name'])
            else:
                # Try to infer from first two fields
                fields = list(record.keys())
                if len(fields) >= 2:
                    # Skip 'id' field if present, use next fields
                    field_idx = 1 if fields[0].lower() == 'id' else 0
                    if field_idx < len(fields):
                        code_value = str(record[fields[field_idx]])
                    if field_idx + 1 < len(fields):
                        name_value = str(record[fields[field_idx + 1]])

            if code_value and name_value:
                transformed.append({
                    "code": code_value,
                    "name": name_value
                })

        return transformed

    def deploy_all(self, client) -> Dict[str, Any]:
        """
        Deploy all master data forms and populate with data

        Args:
            client: JogetClient instance

        Returns:
            Deployment summary dictionary
        """
        self.logger.info("=" * 70)
        self.logger.info("Starting Master Data Deployment")
        self.logger.info("=" * 70)

        summary = {
            'total_forms': 0,
            'forms_created': 0,
            'forms_failed': 0,
            'total_records': 0,
            'records_posted': 0,
            'records_failed': 0,
            'results': [],
            'errors': []
        }

        try:
            # Discover forms
            form_files = self.discover_forms()
            summary['total_forms'] = len(form_files)

            self.logger.info(f"\nTarget Application: {self.target_app.get('app_id')}")
            self.logger.info(f"Target Version: {self.target_app.get('app_version')}")
            self.logger.info(f"Forms to deploy: {len(form_files)}\n")

            # Phase 1: Create Forms
            self.logger.info("-" * 70)
            self.logger.info("PHASE 1: Creating Forms")
            self.logger.info("-" * 70)

            form_metadata_list = []

            for idx, form_file in enumerate(form_files, 1):
                self.logger.info(f"\n[{idx}/{len(form_files)}] Processing: {form_file.name}")

                try:
                    # Extract metadata
                    form_metadata = self.extract_form_metadata(form_file)
                    form_metadata_list.append(form_metadata)

                    # Create form
                    create_result = self.create_form(client, form_metadata)

                    if create_result['success']:
                        summary['forms_created'] += 1
                    else:
                        summary['forms_failed'] += 1
                        summary['errors'].append({
                            'phase': 'form_creation',
                            'form': form_metadata['form_id'],
                            'error': create_result['error']
                        })

                        if self.options.get('stop_on_error', False):
                            self.logger.error("\nStopping deployment due to error (stop_on_error=true)")
                            summary['stopped_early'] = True
                            return summary

                    # Add delay between API calls
                    delay = self.options.get('api_call_delay', 0.5)
                    if delay > 0:
                        time.sleep(delay)

                except Exception as e:
                    self.logger.error(f"✗ Error processing {form_file.name}: {e}")
                    summary['forms_failed'] += 1
                    summary['errors'].append({
                        'phase': 'form_processing',
                        'file': str(form_file),
                        'error': str(e)
                    })

                    if self.options.get('stop_on_error', False):
                        return summary

            # Phase 1.5: Query API IDs for created forms
            if self.options.get('populate_data', True) and summary['forms_created'] > 0:
                self.logger.info("\n" + "-" * 70)
                self.logger.info("PHASE 1.5: Querying API IDs from Database")
                self.logger.info("-" * 70)

                # Load database configuration from .env file
                db_config_section = self.config.get('database', {})
                env_file = db_config_section.get('env_file', '.env.3')

                # Load environment variables from .env file
                env_file_path = Path(env_file)
                if not env_file_path.is_absolute():
                    # Resolve relative to project root (where .env.3 is located)
                    # __file__ is in processors/, go up: processors/ -> joget_utility/ -> gam/
                    project_root = Path(__file__).parent.parent.parent
                    env_file_path = project_root / env_file

                if not env_file_path.exists():
                    self.logger.error(f"Environment file not found: {env_file_path}")
                    self.logger.error("Cannot query API IDs without database credentials")
                    summary['errors'].append({
                        'phase': 'api_id_query',
                        'error': f'Environment file not found: {env_file_path}'
                    })
                else:
                    # Load environment variables from the file
                    # Use override=True to override any existing .env file that may have been loaded
                    load_dotenv(env_file_path, override=True)

                    # Build db_config from environment variables
                    db_config = {
                        'host': os.getenv('DB_HOST', 'localhost'),
                        'port': int(os.getenv('DB_PORT', '3306')),
                        'database': os.getenv('DB_NAME', 'jwdb'),
                        'user': os.getenv('DB_USER'),
                        'password': os.getenv('DB_PASSWORD')
                    }

                    # Validate required credentials are present
                    if not db_config.get('user') or db_config.get('password') is None:
                        self.logger.error("Database credentials missing in .env file")
                        self.logger.error(f"Required: DB_USER and DB_PASSWORD in {env_file_path}")
                        summary['errors'].append({
                            'phase': 'api_id_query',
                            'error': 'Database credentials missing in .env file'
                        })
                    else:
                        self.logger.info(f"Loaded database config from: {env_file_path}")
                        self.logger.info(f"Database: {db_config['database']} at {db_config['host']}:{db_config['port']}")

                        for idx, form_metadata in enumerate(form_metadata_list, 1):
                            form_id = form_metadata['form_id']
                            api_name = self.generate_api_name(form_id)

                            self.logger.info(f"\n[{idx}/{len(form_metadata_list)}] Querying API ID for: {form_id} (API name: {api_name})")

                            try:
                                api_id = client.get_api_id_for_form(
                                    app_id=self.target_app.get('app_id'),
                                    app_version=str(self.target_app.get('app_version', '1')),
                                    api_name=api_name,
                                    db_config=db_config
                                )

                                if api_id:
                                    form_metadata['api_id'] = api_id
                                    self.logger.info(f"  ✓ Found API ID: {api_id}")
                                else:
                                    self.logger.warning(f"  ⚠ No API ID found for {form_id} - data population will fail")
                                    form_metadata['api_id'] = None

                            except Exception as e:
                                self.logger.error(f"  ✗ Error querying API ID for {form_id}: {e}")
                                form_metadata['api_id'] = None
                                summary['errors'].append({
                                    'phase': 'api_id_query',
                                    'form': form_id,
                                    'error': str(e)
                                })

            # Phase 2: Populate Data
            if self.options.get('populate_data', True) and summary['forms_created'] > 0:
                self.logger.info("\n" + "-" * 70)
                self.logger.info("PHASE 2: Populating Data")
                self.logger.info("-" * 70)

                for idx, form_metadata in enumerate(form_metadata_list, 1):
                    self.logger.info(f"\n[{idx}/{len(form_metadata_list)}] Populating: {form_metadata['form_id']}")

                    # Find data file
                    data_file = self.get_data_file(form_metadata['file'])

                    if not data_file:
                        self.logger.warning(f"  ⚠ No data file found, skipping data population")
                        continue

                    # Populate data
                    populate_result = self.populate_form_data(client, form_metadata, data_file)

                    if populate_result['success']:
                        summary['records_posted'] += populate_result.get('records_posted', 0)
                        summary['records_failed'] += populate_result.get('records_failed', 0)
                    else:
                        summary['errors'].append({
                            'phase': 'data_population',
                            'form': form_metadata['form_id'],
                            'error': populate_result['error']
                        })

                    summary['results'].append(populate_result)

                    # Add delay
                    delay = self.options.get('api_call_delay', 0.5)
                    if delay > 0:
                        time.sleep(delay)

        except Exception as e:
            self.logger.error(f"Deployment error: {e}")
            summary['errors'].append({
                'phase': 'deployment',
                'error': str(e)
            })

        # Print summary
        self.logger.info("\n" + "=" * 70)
        self.logger.info("DEPLOYMENT SUMMARY")
        self.logger.info("=" * 70)
        self.logger.info(f"Total forms processed: {summary['total_forms']}")
        self.logger.info(f"Forms created: {summary['forms_created']}")
        self.logger.info(f"Forms failed: {summary['forms_failed']}")
        self.logger.info(f"Records posted: {summary['records_posted']}")
        self.logger.info(f"Records failed: {summary['records_failed']}")

        if summary['errors']:
            self.logger.info(f"\nErrors encountered: {len(summary['errors'])}")
            if self.options.get('verbose', False):
                for error in summary['errors']:
                    self.logger.error(f"  - {error}")

        self.logger.info("=" * 70)

        return summary
