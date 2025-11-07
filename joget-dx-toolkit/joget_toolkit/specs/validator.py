"""
Validator for canonical format specifications.

Provides validation utilities beyond Pydantic's built-in validation.
"""

import yaml
from pathlib import Path
from typing import Union, Dict, Any, List
from enum import Enum
from pydantic import ValidationError

from joget_toolkit.specs.schema import AppSpec


class SpecValidator:
    """Validator for canonical format specifications"""

    @staticmethod
    def load_yaml(path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load YAML file and return as dictionary.

        Args:
            path: Path to YAML file

        Returns:
            Dictionary representation of YAML

        Raises:
            FileNotFoundError: If file doesn't exist
            yaml.YAMLError: If YAML is invalid
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    @staticmethod
    def validate_yaml(path: Union[str, Path]) -> AppSpec:
        """
        Load and validate YAML file against canonical schema.

        Args:
            path: Path to YAML file

        Returns:
            Validated AppSpec object

        Raises:
            ValidationError: If validation fails
        """
        data = SpecValidator.load_yaml(path)
        return AppSpec(**data)

    @staticmethod
    def validate_dict(data: Dict[str, Any]) -> AppSpec:
        """
        Validate dictionary against canonical schema.

        Args:
            data: Dictionary representation of spec

        Returns:
            Validated AppSpec object

        Raises:
            ValidationError: If validation fails
        """
        return AppSpec(**data)

    @staticmethod
    def get_validation_errors(data: Dict[str, Any]) -> List[str]:
        """
        Get list of validation errors without raising exception.

        Args:
            data: Dictionary to validate

        Returns:
            List of error messages (empty if valid)
        """
        try:
            AppSpec(**data)
            return []
        except ValidationError as e:
            return [str(err) for err in e.errors()]

    @staticmethod
    def _convert_enums_to_str(obj):
        """Recursively convert enums to strings in nested structures"""
        if isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, dict):
            return {key: SpecValidator._convert_enums_to_str(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [SpecValidator._convert_enums_to_str(item) for item in obj]
        else:
            return obj

    @staticmethod
    def save_yaml(spec: AppSpec, path: Union[str, Path]) -> None:
        """
        Save AppSpec to YAML file.

        Args:
            spec: AppSpec object to save
            path: Output path

        Raises:
            IOError: If file can't be written
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict and handle enums
        data = spec.model_dump(exclude_none=True, by_alias=False)
        data = SpecValidator._convert_enums_to_str(data)

        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
