#!/usr/bin/env python3
"""
Field Validator
Field-level validation logic with type-aware comparisons
"""

import logging
from typing import Any, Optional, Dict
from datetime import datetime
import re


class FieldValidator:
    """
    Field-level validation logic
    Handles type-aware value comparisons and transformations
    """

    def __init__(self, validation_config: Dict[str, Any]):
        """
        Initialize field validator

        Args:
            validation_config: Validation configuration settings
        """
        self.config = validation_config.get('validation', {})
        self.logger = logging.getLogger('joget_validator.field_validator')

        # Get comparison settings
        self.case_sensitive = self.config.get('case_sensitive', False)
        self.trim_strings = self.config.get('trim_strings', True)
        self.null_equals_empty = self.config.get('null_equals_empty', True)

    @staticmethod
    def compare_values(expected: Any, actual: Any, field_type: str = None) -> bool:
        """
        Compare two values considering type and format

        Args:
            expected: Expected value from test data
            actual: Actual value from database
            field_type: Type of the field (string, number, boolean, date, etc.)

        Returns:
            True if values match, False otherwise
        """
        validator = FieldValidator({})  # Create instance for method access
        return validator._compare_values_impl(expected, actual, field_type)

    def _compare_values_impl(self, expected: Any, actual: Any, field_type: str = None) -> bool:
        """
        Internal implementation of value comparison

        Args:
            expected: Expected value from test data
            actual: Actual value from database
            field_type: Type of the field

        Returns:
            True if values match, False otherwise
        """
        # Handle null/empty equivalence
        if self.null_equals_empty:
            if self._is_null_or_empty(expected) and self._is_null_or_empty(actual):
                return True

        # If one is null/empty and the other isn't
        if self._is_null_or_empty(expected) != self._is_null_or_empty(actual):
            return False

        # If both are null/empty (and null_equals_empty is False)
        if self._is_null_or_empty(expected) and self._is_null_or_empty(actual):
            return expected == actual

        # Type-specific comparisons
        if field_type:
            return self._compare_by_type(expected, actual, field_type)
        else:
            return self._compare_generic(expected, actual)

    def _is_null_or_empty(self, value: Any) -> bool:
        """Check if value is null or empty"""
        return value is None or value == '' or (isinstance(value, str) and value.strip() == '')

    def _compare_by_type(self, expected: Any, actual: Any, field_type: str) -> bool:
        """
        Compare values based on specific field type

        Args:
            expected: Expected value
            actual: Actual value
            field_type: Field type (string, number, boolean, date, etc.)

        Returns:
            True if values match
        """
        try:
            if field_type == 'string':
                return self._compare_strings(expected, actual)
            elif field_type in ['number', 'integer', 'float', 'decimal']:
                return self._compare_numbers(expected, actual)
            elif field_type == 'boolean':
                return self._compare_booleans(expected, actual)
            elif field_type in ['date', 'datetime', 'timestamp']:
                return self._compare_dates(expected, actual)
            else:
                return self._compare_generic(expected, actual)

        except Exception as e:
            self.logger.warning(f"Error comparing values of type {field_type}: {e}")
            return self._compare_generic(expected, actual)

    def _compare_strings(self, expected: Any, actual: Any) -> bool:
        """Compare string values"""
        # Convert to strings
        exp_str = str(expected) if expected is not None else ''
        act_str = str(actual) if actual is not None else ''

        # Apply trimming if configured
        if self.trim_strings:
            exp_str = exp_str.strip()
            act_str = act_str.strip()

        # Apply case sensitivity
        if not self.case_sensitive:
            exp_str = exp_str.lower()
            act_str = act_str.lower()

        return exp_str == act_str

    def _compare_numbers(self, expected: Any, actual: Any) -> bool:
        """Compare numeric values"""
        try:
            # Convert to float for comparison
            exp_num = float(expected) if expected is not None else 0.0
            act_num = float(actual) if actual is not None else 0.0

            # Use a small epsilon for float comparison
            epsilon = 1e-9
            return abs(exp_num - act_num) < epsilon

        except (ValueError, TypeError):
            # Fall back to string comparison if conversion fails
            return self._compare_strings(expected, actual)

    def _compare_booleans(self, expected: Any, actual: Any) -> bool:
        """Compare boolean values"""
        try:
            exp_bool = self._to_boolean(expected)
            act_bool = self._to_boolean(actual)
            return exp_bool == act_bool

        except (ValueError, TypeError):
            return self._compare_strings(expected, actual)

    def _compare_dates(self, expected: Any, actual: Any) -> bool:
        """Compare date/datetime values"""
        try:
            exp_date = self._parse_date(expected)
            act_date = self._parse_date(actual)

            if exp_date and act_date:
                # Compare dates (ignore time if both are date objects)
                if hasattr(exp_date, 'date') and hasattr(act_date, 'date'):
                    return exp_date.date() == act_date.date()
                else:
                    return exp_date == act_date

            return False

        except (ValueError, TypeError):
            return self._compare_strings(expected, actual)

    def _compare_generic(self, expected: Any, actual: Any) -> bool:
        """Generic value comparison"""
        # Try direct comparison first
        if expected == actual:
            return True

        # Try string comparison as fallback
        return self._compare_strings(expected, actual)

    def _to_boolean(self, value: Any) -> bool:
        """Convert value to boolean"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ['true', '1', 'yes', 'on', 'y']
        if isinstance(value, (int, float)):
            return bool(value)
        return False

    def _parse_date(self, value: Any) -> Optional[datetime]:
        """Parse date value from various formats"""
        if value is None:
            return None

        if isinstance(value, datetime):
            return value

        if isinstance(value, str):
            # Try common date formats
            date_formats = [
                '%Y-%m-%d',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S',
                '%d/%m/%Y',
                '%m/%d/%Y',
                '%d-%m-%Y',
                '%Y%m%d'
            ]

            for fmt in date_formats:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue

        return None

    @staticmethod
    def apply_transformation(value: Any, transform: str) -> Any:
        """
        Apply transformation to value

        Args:
            value: Value to transform
            transform: Type of transformation to apply

        Returns:
            Transformed value
        """
        if not transform or value is None:
            return value

        try:
            if transform == 'uppercase':
                return str(value).upper()
            elif transform == 'lowercase':
                return str(value).lower()
            elif transform == 'trim':
                return str(value).strip()
            elif transform == 'boolean':
                return FieldValidator._to_boolean_static(value)
            elif transform == 'number':
                return float(value)
            elif transform == 'integer':
                return int(float(value))
            elif transform == 'string':
                return str(value)
            elif transform == 'null_to_empty':
                return '' if value is None else value
            elif transform == 'empty_to_null':
                return None if value == '' else value
            else:
                return value

        except (ValueError, TypeError):
            return value

    @staticmethod
    def _to_boolean_static(value: Any) -> bool:
        """Static version of boolean conversion"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ['true', '1', 'yes', 'on', 'y']
        if isinstance(value, (int, float)):
            return bool(value)
        return False

    def validate_format(self, value: Any, format_pattern: str) -> bool:
        """
        Validate value against a format pattern

        Args:
            value: Value to validate
            format_pattern: Regex pattern or format string

        Returns:
            True if value matches format
        """
        if value is None:
            return False

        try:
            value_str = str(value)
            return bool(re.match(format_pattern, value_str))

        except re.error as e:
            self.logger.warning(f"Invalid regex pattern '{format_pattern}': {e}")
            return True  # Don't fail validation for bad patterns

    def validate_range(self, value: Any, min_val: Any = None, max_val: Any = None) -> bool:
        """
        Validate value is within specified range

        Args:
            value: Value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value

        Returns:
            True if value is within range
        """
        if value is None:
            return True  # Null values pass range validation

        try:
            # Try numeric comparison
            num_value = float(value)
            if min_val is not None and num_value < float(min_val):
                return False
            if max_val is not None and num_value > float(max_val):
                return False
            return True

        except (ValueError, TypeError):
            # Fall back to string comparison
            str_value = str(value)
            if min_val is not None and str_value < str(min_val):
                return False
            if max_val is not None and str_value > str(max_val):
                return False
            return True