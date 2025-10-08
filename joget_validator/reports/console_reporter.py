#!/usr/bin/env python3
"""
Console Reporter
Generates console output for validation results
"""

import logging
from typing import Dict, Any, List

from ..core.models import ValidationReport, ValidationStatus


class ConsoleReporter:
    """
    Generates formatted console output for validation results
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize console reporter

        Args:
            config: Reporter configuration
        """
        self.config = config or {}
        self.logger = logging.getLogger('joget_validator.console_reporter')

        # Configuration options
        self.include_passed_fields = self.config.get('include_passed_fields', False)
        self.max_errors_per_form = self.config.get('max_errors_per_form', 10)
        self.verbose = self.config.get('verbose', False)

    def generate(self, report: ValidationReport) -> None:
        """
        Print formatted report to console

        Args:
            report: Validation report to display
        """
        self._print_header(report)
        self._print_summary(report)

        if report.farmer_results:
            self._print_detailed_results(report)

        self._print_footer()

    def _print_header(self, report: ValidationReport) -> None:
        """Print report header"""
        print("=" * 60)
        print("Farmers Registry Database Validation Report")
        print("=" * 60)
        print(f"Validation Time: {report.validation_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {report.duration_seconds:.2f} seconds")
        print()

    def _print_summary(self, report: ValidationReport) -> None:
        """Print validation summary"""
        print("Summary:")
        print("--------")
        print(f"Total Farmers: {report.total_farmers}")
        print(f"✓ Passed: {report.passed}")
        print(f"✗ Failed: {report.failed}")
        print(f"⊘ Skipped: {report.skipped}")

        if report.total_farmers > 0:
            success_rate = (report.passed / report.total_farmers) * 100
            print(f"Success Rate: {success_rate:.1f}%")

        print()

    def _print_detailed_results(self, report: ValidationReport) -> None:
        """Print detailed results for each farmer"""
        print("Detailed Results:")
        print("-" * 40)

        for farmer_result in report.farmer_results:
            self._print_farmer_result(farmer_result)

    def _print_farmer_result(self, farmer_result) -> None:
        """Print results for a single farmer"""
        status_icon = self._get_status_icon(farmer_result.status)
        farmer_display = f"Farmer: {farmer_result.farmer_id}"

        if farmer_result.national_id:
            farmer_display += f" (NID: {farmer_result.national_id})"

        farmer_display += f" [{farmer_result.status.value}]"

        print(f"\n{farmer_display}")

        # Print form results
        if farmer_result.form_results:
            for form_name, form_result in farmer_result.form_results.items():
                self._print_form_result(form_name, form_result)

        # Print grid results
        if farmer_result.grid_results:
            for grid_name, grid_result in farmer_result.grid_results.items():
                self._print_grid_result(grid_name, grid_result)

    def _print_form_result(self, form_name: str, form_result) -> None:
        """Print results for a single form"""
        status_icon = self._get_status_icon(form_result.status)
        print(f"\n  Form: {form_name} [{form_result.status.value}]")

        if form_result.status == ValidationStatus.PASSED:
            print(f"    ✓ All {form_result.total_fields} fields validated successfully")
        elif form_result.status == ValidationStatus.FAILED:
            print(f"    {form_result.passed_fields}/{form_result.total_fields} fields passed")

            # Show failed fields
            failed_fields = [fr for fr in form_result.field_results if fr.status == ValidationStatus.FAILED]
            errors_shown = 0

            for field_result in failed_fields:
                if errors_shown >= self.max_errors_per_form:
                    remaining = len(failed_fields) - errors_shown
                    print(f"    ... and {remaining} more errors")
                    break

                print(f"    ✗ {field_result.field_name}: {field_result.error_message}")
                errors_shown += 1

        # Show passed fields if configured
        if self.include_passed_fields and form_result.field_results:
            passed_fields = [fr for fr in form_result.field_results if fr.status == ValidationStatus.PASSED]
            for field_result in passed_fields:
                print(f"    ✓ {field_result.field_name}: OK")

    def _print_grid_result(self, grid_name: str, grid_result) -> None:
        """Print results for a single grid"""
        status_icon = self._get_status_icon(grid_result.status)
        print(f"\n  Grid: {grid_name} [{grid_result.status.value}]")

        # Show row count comparison
        if grid_result.expected_rows != grid_result.actual_rows:
            print(f"    ✗ Row count mismatch: Expected {grid_result.expected_rows}, Found {grid_result.actual_rows}")
        else:
            print(f"    ✓ Row count: {grid_result.actual_rows}")

        # Show row validation details if verbose
        if self.verbose and grid_result.row_validations:
            for idx, row_validation in enumerate(grid_result.row_validations):
                row_status = row_validation.get('status', 'UNKNOWN')
                if row_status == ValidationStatus.FAILED.value:
                    print(f"    ✗ Row {idx + 1}: {len(row_validation.get('errors', []))} errors")

                    # Show field errors for this row
                    field_results = row_validation.get('field_results', [])
                    for field_result in field_results:
                        if field_result.get('status') == ValidationStatus.FAILED.value:
                            error_msg = field_result.get('error_message', 'Validation failed')
                            print(f"      ✗ {field_result['field_name']}: {error_msg}")
                elif row_status == ValidationStatus.PASSED.value:
                    field_count = len(row_validation.get('field_results', []))
                    print(f"    ✓ Row {idx + 1}: {field_count} fields validated")

    def _print_footer(self) -> None:
        """Print report footer"""
        print("\n" + "=" * 60)

    def _get_status_icon(self, status: ValidationStatus) -> str:
        """Get icon for validation status"""
        icons = {
            ValidationStatus.PASSED: "✓",
            ValidationStatus.FAILED: "✗",
            ValidationStatus.SKIPPED: "⊘",
            ValidationStatus.ERROR: "⚠"
        }
        return icons.get(status, "?")

    def print_farmer_summary(self, farmer_result) -> None:
        """
        Print summary for a single farmer (useful for single farmer validation)

        Args:
            farmer_result: Single farmer validation result
        """
        print("=" * 50)
        print("Single Farmer Validation Result")
        print("=" * 50)

        self._print_farmer_result(farmer_result)

        # Print summary statistics
        print(f"\nValidation Summary:")
        print(f"Duration: {farmer_result.duration_seconds:.2f} seconds")

        total_forms = len(farmer_result.form_results)
        passed_forms = sum(1 for fr in farmer_result.form_results.values()
                          if fr.status == ValidationStatus.PASSED)

        total_grids = len(farmer_result.grid_results)
        passed_grids = sum(1 for gr in farmer_result.grid_results.values()
                          if gr.status == ValidationStatus.PASSED)

        print(f"Forms: {passed_forms}/{total_forms} passed")
        print(f"Grids: {passed_grids}/{total_grids} passed")

        print("=" * 50)

    def print_connection_test_results(self, results: Dict[str, bool]) -> None:
        """
        Print connection test results

        Args:
            results: Dictionary with test results
        """
        print("=" * 40)
        print("Connection Test Results")
        print("=" * 40)

        for component, success in results.items():
            icon = "✓" if success else "✗"
            status = "OK" if success else "FAILED"
            print(f"{icon} {component.replace('_', ' ').title()}: {status}")

        print("=" * 40)

    def print_validation_progress(self, current: int, total: int, farmer_id: str = None) -> None:
        """
        Print validation progress (for real-time feedback)

        Args:
            current: Current farmer number
            total: Total number of farmers
            farmer_id: ID of current farmer being validated
        """
        progress = (current / total) * 100 if total > 0 else 0
        farmer_info = f" (Farmer: {farmer_id})" if farmer_id else ""
        print(f"Progress: {current}/{total} ({progress:.1f}%){farmer_info}", end='\r', flush=True)

        # Print newline when complete
        if current == total:
            print()  # Move to next line when done