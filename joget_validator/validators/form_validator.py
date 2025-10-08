#!/usr/bin/env python3
"""
Form Validator
Validates data in main form tables against test data
"""

import logging
from typing import Dict, Any, Optional, List

from ..core.models import (
    FormValidationResult, FieldValidationResult, ValidationStatus
)
from .field_validator import FieldValidator


class FormValidator:
    """
    Validates data in main form tables
    """

    def __init__(self, validation_config: Dict[str, Any]):
        """
        Initialize form validator

        Args:
            validation_config: Validation configuration settings
        """
        self.config = validation_config
        self.logger = logging.getLogger('joget_validator.form_validator')
        self.field_validator = FieldValidator(validation_config)

        # Get ignore fields from config
        self.ignore_fields = validation_config.get('validation', {}).get('ignore_fields', [])

    def validate(self, test_data: Dict[str, Any], db_data: Optional[Dict[str, Any]],
                mappings: Dict[str, Any], form_name: str) -> FormValidationResult:
        """
        Validate form data against test data

        Args:
            test_data: Test data for the farmer
            db_data: Database data from form table
            mappings: Form configuration and field mappings
            form_name: Name of the form being validated

        Returns:
            Form validation result
        """
        self.logger.debug(f"Validating form {form_name}")

        # Initialize result
        result = FormValidationResult(
            form_name=form_name,
            table_name=mappings.get('table_name', f'app_fd_{form_name}'),
            status=ValidationStatus.PASSED,
            total_fields=0,
            passed_fields=0,
            failed_fields=0
        )

        # Check if database data exists
        if not db_data:
            self.logger.warning(f"No database data found for form {form_name}")
            result.status = ValidationStatus.FAILED
            return result

        # Get field mappings
        field_mappings = mappings.get('mappings', {})
        if not field_mappings:
            self.logger.warning(f"No field mappings found for form {form_name}")
            result.status = ValidationStatus.ERROR
            return result

        # Validate each mapped field
        for field_name, field_config in field_mappings.items():
            # Skip ignored fields
            if field_name in self.ignore_fields:
                continue

            result.total_fields += 1

            try:
                field_result = self._validate_field(
                    field_name=field_name,
                    field_config=field_config,
                    test_data=test_data,
                    db_data=db_data
                )

                result.field_results.append(field_result)

                if field_result.status == ValidationStatus.PASSED:
                    result.passed_fields += 1
                else:
                    result.failed_fields += 1

            except Exception as e:
                self.logger.error(f"Error validating field {field_name}: {e}")
                result.failed_fields += 1
                result.field_results.append(FieldValidationResult(
                    field_name=field_name,
                    joget_column=field_config.get('joget_column', f'c_{field_name}'),
                    expected_value=None,
                    actual_value=None,
                    status=ValidationStatus.ERROR,
                    error_message=str(e)
                ))

        # Determine overall status
        if result.failed_fields > 0:
            result.status = ValidationStatus.FAILED
        elif result.total_fields == 0:
            result.status = ValidationStatus.SKIPPED
        else:
            result.status = ValidationStatus.PASSED

        self.logger.debug(f"Form {form_name} validation: {result.passed_fields}/{result.total_fields} passed")

        return result

    def _validate_field(self, field_name: str, field_config: Dict[str, Any],
                       test_data: Dict[str, Any], db_data: Dict[str, Any]) -> FieldValidationResult:
        """
        Validate a single field

        Args:
            field_name: Name of the field
            field_config: Field configuration from mappings
            test_data: Test data for the farmer
            db_data: Database record data

        Returns:
            Field validation result
        """
        from ..parsers.test_data_parser import TestDataParser

        # Extract configuration
        joget_column = field_config.get('joget_column', f'c_{field_name}')
        json_path = field_config.get('json_path', field_name)
        transform = field_config.get('transform')
        field_type = field_config.get('type', 'string')

        # Get expected value from test data
        test_parser = TestDataParser.__new__(TestDataParser)  # Create instance without file loading
        test_parser.data = {}  # Not needed for extract_value
        expected_value = test_parser.extract_value(test_data, json_path)

        # Apply transformation if specified
        if transform:
            from ..parsers.services_parser import ServicesParser
            services_parser = ServicesParser.__new__(ServicesParser)  # Create instance for transformation
            services_parser.transformations = services_parser._load_transformations(services_parser)
            expected_value = services_parser.apply_transformation(expected_value, transform)

        # Get actual value from database
        actual_value = db_data.get(joget_column)

        # Compare values
        comparison_result = self.field_validator.compare_values(
            expected=expected_value,
            actual=actual_value,
            field_type=field_type
        )

        # Create result
        status = ValidationStatus.PASSED if comparison_result else ValidationStatus.FAILED
        error_message = None if comparison_result else f"Expected '{expected_value}', but found '{actual_value}'"

        return FieldValidationResult(
            field_name=field_name,
            joget_column=joget_column,
            expected_value=expected_value,
            actual_value=actual_value,
            status=status,
            error_message=error_message
        )

    def validate_required_fields(self, test_data: Dict[str, Any], db_data: Dict[str, Any],
                                mappings: Dict[str, Any]) -> List[str]:
        """
        Validate that all required fields are present and not empty

        Args:
            test_data: Test data for the farmer
            db_data: Database record data
            mappings: Form field mappings

        Returns:
            List of missing required fields
        """
        missing_fields = []
        field_mappings = mappings.get('mappings', {})

        for field_name, field_config in field_mappings.items():
            if field_config.get('required', False):
                joget_column = field_config.get('joget_column', f'c_{field_name}')
                value = db_data.get(joget_column)

                if value is None or value == '':
                    missing_fields.append(field_name)

        return missing_fields

    def get_field_summary(self, result: FormValidationResult) -> Dict[str, Any]:
        """
        Get summary of field validation results

        Args:
            result: Form validation result

        Returns:
            Summary dictionary
        """
        summary = {
            'total_fields': result.total_fields,
            'passed_fields': result.passed_fields,
            'failed_fields': result.failed_fields,
            'success_rate': 0.0,
            'failed_field_names': [],
            'error_messages': []
        }

        if result.total_fields > 0:
            summary['success_rate'] = (result.passed_fields / result.total_fields) * 100

        for field_result in result.field_results:
            if field_result.status == ValidationStatus.FAILED:
                summary['failed_field_names'].append(field_result.field_name)
                if field_result.error_message:
                    summary['error_messages'].append({
                        'field': field_result.field_name,
                        'message': field_result.error_message
                    })

        return summary

    def format_field_errors(self, result: FormValidationResult, max_errors: int = 10) -> List[str]:
        """
        Format field validation errors for display

        Args:
            result: Form validation result
            max_errors: Maximum number of errors to include

        Returns:
            List of formatted error messages
        """
        errors = []
        error_count = 0

        for field_result in result.field_results:
            if field_result.status == ValidationStatus.FAILED and error_count < max_errors:
                error_msg = f"✗ {field_result.field_name}: {field_result.error_message}"
                errors.append(error_msg)
                error_count += 1

        if error_count >= max_errors and result.failed_fields > max_errors:
            remaining = result.failed_fields - max_errors
            errors.append(f"... and {remaining} more errors")

        return errors