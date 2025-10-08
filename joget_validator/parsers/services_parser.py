#!/usr/bin/env python3
"""
Services.yml Parser for Joget Validation
Parses services.yml to extract form mappings and transformations
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable


class ServicesParser:
    """
    Parser for services.yml configuration file
    Extracts form mappings, grid configurations, and transformations
    """

    def __init__(self, yml_path: str):
        """
        Initialize services parser

        Args:
            yml_path: Path to services.yml file
        """
        self.yml_path = Path(yml_path)
        self.logger = logging.getLogger('joget_validator.services_parser')
        self.config = self._load_yaml()
        self.transformations = self._load_transformations()

    def _load_yaml(self) -> Dict[str, Any]:
        """
        Load and parse services.yml file

        Returns:
            Parsed YAML configuration
        """
        if not self.yml_path.exists():
            raise FileNotFoundError(f"Services configuration file not found: {self.yml_path}")

        try:
            with open(self.yml_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                self.logger.info(f"Loaded services configuration from {self.yml_path}")
                return config

        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML file: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading services file: {e}")
            raise

    def _load_transformations(self) -> Dict[str, Callable]:
        """
        Load transformation functions

        Returns:
            Dictionary of transformation name to function mappings
        """
        transformations = {
            'uppercase': lambda x: str(x).upper() if x is not None else None,
            'lowercase': lambda x: str(x).lower() if x is not None else None,
            'trim': lambda x: str(x).strip() if x is not None else None,
            'boolean': self._transform_boolean,
            'date_format': self._transform_date,
            'number': self._transform_number,
            'string': lambda x: str(x) if x is not None else None,
            'null_to_empty': lambda x: '' if x is None else x,
            'empty_to_null': lambda x: None if x == '' else x,
        }
        return transformations

    def _transform_boolean(self, value: Any) -> Optional[bool]:
        """Transform value to boolean"""
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ['true', '1', 'yes', 'on']
        if isinstance(value, (int, float)):
            return bool(value)
        return None

    def _transform_date(self, value: Any) -> Optional[str]:
        """Transform date value to standard format"""
        if value is None:
            return None
        # Add date transformation logic here
        return str(value)

    def _transform_number(self, value: Any) -> Optional[float]:
        """Transform value to number"""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def get_forms(self) -> List[str]:
        """
        Get list of all form names

        Returns:
            List of form names
        """
        forms = []

        # Check different possible structure locations
        if 'forms' in self.config:
            if isinstance(self.config['forms'], dict):
                forms.extend(self.config['forms'].keys())

        if 'formMappings' in self.config:
            if isinstance(self.config['formMappings'], dict):
                # Exclude grids/arrays from forms
                for name, config in self.config['formMappings'].items():
                    if isinstance(config, dict) and config.get('type') != 'array':
                        forms.append(name)

        if 'govstack' in self.config:
            if isinstance(self.config['govstack'], dict) and 'forms' in self.config['govstack']:
                if isinstance(self.config['govstack']['forms'], dict):
                    forms.extend(self.config['govstack']['forms'].keys())

        # Look for form definitions in services
        if 'services' in self.config:
            for service_name, service_config in self.config['services'].items():
                if isinstance(service_config, dict) and 'forms' in service_config:
                    forms.extend(service_config['forms'].keys())

        return list(set(forms))

    def get_grids(self) -> List[str]:
        """
        Get list of all grid names

        Returns:
            List of grid names
        """
        grids = []

        # Check different possible structure locations
        if 'grids' in self.config:
            if isinstance(self.config['grids'], dict):
                grids.extend(self.config['grids'].keys())

        if 'formMappings' in self.config:
            if isinstance(self.config['formMappings'], dict):
                # Find grids/arrays in formMappings
                for name, config in self.config['formMappings'].items():
                    if isinstance(config, dict) and config.get('type') == 'array':
                        grids.append(name)

        if 'govstack' in self.config:
            if isinstance(self.config['govstack'], dict) and 'grids' in self.config['govstack']:
                if isinstance(self.config['govstack']['grids'], dict):
                    grids.extend(self.config['govstack']['grids'].keys())

        # Look for grid definitions in services
        if 'services' in self.config:
            for service_name, service_config in self.config['services'].items():
                if isinstance(service_config, dict) and 'grids' in service_config:
                    grids.extend(service_config['grids'].keys())

        return list(set(grids))

    def get_form_mappings(self, form_name: str) -> Dict[str, Any]:
        """
        Get field mappings for a specific form

        Args:
            form_name: Name of the form

        Returns:
            Dictionary containing form configuration and field mappings
        """
        form_config = None

        # Check formMappings first (new structure)
        if 'formMappings' in self.config and form_name in self.config['formMappings']:
            form_config = self.config['formMappings'][form_name]
        else:
            # Search in different locations
            search_paths = [
                ('forms', form_name),
                ('govstack', 'forms', form_name),
            ]

            # Also search in services
            if 'services' in self.config:
                for service_name, service_config in self.config['services'].items():
                    if 'forms' in service_config and form_name in service_config['forms']:
                        search_paths.append(('services', service_name, 'forms', form_name))

            for path in search_paths:
                config_section = self.config
                try:
                    for key in path:
                        config_section = config_section[key]
                    form_config = config_section
                    break
                except KeyError:
                    continue

        if not form_config:
            self.logger.warning(f"Form configuration not found: {form_name}")
            return {}

        # Extract mappings
        mappings = {}

        # Look for fields/mapping configuration
        if 'fields' in form_config:
            if isinstance(form_config['fields'], list):
                # New structure: fields is a list of field objects
                mappings = self._extract_field_mappings_from_list(form_config['fields'])
            else:
                # Old structure: fields is a dict
                mappings = self._extract_field_mappings(form_config['fields'])
        elif 'mapping' in form_config:
            mappings = self._extract_field_mappings(form_config['mapping'])

        # Add table name and other metadata
        result = {
            'table_name': form_config.get('tableName') or form_config.get('table', f'app_fd_{form_name}'),
            'mappings': mappings,
            'config': form_config
        }

        self.logger.debug(f"Form {form_name} mappings: {len(mappings)} fields")
        return result

    def get_grid_config(self, grid_name: str) -> Dict[str, Any]:
        """
        Get configuration for a grid

        Args:
            grid_name: Name of the grid

        Returns:
            Dictionary containing grid configuration
        """
        grid_config = None

        # Check formMappings first (grids are there with type='array')
        if 'formMappings' in self.config and grid_name in self.config['formMappings']:
            config = self.config['formMappings'][grid_name]
            if config.get('type') == 'array':
                grid_config = config
        else:
            # Search in different locations
            search_paths = [
                ('grids', grid_name),
                ('govstack', 'grids', grid_name),
            ]

            # Also search in services
            if 'services' in self.config:
                for service_name, service_config in self.config['services'].items():
                    if 'grids' in service_config and grid_name in service_config['grids']:
                        search_paths.append(('services', service_name, 'grids', grid_name))

            for path in search_paths:
                config_section = self.config
                try:
                    for key in path:
                        config_section = config_section[key]
                    grid_config = config_section
                    break
                except KeyError:
                    continue

        if not grid_config:
            self.logger.warning(f"Grid configuration not found: {grid_name}")
            return {}

        # Extract mappings
        mappings = {}

        if 'fields' in grid_config:
            if isinstance(grid_config['fields'], list):
                # New structure: fields is a list of field objects
                mappings = self._extract_field_mappings_from_list(grid_config['fields'])
            else:
                # Old structure: fields is a dict
                mappings = self._extract_field_mappings(grid_config['fields'])
        elif 'mapping' in grid_config:
            mappings = self._extract_field_mappings(grid_config['mapping'])

        # Add table name and other metadata
        result = {
            'table_name': grid_config.get('tableName') or grid_config.get('table', f'app_fd_{grid_name}'),
            'parent_field': grid_config.get('parentKey') or grid_config.get('parent_field', 'c_farmer_id'),
            'mappings': mappings,
            'config': grid_config
        }

        self.logger.debug(f"Grid {grid_name} configuration: {len(mappings)} fields")
        return result

    def _extract_field_mappings(self, fields_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract field mappings from configuration

        Args:
            fields_config: Fields configuration section

        Returns:
            Dictionary of field mappings
        """
        mappings = {}

        for field_name, field_config in fields_config.items():
            if isinstance(field_config, dict):
                mapping = {
                    'joget_column': field_config.get('joget', f'c_{field_name}'),
                    'json_path': field_config.get('govstack', {}).get('jsonPath', field_name),
                    'transform': field_config.get('transform'),
                    'required': field_config.get('required', False),
                    'type': field_config.get('type', 'string')
                }
            else:
                # Simple string mapping
                mapping = {
                    'joget_column': f'c_{field_name}',
                    'json_path': field_name,
                    'transform': None,
                    'required': False,
                    'type': 'string'
                }

            mappings[field_name] = mapping

        return mappings

    def _extract_field_mappings_from_list(self, fields_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract field mappings from list format (new structure)

        Args:
            fields_list: List of field configurations

        Returns:
            Dictionary of field mappings
        """
        mappings = {}

        for field_config in fields_list:
            if not isinstance(field_config, dict):
                continue

            # Get the Joget field name
            joget_name = field_config.get('joget', '')
            if not joget_name:
                continue

            # Create mapping
            mapping = {
                'joget_column': field_config.get('column', f'c_{joget_name}'),
                'json_path': field_config.get('govstack', '') or field_config.get('jsonPath', joget_name),
                'transform': field_config.get('transform'),
                'required': field_config.get('required', False),
                'type': field_config.get('type', 'string'),
                'valueMapping': field_config.get('valueMapping')
            }

            mappings[joget_name] = mapping

        return mappings

    def get_transformation(self, transform_type: str) -> Optional[Callable]:
        """
        Get transformation function

        Args:
            transform_type: Type of transformation

        Returns:
            Transformation function or None if not found
        """
        return self.transformations.get(transform_type)

    def apply_transformation(self, value: Any, transform_type: str) -> Any:
        """
        Apply transformation to a value

        Args:
            value: Value to transform
            transform_type: Type of transformation to apply

        Returns:
            Transformed value
        """
        if not transform_type:
            return value

        transform_func = self.get_transformation(transform_type)
        if transform_func:
            try:
                return transform_func(value)
            except Exception as e:
                self.logger.warning(f"Transformation {transform_type} failed for value {value}: {e}")
                return value
        else:
            self.logger.warning(f"Unknown transformation type: {transform_type}")
            return value

    def get_all_mappings(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all form and grid mappings

        Returns:
            Dictionary containing all mappings organized by type
        """
        all_mappings = {
            'forms': {},
            'grids': {}
        }

        # Get all forms
        for form_name in self.get_forms():
            all_mappings['forms'][form_name] = self.get_form_mappings(form_name)

        # Get all grids
        for grid_name in self.get_grids():
            all_mappings['grids'][grid_name] = self.get_grid_config(grid_name)

        return all_mappings