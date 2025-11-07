"""
Canonical format specifications for forms.

This module defines the canonical YAML format used as the intermediate
representation between different input formats and platform-specific outputs.
"""

from joget_toolkit.specs.schema import (
    AppSpec,
    FormSpec,
    FieldSpec,
    FieldType,
    SelectOption,
    ForeignKeyRef,
    IndexSpec,
)
from joget_toolkit.specs.validator import SpecValidator

__all__ = [
    "AppSpec",
    "FormSpec",
    "FieldSpec",
    "FieldType",
    "SelectOption",
    "ForeignKeyRef",
    "IndexSpec",
    "SpecValidator",
]
