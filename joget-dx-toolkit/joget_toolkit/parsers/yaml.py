"""
YAML parser (identity transformation with validation).

Reads YAML files that are already in canonical format and validates them.
This is mainly for validation and normalization purposes.
"""

from pathlib import Path
from typing import Union

from joget_toolkit.parsers.base import BaseParser
from joget_toolkit.specs.schema import AppSpec
from joget_toolkit.specs.validator import SpecValidator


class YAMLParser(BaseParser):
    """Parser for YAML files (identity transformation with validation)"""

    def parse(self, input_path: Union[str, Path], **kwargs) -> AppSpec:
        """
        Parse YAML file and return validated AppSpec.

        Args:
            input_path: Path to YAML file
            **kwargs: Not used (for consistency with base class)

        Returns:
            Validated AppSpec

        Raises:
            FileNotFoundError: If file doesn't exist
            ValidationError: If YAML doesn't match canonical format
        """
        # Use validator to load and validate
        app_spec = SpecValidator.validate_yaml(input_path)

        return self._validate_result(app_spec)
