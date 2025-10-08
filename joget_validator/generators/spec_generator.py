#!/usr/bin/env python3
"""
Validation Specification Generator
Core class that orchestrates the generation of test-validation.yml
"""

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

from .mapping_engine import MappingEngine
from .transformation_rules import TransformationRules


class ValidationSpecGenerator:
    """
    Generates validation specification from form definitions, services.yml, and test data
    """

    def __init__(self, forms_dir: str, services_yml: str, test_data_json: str, verbose: bool = False):
        """
        Initialize the generator

        Args:
            forms_dir: Directory containing form JSON definitions
            services_yml: Path to services.yml file
            test_data_json: Path to test-data.json file
            verbose: Enable verbose output
        """
        self.forms_dir = Path(forms_dir)
        self.services_yml = Path(services_yml)
        self.test_data_json = Path(test_data_json)
        self.verbose = verbose

        # Load inputs
        self.forms = self._load_forms()
        self.services = self._load_services()
        self.test_data = self._load_test_data()

        # Initialize components
        self.mapping_engine = MappingEngine(self.services, self.forms)
        self.transformer = TransformationRules()

        if self.verbose:
            print(f"Loaded {len(self.forms)} form definitions")
            print(f"Loaded services.yml with {len(self.services.get('formMappings', {}))} form mappings")
            print(f"Loaded test data with {len(self.test_data)} records")

    def _load_forms(self) -> Dict[str, Any]:
        """Load all form JSON definitions"""
        forms = {}

        for json_file in self.forms_dir.glob("*.json"):
            with open(json_file, 'r') as f:
                data = json.load(f)

                # Extract form info from different JSON structures
                form_def = None
                form_id = None

                if 'className' in data and 'Form' in data.get('className', ''):
                    form_def = data
                    props = data.get('properties', {})
                    form_id = props.get('id', json_file.stem)
                elif 'formDefId' in data:
                    form_def = data
                    form_id = data.get('formDefId')

                if form_def and form_id:
                    forms[form_id] = form_def
                    if self.verbose:
                        print(f"  Loaded form: {form_id} from {json_file.name}")

        return forms

    def _load_services(self) -> Dict[str, Any]:
        """Load services.yml mappings"""
        with open(self.services_yml, 'r') as f:
            return yaml.safe_load(f)

    def _load_test_data(self) -> List[Dict[str, Any]]:
        """Load test-data.json"""
        with open(self.test_data_json, 'r') as f:
            data = json.load(f)

            # Handle wrapped format
            if 'testData' in data:
                return data['testData']
            elif isinstance(data, list):
                return data
            else:
                return [data]

    def generate_spec(self) -> Dict[str, Any]:
        """
        Generate the complete validation specification

        Returns:
            Complete specification as a dictionary
        """
        # Get the first test record (farmer-002)
        if not self.test_data:
            raise ValueError("No test data found")

        test_record = self.test_data[0]
        test_id = test_record.get('id', 'unknown')

        spec = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'generator_version': '1.0',
                'inputs': {
                    'forms_dir': str(self.forms_dir),
                    'services_yml': str(self.services_yml),
                    'test_data': str(self.test_data_json)
                }
            },
            'test_case': {
                'id': test_id,
                'source_data': str(self.test_data_json),
                'farmer_name': self._extract_farmer_name(test_record)
            },
            'expected_state': {
                'tables': {}
            }
        }

        # Process each form mapping
        form_mappings = self.services.get('formMappings', {})

        for section_name, section_config in form_mappings.items():
            if self.verbose:
                print(f"\nProcessing section: {section_name}")

            # Skip if it's metadata section
            if section_name in ['metadata', 'transformations']:
                continue

            section_type = section_config.get('type', 'form')

            if section_type == 'array':
                # Handle grid/array data
                self._process_grid_section(
                    section_name, section_config, test_record,
                    spec['expected_state']['tables'], test_id
                )
            else:
                # Handle regular form data
                self._process_form_section(
                    section_name, section_config, test_record,
                    spec['expected_state']['tables'], test_id
                )

        return spec

    def _process_form_section(self, section_name: str, config: Dict, test_record: Dict,
                             tables: Dict, parent_id: str):
        """Process a regular form section"""

        table_name = config.get('tableName')
        if not table_name:
            if self.verbose:
                print(f"  Skipping {section_name}: no tableName")
            return

        # Ensure table name has app_fd_ prefix
        if not table_name.startswith('app_fd_'):
            table_name = f'app_fd_{table_name}'

        if self.verbose:
            print(f"  Processing table: {table_name}")

        # Initialize table spec if not exists
        if table_name not in tables:
            tables[table_name] = {
                'record_count': 0,
                'primary_key': 'id',
                'records': []
            }

        # Create record
        record = {
            'id': parent_id,
            'c_parent_id': parent_id  # Parent linking field
        }

        # Process fields
        fields = config.get('fields', [])
        for field_config in fields:
            field_id = field_config.get('joget')
            govstack_path = field_config.get('govstack')

            if not field_id or not govstack_path:
                continue

            # Skip parent_id as we already added it
            if field_id == 'parent_id':
                continue

            # Extract value from test data
            value = self.mapping_engine.extract_value(test_record, govstack_path)

            # Apply transformations
            transformation = field_config.get('transform')
            if transformation and value is not None:
                value = self.transformer.transform(value, transformation)

            # Apply value mappings
            value_mapping = field_config.get('valueMapping')
            if value_mapping and value in value_mapping:
                value = value_mapping[value]

            # Add to record with c_ prefix
            column_name = f'c_{field_id}'
            record[column_name] = value if value is not None else ''

            if self.verbose and value is not None:
                print(f"    {column_name}: {value}")

        # Add record to table
        tables[table_name]['records'].append(record)
        tables[table_name]['record_count'] = len(tables[table_name]['records'])

    def _process_grid_section(self, section_name: str, config: Dict, test_record: Dict,
                             tables: Dict, parent_id: str):
        """Process a grid/array section"""

        table_name = config.get('tableName')
        if not table_name:
            return

        # Ensure table name has app_fd_ prefix
        if not table_name.startswith('app_fd_'):
            table_name = f'app_fd_{table_name}'

        govstack_path = config.get('govstack')
        if not govstack_path:
            return

        if self.verbose:
            print(f"  Processing grid table: {table_name}")
            print(f"    Looking for array at: {govstack_path}")

        # Extract array data from test record
        array_data = self.mapping_engine.extract_array(test_record, govstack_path)

        if not array_data:
            if self.verbose:
                print(f"    No array data found")
            return

        if self.verbose:
            print(f"    Found {len(array_data)} records")

        # Initialize table spec
        parent_field = config.get('parentField', 'farmer_id')

        tables[table_name] = {
            'record_count': len(array_data),
            'primary_key': 'id',
            'parent_link': f'c_{parent_field}',
            'records': []
        }

        # Process each array item
        fields = config.get('fields', [])

        for item in array_data:
            record = {
                f'c_{parent_field}': parent_id  # Parent link
            }

            # Process fields for this item
            for field_config in fields:
                field_id = field_config.get('joget')
                govstack_path = field_config.get('govstack')

                if not field_id or not govstack_path:
                    continue

                # Skip parent field as we already added it
                if field_id == parent_field:
                    continue

                # Extract value from item
                value = self.mapping_engine.extract_value(item, govstack_path)

                # Apply transformations
                transformation = field_config.get('transform')
                if transformation and value is not None:
                    value = self.transformer.transform(value, transformation)

                # Apply value mappings
                value_mapping = field_config.get('valueMapping')
                if value_mapping and value in value_mapping:
                    value = value_mapping[value]

                # Add to record
                column_name = f'c_{field_id}'
                record[column_name] = value if value is not None else ''

            tables[table_name]['records'].append(record)

    def _extract_farmer_name(self, test_record: Dict) -> str:
        """Extract farmer full name from test record"""
        name_obj = test_record.get('name', {})
        given_names = name_obj.get('given', [])
        family_name = name_obj.get('family', '')

        full_name = ' '.join(given_names) + ' ' + family_name
        return full_name.strip()

    def save_spec(self, output_path: str):
        """
        Save the specification to a YAML file

        Args:
            output_path: Path to save the specification
        """
        spec = self.generate_spec()

        with open(output_path, 'w') as f:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False, indent=2)

        if self.verbose:
            print(f"\nSpecification saved to: {output_path}")