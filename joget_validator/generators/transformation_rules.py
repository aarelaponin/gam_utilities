#!/usr/bin/env python3
"""
Transformation Rules
Handles data transformations based on services.yml rules
"""

from typing import Any, Optional
from datetime import datetime
import base64


class TransformationRules:
    """
    Applies transformation rules to values
    """

    def transform(self, value: Any, transformation: str) -> Any:
        """
        Apply a transformation to a value

        Args:
            value: Input value
            transformation: Transformation name from services.yml

        Returns:
            Transformed value
        """
        if value is None:
            return None

        # Map transformation name to method
        transformations = {
            'date_ISO8601': self._transform_date_iso8601,
            'numeric': self._transform_numeric,
            'yesNoBoolean': self._transform_yes_no_boolean,
            'multiCheckbox': self._transform_multi_checkbox,
            'base64': self._transform_base64
        }

        transform_func = transformations.get(transformation)
        if transform_func:
            return transform_func(value)

        # Unknown transformation, return original value
        return value

    def _transform_date_iso8601(self, value: Any) -> str:
        """
        Transform date to ISO8601 format

        Input formats:
        - "1987-12-24" (ISO date)
        - "1987-12-24T00:00:00Z" (ISO datetime)

        Output format:
        - "1987-12-24" (date only for Joget)
        """
        if not value:
            return ''

        # If already in correct format, return as is
        if isinstance(value, str):
            # Extract just the date part if datetime
            if 'T' in value:
                return value.split('T')[0]
            return value

        return str(value)

    def _transform_numeric(self, value: Any) -> str:
        """
        Transform to numeric string

        Args:
            value: Input value (string, int, float)

        Returns:
            Numeric string
        """
        if value is None or value == '':
            return ''

        # Convert to string, removing any non-numeric characters except . and -
        str_value = str(value)

        # Handle boolean values
        if isinstance(value, bool):
            return '1' if value else '0'

        # Remove commas and spaces
        str_value = str_value.replace(',', '').replace(' ', '')

        # Validate it's a number
        try:
            float(str_value)
            return str_value
        except ValueError:
            return '0'

    def _transform_yes_no_boolean(self, value: Any) -> str:
        """
        Transform boolean to yes/no string

        Args:
            value: Boolean or string value

        Returns:
            "yes" or "no"
        """
        if value is None:
            return 'no'

        # Handle boolean
        if isinstance(value, bool):
            return 'yes' if value else 'no'

        # Handle string
        str_value = str(value).lower()
        if str_value in ['true', '1', 'yes', 'y']:
            return 'yes'

        return 'no'

    def _transform_multi_checkbox(self, value: Any) -> str:
        """
        Transform array to comma-separated string

        Args:
            value: List or string value

        Returns:
            Comma-separated string
        """
        if not value:
            return ''

        # If already a string, return as is
        if isinstance(value, str):
            return value

        # If list, join with commas
        if isinstance(value, list):
            # Filter out None and empty values
            filtered = [str(v) for v in value if v]
            return ','.join(filtered)

        return str(value)

    def _transform_base64(self, value: Any) -> str:
        """
        Transform to base64 encoded string

        Args:
            value: String to encode

        Returns:
            Base64 encoded string
        """
        if not value:
            return ''

        # If already looks like base64, return as is
        if isinstance(value, str) and value.startswith('data:'):
            return value

        # Encode to base64
        try:
            if isinstance(value, str):
                encoded = base64.b64encode(value.encode('utf-8')).decode('utf-8')
                return f'data:text/plain;base64,{encoded}'
            return ''
        except Exception:
            return ''