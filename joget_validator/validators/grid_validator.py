#!/usr/bin/env python3
"""
Grid Validator
Validates data in grid/sub-form tables against test data
"""

import logging
from typing import Dict, Any, List, Optional

from ..core.models import GridValidationResult, ValidationStatus
from .field_validator import FieldValidator


class GridValidator:
    """
    Validates data in grid/sub-form tables
    """

    def __init__(self, validation_config: Dict[str, Any]):
        """
        Initialize grid validator

        Args:
            validation_config: Validation configuration settings
        """
        self.config = validation_config
        self.logger = logging.getLogger('joget_validator.grid_validator')
        self.field_validator = FieldValidator(validation_config)

        # Get ignore fields from config
        self.ignore_fields = validation_config.get('validation', {}).get('ignore_fields', [])

    def validate(self, test_data: Dict[str, Any], db_data: List[Dict[str, Any]],
                mappings: Dict[str, Any], grid_name: str) -> GridValidationResult:
        """
        Validate grid data against test data

        Args:
            test_data: Test data for the farmer (contains grid data)
            db_data: Database data from grid table (list of records)
            mappings: Grid configuration and field mappings
            grid_name: Name of the grid being validated

        Returns:
            Grid validation result
        """
        self.logger.debug(f"Validating grid {grid_name}")

        # Extract grid data from test data
        test_grid_data = self._extract_grid_data(test_data, grid_name, mappings)

        # Initialize result
        result = GridValidationResult(
            grid_name=grid_name,
            table_name=mappings.get('table_name', f'app_fd_{grid_name}'),
            status=ValidationStatus.PASSED,
            expected_rows=len(test_grid_data),
            actual_rows=len(db_data) if db_data else 0
        )

        # Validate row count
        if not self._validate_row_count(result.expected_rows, result.actual_rows):
            result.status = ValidationStatus.FAILED
            self.logger.warning(f"Row count mismatch for grid {grid_name}: expected {result.expected_rows}, got {result.actual_rows}")

        # If no data to validate
        if not test_grid_data and not db_data:
            result.status = ValidationStatus.PASSED
            return result

        if not test_grid_data:
            if db_data:
                result.status = ValidationStatus.FAILED
            return result

        # Validate each row
        row_validations = []

        # Match rows based on order or key fields
        matched_pairs = self._match_rows(test_grid_data, db_data, mappings)

        for idx, (test_row, db_row) in enumerate(matched_pairs):
            row_validation = self._validate_row(
                test_row=test_row,
                db_row=db_row,
                mappings=mappings,
                row_index=idx
            )
            row_validations.append(row_validation)

            # Update overall status if any row fails
            if row_validation.get('status') == ValidationStatus.FAILED.value:
                result.status = ValidationStatus.FAILED

        result.row_validations = row_validations

        self.logger.debug(f"Grid {grid_name} validation: {len(row_validations)} rows processed")

        return result

    def _extract_grid_data(self, test_data: Dict[str, Any], grid_name: str,
                          mappings: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract grid data from test data

        Args:
            test_data: Test data for the farmer
            grid_name: Name of the grid
            mappings: Grid mappings configuration

        Returns:
            List of grid row data
        """
        from ..parsers.test_data_parser import TestDataParser

        # Create parser instance for data extraction
        test_parser = TestDataParser.__new__(TestDataParser)
        test_parser.data = {}

        # Try different possible paths for grid data
        possible_paths = [
            grid_name,
            f"{grid_name}Data",
            f"{grid_name}_data",
            f"grids.{grid_name}",
            f"subforms.{grid_name}"
        ]

        # Also check if there's a specific path defined in mappings
        grid_path = mappings.get('config', {}).get('data_path')
        if grid_path:
            possible_paths.insert(0, grid_path)

        for path in possible_paths:
            grid_data = test_parser.extract_value(test_data, path)
            if grid_data:
                if isinstance(grid_data, list):
                    return grid_data
                elif isinstance(grid_data, dict):
                    # Single item, return as list
                    return [grid_data]

        # If no specific grid data found, return empty list
        self.logger.debug(f"No grid data found for {grid_name} in test data")
        return []

    def _validate_row_count(self, expected: int, actual: int) -> bool:
        """
        Check if row counts match

        Args:
            expected: Expected number of rows
            actual: Actual number of rows

        Returns:
            True if counts match
        """
        return expected == actual

    def _match_rows(self, test_rows: List[Dict[str, Any]], db_rows: List[Dict[str, Any]],
                   mappings: Dict[str, Any]) -> List[tuple]:
        """
        Match test data rows with database rows

        Args:
            test_rows: List of test data rows
            db_rows: List of database rows
            mappings: Grid mappings configuration

        Returns:
            List of (test_row, db_row) tuples
        """
        matched_pairs = []

        # Get key fields for matching if specified
        key_fields = mappings.get('config', {}).get('key_fields', [])

        if key_fields:
            # Match by key fields
            matched_pairs = self._match_by_keys(test_rows, db_rows, key_fields, mappings)
        else:
            # Match by order/index
            max_rows = max(len(test_rows), len(db_rows))
            for i in range(max_rows):
                test_row = test_rows[i] if i < len(test_rows) else None
                db_row = db_rows[i] if i < len(db_rows) else None
                matched_pairs.append((test_row, db_row))

        return matched_pairs

    def _match_by_keys(self, test_rows: List[Dict[str, Any]], db_rows: List[Dict[str, Any]],
                      key_fields: List[str], mappings: Dict[str, Any]) -> List[tuple]:
        """
        Match rows by key fields

        Args:
            test_rows: List of test data rows
            db_rows: List of database rows
            key_fields: List of key field names for matching
            mappings: Grid mappings configuration

        Returns:
            List of (test_row, db_row) tuples
        """
        from ..parsers.test_data_parser import TestDataParser

        matched_pairs = []
        test_parser = TestDataParser.__new__(TestDataParser)
        test_parser.data = {}

        # Create index of database rows by key values
        db_index = {}
        field_mappings = mappings.get('mappings', {})

        for db_row in db_rows:
            key_values = []
            for key_field in key_fields:
                if key_field in field_mappings:
                    joget_column = field_mappings[key_field].get('joget_column', f'c_{key_field}')
                    key_values.append(str(db_row.get(joget_column, '')))
                else:
                    key_values.append(str(db_row.get(f'c_{key_field}', '')))

            key = '|'.join(key_values)
            db_index[key] = db_row

        # Match test rows with database rows
        for test_row in test_rows:
            key_values = []
            for key_field in key_fields:
                if key_field in field_mappings:
                    json_path = field_mappings[key_field].get('json_path', key_field)
                    value = test_parser.extract_value(test_row, json_path)
                    key_values.append(str(value) if value is not None else '')
                else:
                    value = test_parser.extract_value(test_row, key_field)
                    key_values.append(str(value) if value is not None else '')

            key = '|'.join(key_values)
            db_row = db_index.get(key)
            matched_pairs.append((test_row, db_row))

        # Add unmatched database rows
        matched_db_rows = {id(pair[1]) for pair in matched_pairs if pair[1] is not None}
        for db_row in db_rows:
            if id(db_row) not in matched_db_rows:
                matched_pairs.append((None, db_row))

        return matched_pairs

    def _validate_row(self, test_row: Optional[Dict[str, Any]], db_row: Optional[Dict[str, Any]],
                     mappings: Dict[str, Any], row_index: int) -> Dict[str, Any]:
        """
        Validate a single grid row

        Args:
            test_row: Test data row
            db_row: Database row
            mappings: Grid mappings configuration
            row_index: Index of the row

        Returns:
            Row validation result dictionary
        """
        row_result = {
            'row_index': row_index,
            'status': ValidationStatus.PASSED.value,
            'field_results': [],
            'errors': []
        }

        # Check for missing rows
        if test_row is None and db_row is not None:
            row_result['status'] = ValidationStatus.FAILED.value
            row_result['errors'].append("Unexpected database row")
            return row_result

        if test_row is not None and db_row is None:
            row_result['status'] = ValidationStatus.FAILED.value
            row_result['errors'].append("Missing database row")
            return row_result

        if test_row is None and db_row is None:
            return row_result

        # Validate fields in the row
        field_mappings = mappings.get('mappings', {})

        for field_name, field_config in field_mappings.items():
            # Skip ignored fields
            if field_name in self.ignore_fields:
                continue

            try:
                field_result = self._validate_row_field(
                    field_name=field_name,
                    field_config=field_config,
                    test_row=test_row,
                    db_row=db_row
                )

                row_result['field_results'].append(field_result)

                if field_result['status'] == ValidationStatus.FAILED.value:
                    row_result['status'] = ValidationStatus.FAILED.value

            except Exception as e:
                self.logger.error(f"Error validating field {field_name} in row {row_index}: {e}")
                row_result['status'] = ValidationStatus.FAILED.value
                row_result['errors'].append(f"Field {field_name}: {str(e)}")

        return row_result

    def _validate_row_field(self, field_name: str, field_config: Dict[str, Any],
                           test_row: Dict[str, Any], db_row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a single field in a grid row

        Args:
            field_name: Name of the field
            field_config: Field configuration from mappings
            test_row: Test data row
            db_row: Database row

        Returns:
            Field validation result dictionary
        """
        from ..parsers.test_data_parser import TestDataParser

        # Extract configuration
        joget_column = field_config.get('joget_column', f'c_{field_name}')
        json_path = field_config.get('json_path', field_name)
        transform = field_config.get('transform')
        field_type = field_config.get('type', 'string')

        # Get expected value from test data
        test_parser = TestDataParser.__new__(TestDataParser)
        test_parser.data = {}
        expected_value = test_parser.extract_value(test_row, json_path)

        # Apply transformation if specified
        if transform:
            expected_value = self.field_validator.apply_transformation(expected_value, transform)

        # Get actual value from database
        actual_value = db_row.get(joget_column)

        # Compare values
        comparison_result = self.field_validator._compare_values_impl(
            expected_value, actual_value, field_type
        )

        # Create result
        result = {
            'field_name': field_name,
            'joget_column': joget_column,
            'expected_value': expected_value,
            'actual_value': actual_value,
            'status': ValidationStatus.PASSED.value if comparison_result else ValidationStatus.FAILED.value
        }

        if not comparison_result:
            result['error_message'] = f"Expected '{expected_value}', but found '{actual_value}'"

        return result

    def get_grid_summary(self, result: GridValidationResult) -> Dict[str, Any]:
        """
        Get summary of grid validation results

        Args:
            result: Grid validation result

        Returns:
            Summary dictionary
        """
        summary = {
            'grid_name': result.grid_name,
            'expected_rows': result.expected_rows,
            'actual_rows': result.actual_rows,
            'row_count_match': result.expected_rows == result.actual_rows,
            'validated_rows': len(result.row_validations),
            'passed_rows': 0,
            'failed_rows': 0,
            'total_fields_validated': 0,
            'failed_fields': 0
        }

        for row_validation in result.row_validations:
            if row_validation.get('status') == ValidationStatus.PASSED.value:
                summary['passed_rows'] += 1
            else:
                summary['failed_rows'] += 1

            # Count field validations
            field_results = row_validation.get('field_results', [])
            summary['total_fields_validated'] += len(field_results)

            for field_result in field_results:
                if field_result.get('status') == ValidationStatus.FAILED.value:
                    summary['failed_fields'] += 1

        return summary