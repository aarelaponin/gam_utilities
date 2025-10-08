#!/usr/bin/env python3
"""
Base processor class for data transformations
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from pathlib import Path


class BaseProcessor(ABC):
    """Abstract base class for data processors"""

    def __init__(self, field_mapping: Dict[str, str] = None):
        """
        Initialize processor with optional field mapping

        Args:
            field_mapping: Dictionary mapping source fields to target fields
        """
        self.field_mapping = field_mapping or {}
        self.errors = []
        self.warnings = []

    @abstractmethod
    def read_file(self, file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Read data from file

        Args:
            file_path: Path to the input file

        Returns:
            List of dictionaries representing records
        """
        pass

    def transform_record(self, record: Dict[str, Any],
                        required_fields: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Transform a single record according to field mapping

        Args:
            record: Input record
            required_fields: List of required field names

        Returns:
            Transformed record or None if validation fails
        """
        # Apply field mapping
        transformed = {}
        for source_field, target_field in self.field_mapping.items():
            if source_field in record:
                transformed[target_field] = record[source_field]

        # If no mapping, use original fields
        if not self.field_mapping:
            transformed = record.copy()

        # Validate required fields
        if required_fields:
            missing_fields = [f for f in required_fields if f not in transformed or not transformed[f]]
            if missing_fields:
                self.errors.append(f"Missing required fields: {', '.join(missing_fields)}")
                return None

        # Clean up empty values
        transformed = {k: v for k, v in transformed.items() if v is not None and v != ''}

        return transformed

    def validate_record(self, record: Dict[str, Any]) -> Optional[str]:
        """
        Validate a single record

        Args:
            record: Record to validate

        Returns:
            Error message if invalid, None if valid
        """
        if not record:
            return "Empty record"

        # Subclasses can add specific validation
        return None

    def process_file(self, file_path: Union[str, Path],
                    required_fields: List[str] = None) -> List[Dict[str, Any]]:
        """
        Process entire file: read, transform, and validate

        Args:
            file_path: Path to the input file
            required_fields: List of required field names

        Returns:
            List of processed records
        """
        self.errors = []
        self.warnings = []

        # Read file
        try:
            records = self.read_file(file_path)
        except Exception as e:
            self.errors.append(f"Error reading file: {str(e)}")
            return []

        # Process records
        processed = []
        for idx, record in enumerate(records):
            # Validate
            error = self.validate_record(record)
            if error:
                self.warnings.append(f"Record {idx + 1}: {error}")
                continue

            # Transform
            transformed = self.transform_record(record, required_fields)
            if transformed:
                processed.append(transformed)

        return processed

    def get_summary(self) -> Dict[str, Any]:
        """
        Get processing summary

        Returns:
            Dictionary with processing statistics
        """
        return {
            "errors": self.errors,
            "warnings": self.warnings,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings)
        }