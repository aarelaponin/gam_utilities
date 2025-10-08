#!/usr/bin/env python3
"""
JSON data processor for Joget imports
"""

import json
from typing import Dict, List, Any, Union, Optional
from pathlib import Path
from .base import BaseProcessor


class JSONProcessor(BaseProcessor):
    """Processor for JSON data files"""

    def __init__(self, field_mapping: Dict[str, str] = None):
        """
        Initialize JSON processor

        Args:
            field_mapping: Dictionary mapping source fields to target fields
        """
        super().__init__(field_mapping)

    def read_file(self, file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Read JSON file

        Args:
            file_path: Path to the JSON file

        Returns:
            List of dictionaries representing records

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not valid JSON or has unexpected format
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not file_path.is_file():
            raise ValueError(f"Not a file: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON file: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error reading JSON file: {str(e)}")

        # Handle different JSON structures
        records = []

        if isinstance(data, list):
            # Array of objects
            for item in data:
                if isinstance(item, dict):
                    records.append(item)
                else:
                    self.warnings.append(f"Skipping non-dictionary item: {item}")

        elif isinstance(data, dict):
            # Single object or wrapped array
            if 'data' in data and isinstance(data['data'], list):
                # Common pattern: {"data": [...]}
                for item in data['data']:
                    if isinstance(item, dict):
                        records.append(item)
            elif 'records' in data and isinstance(data['records'], list):
                # Alternative pattern: {"records": [...]}
                for item in data['records']:
                    if isinstance(item, dict):
                        records.append(item)
            elif 'testData' in data and isinstance(data['testData'], list):
                # GovStack pattern: {"testData": [...]}
                for item in data['testData']:
                    if isinstance(item, dict):
                        records.append(item)
            else:
                # Treat as single record
                records.append(data)
        else:
            raise ValueError(f"Unexpected JSON structure: expected array or object")

        if not records:
            raise ValueError(f"No valid records found in file: {file_path}")

        return records

    def validate_record(self, record: Dict[str, Any]) -> Optional[str]:
        """
        Validate JSON record

        Args:
            record: Record to validate

        Returns:
            Error message if invalid, None if valid
        """
        # Call parent validation
        base_error = super().validate_record(record)
        if base_error:
            return base_error

        # Add JSON-specific validation if needed
        # For example, check for nested objects that might need flattening
        for key, value in record.items():
            if isinstance(value, (dict, list)):
                self.warnings.append(f"Field '{key}' contains complex data structure")

        return None

    def flatten_record(self, record: Dict[str, Any], separator: str = '_') -> Dict[str, Any]:
        """
        Flatten nested dictionary structures

        Args:
            record: Record to flatten
            separator: Separator for nested keys

        Returns:
            Flattened dictionary
        """
        def _flatten(obj, parent_key=''):
            items = []
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_key = f"{parent_key}{separator}{k}" if parent_key else k
                    if isinstance(v, dict):
                        items.extend(_flatten(v, new_key).items())
                    elif isinstance(v, list):
                        # Convert list to string or handle as needed
                        items.append((new_key, json.dumps(v) if v else ''))
                    else:
                        items.append((new_key, v))
            else:
                items.append((parent_key, obj))
            return dict(items)

        return _flatten(record)