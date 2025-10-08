#!/usr/bin/env python3
"""
Data models for validation results
Core data classes as specified in the validation specification
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime


class ValidationStatus(Enum):
    """Validation status enumeration"""
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"


@dataclass
class FieldValidationResult:
    """Result of validating a single field"""
    field_name: str
    joget_column: str
    expected_value: Any
    actual_value: Any
    status: ValidationStatus
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'field_name': self.field_name,
            'joget_column': self.joget_column,
            'expected_value': self.expected_value,
            'actual_value': self.actual_value,
            'status': self.status.value,
            'error_message': self.error_message
        }


@dataclass
class FormValidationResult:
    """Result of validating a form"""
    form_name: str
    table_name: str
    status: ValidationStatus
    total_fields: int
    passed_fields: int
    failed_fields: int
    field_results: List[FieldValidationResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'form_name': self.form_name,
            'table_name': self.table_name,
            'status': self.status.value,
            'total_fields': self.total_fields,
            'passed_fields': self.passed_fields,
            'failed_fields': self.failed_fields,
            'field_results': [fr.to_dict() for fr in self.field_results]
        }


@dataclass
class GridValidationResult:
    """Result of validating a grid"""
    grid_name: str
    table_name: str
    status: ValidationStatus
    expected_rows: int
    actual_rows: int
    row_validations: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'grid_name': self.grid_name,
            'table_name': self.table_name,
            'status': self.status.value,
            'expected_rows': self.expected_rows,
            'actual_rows': self.actual_rows,
            'row_validations': self.row_validations
        }


@dataclass
class FarmerValidationResult:
    """Result of validating a single farmer"""
    farmer_id: str
    national_id: Optional[str]
    status: ValidationStatus
    form_results: Dict[str, FormValidationResult] = field(default_factory=dict)
    grid_results: Dict[str, GridValidationResult] = field(default_factory=dict)
    validation_time: Optional[datetime] = None
    duration_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'farmer_id': self.farmer_id,
            'national_id': self.national_id,
            'status': self.status.value,
            'form_results': {name: result.to_dict() for name, result in self.form_results.items()},
            'grid_results': {name: result.to_dict() for name, result in self.grid_results.items()},
            'validation_time': self.validation_time.isoformat() if self.validation_time else None,
            'duration_seconds': self.duration_seconds
        }


@dataclass
class ValidationReport:
    """Complete validation report"""
    total_farmers: int
    passed: int
    failed: int
    skipped: int
    validation_time: datetime
    duration_seconds: float
    farmer_results: List[FarmerValidationResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'validation_report': {
                'metadata': {
                    'validation_time': self.validation_time.isoformat(),
                    'duration_seconds': self.duration_seconds,
                    'tool_version': '1.0.0'
                },
                'summary': {
                    'total_farmers': self.total_farmers,
                    'passed': self.passed,
                    'failed': self.failed,
                    'skipped': self.skipped
                },
                'results': [result.to_dict() for result in self.farmer_results]
            }
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics"""
        return {
            'total_farmers': self.total_farmers,
            'passed': self.passed,
            'failed': self.failed,
            'skipped': self.skipped,
            'success_rate': (self.passed / self.total_farmers * 100) if self.total_farmers > 0 else 0,
            'duration_seconds': self.duration_seconds
        }