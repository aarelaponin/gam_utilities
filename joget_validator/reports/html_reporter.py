#!/usr/bin/env python3
"""
HTML Reporter
Generates HTML report files for validation results
"""

import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from ..core.models import ValidationReport, ValidationStatus


class HTMLReporter:
    """
    Generates HTML report files for validation results
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize HTML reporter

        Args:
            config: Reporter configuration
        """
        self.config = config or {}
        self.logger = logging.getLogger('joget_validator.html_reporter')

        # Configuration options
        self.output_directory = Path(self.config.get('output_directory', './validation_reports'))
        self.include_passed_fields = self.config.get('include_passed_fields', False)
        self.max_errors_per_form = self.config.get('max_errors_per_form', 10)

    def generate(self, report: ValidationReport, output_path: str = None) -> Path:
        """
        Generate HTML report file

        Args:
            report: Validation report
            output_path: Optional custom output path

        Returns:
            Path to generated HTML file
        """
        # Determine output path
        if output_path:
            html_path = Path(output_path)
        else:
            timestamp = report.validation_time.strftime('%Y%m%d_%H%M%S')
            filename = f'validation_report_{timestamp}.html'
            html_path = self.output_directory / filename

        # Ensure output directory exists
        html_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate HTML content
        html_content = self._generate_html_content(report)

        # Write HTML file
        try:
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            self.logger.info(f"HTML report generated: {html_path}")
            return html_path

        except Exception as e:
            self.logger.error(f"Error generating HTML report: {e}")
            raise

    def _generate_html_content(self, report: ValidationReport) -> str:
        """
        Generate complete HTML content

        Args:
            report: Validation report

        Returns:
            HTML content as string
        """
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Farmers Registry Validation Report</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        {self._generate_header(report)}
        {self._generate_summary(report)}
        {self._generate_farmers_section(report)}
        {self._generate_footer()}
    </div>
    <script>
        {self._get_javascript()}
    </script>
