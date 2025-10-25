#!/usr/bin/env python3
"""
Form Comparator
Compares local form definitions with deployed forms in Joget instance.

SINGLE RESPONSIBILITY: Diff local JSON vs remote forms
Does NOT: Create forms, fix issues, or deploy

Critical checks for Pattern 2 forms:
- SelectBox vs TextField for FK fields
- Missing FK fields
- FormOptionsBinder configuration
- Parent form references
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging


class DifferenceType(Enum):
    """Types of differences between forms"""
    MISSING_FORM = "missing_form"  # Form doesn't exist in Joget
    MISSING_FIELD = "missing_field"  # Field in local but not in remote
    EXTRA_FIELD = "extra_field"  # Field in remote but not in local
    FIELD_TYPE_MISMATCH = "field_type_mismatch"  # TextField vs SelectBox
    MISSING_FK_FIELD = "missing_fk_field"  # Critical: FK field missing
    WRONG_FIELD_TYPE = "wrong_field_type"  # Critical: TextField instead of SelectBox
    BINDER_MISMATCH = "binder_mismatch"  # FormOptionsBinder configuration wrong
    MISSING_VALIDATOR = "missing_validator"  # DuplicateValueValidator missing on PK


@dataclass
class FieldDifference:
    """Difference in a single field"""
    field_id: str
    difference_type: DifferenceType
    local_value: Optional[Any]
    remote_value: Optional[Any]
    severity: str  # 'critical', 'warning', 'info'
    message: str


@dataclass
class FormComparison:
    """Comparison result for a single form"""
    form_id: str
    exists_in_joget: bool
    has_differences: bool
    differences: List[FieldDifference]
    critical_count: int
    warning_count: int
    info_count: int


class FormComparator:
    """
    Compare local form definitions with Joget instance.

    Performs deep comparison of form structure, focusing on
    fields critical for nested LOV functionality.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize form comparator.

        Args:
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger('joget_utility.form_comparator')

    def compare_forms(self,
                     local_form_path: Path,
                     remote_form_json: Optional[Dict[str, Any]]) -> FormComparison:
        """
        Compare local form definition with remote Joget form.

        Args:
            local_form_path: Path to local form JSON file
            remote_form_json: Remote form definition (from Joget), or None if doesn't exist

        Returns:
            FormComparison object
        """
        # Load local form
        with open(local_form_path, 'r') as f:
            local_form = json.load(f)

        form_id = local_form.get('properties', {}).get('id', local_form_path.stem)

        # Check if form exists
        if remote_form_json is None:
            return FormComparison(
                form_id=form_id,
                exists_in_joget=False,
                has_differences=True,
                differences=[
                    FieldDifference(
                        field_id=form_id,
                        difference_type=DifferenceType.MISSING_FORM,
                        local_value=form_id,
                        remote_value=None,
                        severity='critical',
                        message=f"Form '{form_id}' does not exist in Joget"
                    )
                ],
                critical_count=1,
                warning_count=0,
                info_count=0
            )

        # Extract fields from both forms
        local_fields = self._extract_fields(local_form)
        remote_fields = self._extract_fields(remote_form_json)

        # Compare fields
        differences = []

        # Check local fields against remote
        for field_id, local_field in local_fields.items():
            if field_id not in remote_fields:
                differences.append(FieldDifference(
                    field_id=field_id,
                    difference_type=DifferenceType.MISSING_FIELD,
                    local_value=local_field.get('className'),
                    remote_value=None,
                    severity='warning',
                    message=f"Field '{field_id}' exists in local but not in remote"
                ))
            else:
                # Compare field details
                remote_field = remote_fields[field_id]
                field_diffs = self._compare_field_details(field_id, local_field, remote_field)
                differences.extend(field_diffs)

        # Check for extra fields in remote
        for field_id, remote_field in remote_fields.items():
            if field_id not in local_fields:
                differences.append(FieldDifference(
                    field_id=field_id,
                    difference_type=DifferenceType.EXTRA_FIELD,
                    local_value=None,
                    remote_value=remote_field.get('className'),
                    severity='info',
                    message=f"Field '{field_id}' exists in remote but not in local"
                ))

        # Count by severity
        critical_count = len([d for d in differences if d.severity == 'critical'])
        warning_count = len([d for d in differences if d.severity == 'warning'])
        info_count = len([d for d in differences if d.severity == 'info'])

        return FormComparison(
            form_id=form_id,
            exists_in_joget=True,
            has_differences=len(differences) > 0,
            differences=differences,
            critical_count=critical_count,
            warning_count=warning_count,
            info_count=info_count
        )

    def _extract_fields(self, form_json: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Extract all fields from form JSON.

        Returns:
            Dictionary mapping field_id to field definition
        """
        fields = {}

        def traverse_elements(elements):
            if not isinstance(elements, list):
                return

            for element in elements:
                if not isinstance(element, dict):
                    continue

                # Check if this is a field element
                properties = element.get('properties', {})
                field_id = properties.get('id')

                if field_id:
                    fields[field_id] = element

                # Recursively check child elements
                child_elements = element.get('elements')
                if child_elements:
                    traverse_elements(child_elements)

        # Start traversal
        elements = form_json.get('elements', [])
        traverse_elements(elements)

        return fields

    def _compare_field_details(self,
                               field_id: str,
                               local_field: Dict[str, Any],
                               remote_field: Dict[str, Any]) -> List[FieldDifference]:
        """
        Compare details of a specific field.

        Critical checks for Pattern 2:
        - Field ending with '_code' should be SelectBox, not TextField
        - SelectBox should have FormOptionsBinder
        - PK field should have DuplicateValueValidator
        """
        differences = []

        local_class = local_field.get('className', '')
        remote_class = remote_field.get('className', '')

        # Check 1: Field type mismatch
        if local_class != remote_class:
            # Critical if FK field is wrong type
            is_fk_field = field_id.endswith('_code') or field_id.endswith('_id')

            if is_fk_field and 'TextField' in remote_class and 'SelectBox' in local_class:
                differences.append(FieldDifference(
                    field_id=field_id,
                    difference_type=DifferenceType.WRONG_FIELD_TYPE,
                    local_value=local_class,
                    remote_value=remote_class,
                    severity='critical',
                    message=f"Field '{field_id}' is TextField in Joget but should be SelectBox for nested LOV"
                ))
            else:
                differences.append(FieldDifference(
                    field_id=field_id,
                    difference_type=DifferenceType.FIELD_TYPE_MISMATCH,
                    local_value=local_class,
                    remote_value=remote_class,
                    severity='warning',
                    message=f"Field '{field_id}' has different type: local={local_class}, remote={remote_class}"
                ))

        # Check 2: SelectBox should have FormOptionsBinder
        if 'SelectBox' in local_class:
            local_props = local_field.get('properties', {})
            remote_props = remote_field.get('properties', {})

            local_binder = local_props.get('optionsBinder', {})
            remote_binder = remote_props.get('optionsBinder', {})

            if local_binder and not remote_binder:
                differences.append(FieldDifference(
                    field_id=field_id,
                    difference_type=DifferenceType.BINDER_MISMATCH,
                    local_value=local_binder.get('className'),
                    remote_value=None,
                    severity='critical',
                    message=f"Field '{field_id}' missing FormOptionsBinder in remote"
                ))
            elif local_binder and remote_binder:
                # Check binder configuration
                local_binder_props = local_binder.get('properties', {})
                remote_binder_props = remote_binder.get('properties', {})

                # Check parent form reference
                local_form_ref = local_binder_props.get('formDefId')
                remote_form_ref = remote_binder_props.get('formDefId')

                if local_form_ref != remote_form_ref:
                    differences.append(FieldDifference(
                        field_id=field_id,
                        difference_type=DifferenceType.BINDER_MISMATCH,
                        local_value=local_form_ref,
                        remote_value=remote_form_ref,
                        severity='critical',
                        message=f"Field '{field_id}' references different parent form: local={local_form_ref}, remote={remote_form_ref}"
                    ))

        # Check 3: PK field should have DuplicateValueValidator
        if field_id in ['id', 'code']:
            local_props = local_field.get('properties', {})
            remote_props = remote_field.get('properties', {})

            local_validator = local_props.get('validator', {})
            remote_validator = remote_props.get('validator', {})

            if 'DuplicateValueValidator' in local_validator.get('className', ''):
                if 'DuplicateValueValidator' not in remote_validator.get('className', ''):
                    differences.append(FieldDifference(
                        field_id=field_id,
                        difference_type=DifferenceType.MISSING_VALIDATOR,
                        local_value='DuplicateValueValidator',
                        remote_value=remote_validator.get('className'),
                        severity='warning',
                        message=f"Primary key field '{field_id}' missing DuplicateValueValidator in remote"
                    ))

        return differences

    def generate_comparison_report(self, comparisons: List[FormComparison]) -> str:
        """
        Generate human-readable comparison report.

        Args:
            comparisons: List of FormComparison objects

        Returns:
            Formatted report string
        """
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("FORM COMPARISON REPORT")
        report_lines.append("=" * 80)
        report_lines.append("")

        # Summary
        total_forms = len(comparisons)
        missing_forms = len([c for c in comparisons if not c.exists_in_joget])
        forms_with_diffs = len([c for c in comparisons if c.has_differences])
        total_critical = sum(c.critical_count for c in comparisons)
        total_warnings = sum(c.warning_count for c in comparisons)

        report_lines.append(f"Total Forms Compared: {total_forms}")
        report_lines.append(f"Missing in Joget: {missing_forms}")
        report_lines.append(f"Forms with Differences: {forms_with_diffs}")
        report_lines.append(f"Critical Issues: {total_critical}")
        report_lines.append(f"Warnings: {total_warnings}")
        report_lines.append("")

        # Detailed comparison
        for comparison in comparisons:
            if not comparison.has_differences:
                continue

            report_lines.append("-" * 80)
            report_lines.append(f"Form: {comparison.form_id}")
            report_lines.append(f"Exists in Joget: {comparison.exists_in_joget}")
            report_lines.append(f"Critical: {comparison.critical_count}, Warnings: {comparison.warning_count}, Info: {comparison.info_count}")
            report_lines.append("")

            # Group differences by severity
            critical = [d for d in comparison.differences if d.severity == 'critical']
            warnings = [d for d in comparison.differences if d.severity == 'warning']
            info = [d for d in comparison.differences if d.severity == 'info']

            if critical:
                report_lines.append("  CRITICAL ISSUES:")
                for diff in critical:
                    report_lines.append(f"    ✗ {diff.message}")

            if warnings:
                report_lines.append("  WARNINGS:")
                for diff in warnings:
                    report_lines.append(f"    ⚠ {diff.message}")

            if info:
                report_lines.append("  INFO:")
                for diff in info:
                    report_lines.append(f"    ℹ {diff.message}")

            report_lines.append("")

        report_lines.append("=" * 80)

        return "\n".join(report_lines)
