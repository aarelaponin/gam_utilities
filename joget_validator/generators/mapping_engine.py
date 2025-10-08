#!/usr/bin/env python3
"""
Mapping Engine
Handles extraction of values from test data using GovStack paths
"""

from typing import Dict, Any, List, Optional


class MappingEngine:
    """
    Engine for mapping GovStack paths to values in test data
    """

    def __init__(self, services: Dict[str, Any], forms: Dict[str, Any]):
        """
        Initialize mapping engine

        Args:
            services: Parsed services.yml
            forms: Parsed form definitions
        """
        self.services = services
        self.forms = forms

    def extract_value(self, data: Dict[str, Any], path: str) -> Optional[Any]:
        """
        Extract a value from data using a dot-notation path

        Args:
            data: Source data dictionary
            path: Dot-notation path (e.g., "name.given[0]")

        Returns:
            Extracted value or None if not found
        """
        if not path or not data:
            return None

        # Handle array notation in path
        current = data
        segments = self._parse_path(path)

        for segment in segments:
            if current is None:
                return None

            if isinstance(segment, int):
                # Array index
                if isinstance(current, list) and 0 <= segment < len(current):
                    current = current[segment]
                else:
                    return None
            else:
                # Dictionary key
                if isinstance(current, dict):
                    current = current.get(segment)
                else:
                    return None

        return current

    def extract_array(self, data: Dict[str, Any], path: str) -> List[Dict[str, Any]]:
        """
        Extract an array from data using a path

        Args:
            data: Source data dictionary
            path: Path to array

        Returns:
            List of items or empty list if not found
        """
        value = self.extract_value(data, path)

        if isinstance(value, list):
            return value

        return []

    def _parse_path(self, path: str) -> List:
        """
        Parse a path into segments, handling array notation

        Examples:
            "name.given[0]" -> ["name", "given", 0]
            "address[0].city" -> ["address", 0, "city"]

        Args:
            path: Dot and bracket notation path

        Returns:
            List of path segments
        """
        segments = []
        current = ""

        i = 0
        while i < len(path):
            char = path[i]

            if char == '.':
                if current:
                    segments.append(current)
                    current = ""
                i += 1

            elif char == '[':
                # Save current segment if exists
                if current:
                    segments.append(current)
                    current = ""

                # Extract array index
                i += 1
                index_str = ""
                while i < len(path) and path[i] != ']':
                    index_str += path[i]
                    i += 1

                if index_str.isdigit():
                    segments.append(int(index_str))

                # Skip the closing bracket
                if i < len(path) and path[i] == ']':
                    i += 1

            else:
                current += char
                i += 1

        # Add final segment
        if current:
            segments.append(current)

        return segments

    def get_table_name(self, section_name: str) -> str:
        """
        Get the database table name for a form section

        Args:
            section_name: Section name from services.yml

        Returns:
            Database table name with app_fd_ prefix
        """
        form_mappings = self.services.get('formMappings', {})
        section = form_mappings.get(section_name, {})
        table_name = section.get('tableName', '')

        # Ensure app_fd_ prefix
        if table_name and not table_name.startswith('app_fd_'):
            table_name = f'app_fd_{table_name}'

        return table_name

    def get_column_name(self, field_id: str) -> str:
        """
        Get the database column name for a field

        Args:
            field_id: Field ID from form definition

        Returns:
            Database column name with c_ prefix
        """
        if not field_id:
            return ''

        # System fields don't get c_ prefix
        system_fields = ['id', 'dateCreated', 'dateModified', 'createdBy',
                        'createdByName', 'modifiedBy', 'modifiedByName']

        if field_id in system_fields:
            return field_id

        # All user fields get c_ prefix
        return f'c_{field_id}'