</body>
</html>"""
        return html

    def _get_css_styles(self) -> str:
        """Get CSS styles for the HTML report"""
        return """
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .header {
            text-align: center;
            border-bottom: 3px solid #007acc;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }

        .header h1 {
            color: #333;
            margin: 0;
            font-size: 2.5em;
        }

        .header .subtitle {
            color: #666;
            font-size: 1.1em;
            margin-top: 10px;
        }

        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }

        .summary-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #007acc;
            text-align: center;
        }

        .summary-card h3 {
            margin: 0 0 10px 0;
            color: #333;
        }

        .summary-card .value {
            font-size: 2em;
            font-weight: bold;
            color: #007acc;
        }

        .status-passed { color: #28a745; }
        .status-failed { color: #dc3545; }
        .status-skipped { color: #ffc107; }
        .status-error { color: #fd7e14; }

        .farmer-section {
            margin-bottom: 30px;
        }

        .farmer-card {
            border: 1px solid #ddd;
            border-radius: 6px;
            margin-bottom: 20px;
            overflow: hidden;
        }

        .farmer-header {
            background: #f8f9fa;
            padding: 15px;
            border-bottom: 1px solid #ddd;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .farmer-header:hover {
            background: #e9ecef;
        }

        .farmer-title {
            font-weight: bold;
            font-size: 1.1em;
        }

        .farmer-status {
            padding: 4px 12px;
            border-radius: 4px;
            color: white;
            font-size: 0.9em;
        }

        .farmer-content {
            padding: 20px;
            display: none;
        }

        .farmer-content.expanded {
            display: block;
        }

        .form-section, .grid-section {
            margin-bottom: 25px;
        }

        .form-header, .grid-header {
            background: #e9ecef;
            padding: 10px 15px;
            border-radius: 4px;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .field-list {
            margin-left: 20px;
        }

        .field-item {
            padding: 5px 0;
            border-bottom: 1px solid #f0f0f0;
        }

        .field-item:last-child {
            border-bottom: none;
        }

        .field-name {
            font-weight: bold;
            color: #333;
        }

        .field-error {
            color: #dc3545;
            font-size: 0.9em;
            margin-left: 10px;
        }

        .expand-btn {
            background: #007acc;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 0.8em;
        }

        .expand-btn:hover {
            background: #0056a3;
        }

        .grid-summary {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 10px;
        }

        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 0.9em;
        }

        .toggle-icon {
            transition: transform 0.3s;
        }

        .toggle-icon.expanded {
            transform: rotate(90deg);
        }
        """

    def _get_javascript(self) -> str:
        """Get JavaScript for interactive features"""
        return """
        function toggleFarmer(farmerId) {
            const content = document.getElementById('farmer-content-' + farmerId);
            const icon = document.getElementById('toggle-icon-' + farmerId);

            if (content.classList.contains('expanded')) {
                content.classList.remove('expanded');
                icon.classList.remove('expanded');
            } else {
                content.classList.add('expanded');
                icon.classList.add('expanded');
            }
        }

        function expandAll() {
            const contents = document.querySelectorAll('.farmer-content');
            const icons = document.querySelectorAll('.toggle-icon');

            contents.forEach(content => content.classList.add('expanded'));
            icons.forEach(icon => icon.classList.add('expanded'));
        }

        function collapseAll() {
            const contents = document.querySelectorAll('.farmer-content');
            const icons = document.querySelectorAll('.toggle-icon');

            contents.forEach(content => content.classList.remove('expanded'));
            icons.forEach(icon => icon.classList.remove('expanded'));
        }
        """

    def _generate_header(self, report: ValidationReport) -> str:
        """Generate HTML header section"""
        return f"""
        <div class="header">
            <h1>Farmers Registry Validation Report</h1>
            <div class="subtitle">
                Generated on {report.validation_time.strftime('%Y-%m-%d at %H:%M:%S')} |
                Duration: {report.duration_seconds:.2f} seconds
            </div>
        </div>
        """

    def _generate_summary(self, report: ValidationReport) -> str:
        """Generate summary section"""
        success_rate = (report.passed / report.total_farmers * 100) if report.total_farmers > 0 else 0

        return f"""
        <div class="summary">
            <div class="summary-card">
                <h3>Total Farmers</h3>
                <div class="value">{report.total_farmers}</div>
            </div>
            <div class="summary-card">
                <h3>Passed</h3>
                <div class="value status-passed">{report.passed}</div>
            </div>
            <div class="summary-card">
                <h3>Failed</h3>
                <div class="value status-failed">{report.failed}</div>
            </div>
            <div class="summary-card">
                <h3>Skipped</h3>
                <div class="value status-skipped">{report.skipped}</div>
            </div>
            <div class="summary-card">
                <h3>Success Rate</h3>
                <div class="value">{success_rate:.1f}%</div>
            </div>
        </div>

        <div style="text-align: center; margin-bottom: 30px;">
            <button class="expand-btn" onclick="expandAll()">Expand All</button>
            <button class="expand-btn" onclick="collapseAll()">Collapse All</button>
        </div>
        """

    def _generate_farmers_section(self, report: ValidationReport) -> str:
        """Generate farmers results section"""
        if not report.farmer_results:
            return "<div class='farmer-section'><p>No farmer results to display.</p></div>"

        html = "<div class='farmer-section'>"

        for idx, farmer_result in enumerate(report.farmer_results):
            html += self._generate_farmer_card(farmer_result, idx)

        html += "</div>"
        return html

    def _generate_farmer_card(self, farmer_result, index: int) -> str:
        """Generate HTML for a single farmer card"""
        farmer_id = farmer_result.farmer_id
        status_class = f"status-{farmer_result.status.value.lower()}"

        national_id_display = f" (NID: {farmer_result.national_id})" if farmer_result.national_id else ""

        card_html = f"""
        <div class="farmer-card">
            <div class="farmer-header" onclick="toggleFarmer('{index}')">
                <div>
                    <span class="toggle-icon" id="toggle-icon-{index}">▶</span>
                    <span class="farmer-title">Farmer: {farmer_id}{national_id_display}</span>
                </div>
                <span class="farmer-status {status_class}">{farmer_result.status.value}</span>
            </div>
            <div class="farmer-content" id="farmer-content-{index}">
        """

        # Add form results
        if farmer_result.form_results:
            card_html += "<h4>Forms</h4>"
            for form_name, form_result in farmer_result.form_results.items():
                card_html += self._generate_form_section(form_name, form_result)

        # Add grid results
        if farmer_result.grid_results:
            card_html += "<h4>Grids</h4>"
            for grid_name, grid_result in farmer_result.grid_results.items():
                card_html += self._generate_grid_section(grid_name, grid_result)

        card_html += """
            </div>
        </div>
        """

        return card_html

    def _generate_form_section(self, form_name: str, form_result) -> str:
        """Generate HTML for a form section"""
        status_class = f"status-{form_result.status.value.lower()}"

        html = f"""
        <div class="form-section">
            <div class="form-header">
                <span>{form_name}</span>
                <span class="{status_class}">
                    {form_result.passed_fields}/{form_result.total_fields} passed
                </span>
            </div>
        """

        # Show field results
        if form_result.field_results:
            html += '<div class="field-list">'

            # Show failed fields
            failed_fields = [fr for fr in form_result.field_results if fr.status == ValidationStatus.FAILED]
            shown_errors = 0

            for field_result in failed_fields:
                if shown_errors >= self.max_errors_per_form:
                    remaining = len(failed_fields) - shown_errors
                    html += f'<div class="field-item">... and {remaining} more errors</div>'
                    break

                html += f"""
                <div class="field-item">
                    <span class="field-name status-failed">✗ {field_result.field_name}</span>
                    <span class="field-error">{field_result.error_message or 'Validation failed'}</span>
                </div>
                """
                shown_errors += 1

            # Show passed fields if configured
            if self.include_passed_fields:
                passed_fields = [fr for fr in form_result.field_results if fr.status == ValidationStatus.PASSED]
                for field_result in passed_fields:
                    html += f"""
                    <div class="field-item">
                        <span class="field-name status-passed">✓ {field_result.field_name}</span>
                    </div>
                    """

            html += '</div>'

        html += '</div>'
        return html

    def _generate_grid_section(self, grid_name: str, grid_result) -> str:
        """Generate HTML for a grid section"""
        status_class = f"status-{grid_result.status.value.lower()}"

        html = f"""
        <div class="grid-section">
            <div class="grid-header">
                <span>{grid_name}</span>
                <span class="{status_class}">{grid_result.status.value}</span>
            </div>
            <div class="grid-summary">
                <strong>Rows:</strong> Expected {grid_result.expected_rows}, Found {grid_result.actual_rows}
        """

        if grid_result.expected_rows != grid_result.actual_rows:
            html += ' <span class="status-failed">✗ Count mismatch</span>'
        else:
            html += ' <span class="status-passed">✓ Count matches</span>'

        html += '</div>'

        # Add row validation summary if available
        if grid_result.row_validations:
            failed_rows = sum(1 for rv in grid_result.row_validations
                            if rv.get('status') == ValidationStatus.FAILED.value)
            passed_rows = len(grid_result.row_validations) - failed_rows

            html += f"""
            <div style="margin-left: 20px; font-size: 0.9em;">
                Row validation: {passed_rows} passed, {failed_rows} failed
            </div>
            """

        html += '</div>'
        return html

    def _generate_footer(self) -> str:
        """Generate HTML footer"""
        return f"""
        <div class="footer">
            <p>Generated by Joget Validator v1.0.0 on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        """