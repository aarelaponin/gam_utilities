#!/usr/bin/env python3
"""
CSV data processor for Joget imports
"""

import csv
from typing import Dict, List, Any, Union, Optional
from pathlib import Path
from .base import BaseProcessor


class CSVProcessor(BaseProcessor):
    """Processor for CSV data files"""

    def __init__(self, field_mapping: Dict[str, str] = None, delimiter: str = ','):
        """
        Initialize CSV processor

        Args:
            field_mapping: Dictionary mapping source fields to target fields
            delimiter: CSV delimiter character
        """
        super().__init__(field_mapping)
        self.delimiter = delimiter

    def read_file(self, file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Read CSV file

        Args:
            file_path: Path to the CSV file

        Returns:
            List of dictionaries representing records

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is empty or invalid
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not file_path.is_file():
            raise ValueError(f"Not a file: {file_path}")

        records = []

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Detect delimiter if needed
                sample = file.read(1024)
                file.seek(0)

                sniffer = csv.Sniffer()
                try:
                    detected_delimiter = sniffer.sniff(sample).delimiter
                    if detected_delimiter and self.delimiter == ',':
                        self.delimiter = detected_delimiter
                except:
                    pass  # Use default delimiter

                reader = csv.DictReader(file, delimiter=self.delimiter)

                for row_num, row in enumerate(reader, start=1):
                    # Clean up row data
                    cleaned_row = {}
                    for key, value in row.items():
                        if key:  # Skip empty column names
                            # Strip whitespace and handle None
                            cleaned_value = value.strip() if value else ''
                            cleaned_row[key.strip()] = cleaned_value

                    if cleaned_row:  # Only add non-empty rows
                        records.append(cleaned_row)

        except Exception as e:
            raise ValueError(f"Error reading CSV file: {str(e)}")

        if not records:
            raise ValueError(f"No data found in file: {file_path}")

        return records

    def validate_record(self, record: Dict[str, Any]) -> Optional[str]:
        """
        Validate CSV record

        Args:
            record: Record to validate

        Returns:
            Error message if invalid, None if valid
        """
        # Call parent validation
        base_error = super().validate_record(record)
        if base_error:
            return base_error

        # Add CSV-specific validation if needed
        # For example, check for completely empty records
        if all(not value for value in record.values()):
            return "All fields are empty"

        return None