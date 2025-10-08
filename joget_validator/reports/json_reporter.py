#!/usr/bin/env python3
"""
JSON Reporter
Generates JSON report files for validation results
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

from ..core.models import ValidationReport


class JSONReporter:
    """
    Generates JSON report files for validation results
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize JSON reporter

        Args:
            config: Reporter configuration
        """
        self.config = config or {}
        self.logger = logging.getLogger('joget_validator.json_reporter')

        # Configuration options
        self.output_directory = Path(self.config.get('output_directory', './validation_reports'))
        self.include_passed_fields = self.config.get('include_passed_fields', False)
        self.pretty_print = self.config.get('pretty_print', True)

    def generate(self, report: ValidationReport, output_path: str = None) -> Path:
        """
        Generate JSON report file

        Args:
            report: Validation report
            output_path: Optional custom output path

        Returns:
            Path to generated JSON file
        """
        # Determine output path
        if output_path:
            json_path = Path(output_path)
        else:
            timestamp = report.validation_time.strftime('%Y%m%d_%H%M%S')
            filename = f'validation_report_{timestamp}.json'
            json_path = self.output_directory / filename

        # Ensure output directory exists
        json_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert report to dictionary
        report_data = self._prepare_report_data(report)

        # Write JSON file
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                if self.pretty_print:
                    json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
                else:
                    json.dump(report_data, f, ensure_ascii=False, default=str)

            self.logger.info(f"JSON report generated: {json_path}")
            return json_path

        except Exception as e:
            self.logger.error(f"Error generating JSON report: {e}")
            raise

    def _prepare_report_data(self, report: ValidationReport) -> Dict[str, Any]:
        """
        Prepare report data for JSON serialization

        Args:
            report: Validation report

        Returns:
            Dictionary suitable for JSON serialization
        """
        # Convert report to dict
        report_dict = report.to_dict()

        # Filter out passed fields if not configured to include them
        if not self.include_passed_fields:
            self._filter_passed_fields(report_dict)

        # Add additional metadata
        report_dict['validation_report']['metadata']['generator'] = 'joget_validator'
        report_dict['validation_report']['metadata']['format_version'] = '1.0'

        return report_dict

    def _filter_passed_fields(self, report_dict: Dict[str, Any]) -> None:
        """
        Remove passed field results from the report to reduce size

        Args:
            report_dict: Report dictionary to filter
        """
        results = report_dict.get('validation_report', {}).get('results', [])

        for farmer_result in results:
            # Filter form field results
            form_results = farmer_result.get('form_results', {})
            for form_name, form_result in form_results.items():
                if 'field_results' in form_result:
                    # Keep only failed fields
                    form_result['field_results'] = [
                        fr for fr in form_result['field_results']
                        if fr.get('status') != 'PASSED'
                    ]

            # Filter grid field results
            grid_results = farmer_result.get('grid_results', {})
            for grid_name, grid_result in grid_results.items():
                if 'row_validations' in grid_result:
                    for row_validation in grid_result['row_validations']:
                        if 'field_results' in row_validation:
                            # Keep only failed fields
                            row_validation['field_results'] = [
                                fr for fr in row_validation['field_results']
                                if fr.get('status') != 'PASSED'
                            ]

    def generate_summary_json(self, report: ValidationReport, output_path: str = None) -> Path:
        """
        Generate a summary-only JSON report (without detailed field results)

        Args:
            report: Validation report
            output_path: Optional custom output path

        Returns:
            Path to generated summary JSON file
        """
        # Determine output path
        if output_path:
            json_path = Path(output_path)
        else:
            timestamp = report.validation_time.strftime('%Y%m%d_%H%M%S')
            filename = f'validation_summary_{timestamp}.json'
            json_path = self.output_directory / filename

        # Ensure output directory exists
        json_path.parent.mkdir(parents=True, exist_ok=True)

        # Create summary data
        summary_data = {
            'validation_summary': {
                'metadata': {
                    'validation_time': report.validation_time.isoformat(),
                    'duration_seconds': report.duration_seconds,
                    'tool_version': '1.0.0',
                    'generator': 'joget_validator',
                    'format_version': '1.0'
                },
                'summary': {
                    'total_farmers': report.total_farmers,
                    'passed': report.passed,
                    'failed': report.failed,
                    'skipped': report.skipped,
                    'success_rate': (report.passed / report.total_farmers * 100) if report.total_farmers > 0 else 0
                },
                'farmer_results': []
            }
        }

        # Add farmer-level summaries
        for farmer_result in report.farmer_results:
            farmer_summary = {
                'farmer_id': farmer_result.farmer_id,
                'national_id': farmer_result.national_id,
                'status': farmer_result.status.value,
                'duration_seconds': farmer_result.duration_seconds,
                'forms_summary': {},
                'grids_summary': {}
            }

            # Add form summaries
            for form_name, form_result in farmer_result.form_results.items():
                farmer_summary['forms_summary'][form_name] = {
                    'status': form_result.status.value,
                    'total_fields': form_result.total_fields,
                    'passed_fields': form_result.passed_fields,
                    'failed_fields': form_result.failed_fields
                }

            # Add grid summaries
            for grid_name, grid_result in farmer_result.grid_results.items():
                farmer_summary['grids_summary'][grid_name] = {
                    'status': grid_result.status.value,
                    'expected_rows': grid_result.expected_rows,
                    'actual_rows': grid_result.actual_rows,
                    'row_count_match': grid_result.expected_rows == grid_result.actual_rows
                }

            summary_data['validation_summary']['farmer_results'].append(farmer_summary)

        # Write summary JSON file
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                if self.pretty_print:
                    json.dump(summary_data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(summary_data, f, ensure_ascii=False)

            self.logger.info(f"JSON summary report generated: {json_path}")
            return json_path

        except Exception as e:
            self.logger.error(f"Error generating JSON summary report: {e}")
            raise

    def generate_farmer_json(self, farmer_result, output_path: str = None) -> Path:
        """
        Generate JSON report for a single farmer

        Args:
            farmer_result: Single farmer validation result
            output_path: Optional custom output path

        Returns:
            Path to generated JSON file
        """
        # Determine output path
        if output_path:
            json_path = Path(output_path)
        else:
            filename = f'farmer_{farmer_result.farmer_id}_validation.json'
            json_path = self.output_directory / filename

        # Ensure output directory exists
        json_path.parent.mkdir(parents=True, exist_ok=True)

        # Create farmer report data
        farmer_data = {
            'farmer_validation': {
                'metadata': {
                    'validation_time': farmer_result.validation_time.isoformat(),
                    'duration_seconds': farmer_result.duration_seconds,
                    'tool_version': '1.0.0',
                    'generator': 'joget_validator'
                },
                'farmer': farmer_result.to_dict()
            }
        }

        # Write JSON file
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                if self.pretty_print:
                    json.dump(farmer_data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(farmer_data, f, ensure_ascii=False)

            self.logger.info(f"Farmer JSON report generated: {json_path}")
            return json_path

        except Exception as e:
            self.logger.error(f"Error generating farmer JSON report: {e}")
            raise

    def load_report(self, json_path: str) -> Dict[str, Any]:
        """
        Load validation report from JSON file

        Args:
            json_path: Path to JSON report file

        Returns:
            Loaded report data
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            self.logger.error(f"Error loading JSON report: {e}")
            raise