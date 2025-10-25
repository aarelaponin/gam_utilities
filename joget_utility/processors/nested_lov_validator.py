#!/usr/bin/env python3
"""
Nested LOV Data Integrity Validator
Validates referential integrity of nested List of Values in metadata CSV files.

SINGLE RESPONSIBILITY: Check if nested LOV references are valid
Does NOT: Generate forms, fix issues, or deploy
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
import logging

from .csv_processor import CSVProcessor


@dataclass
class NestedLOVReference:
    """Information about a potential nested LOV reference"""
    child_form: str  # e.g., "md19crops"
    child_file: Path
    column_name: str  # e.g., "crop_category"
    parent_form_expected: str  # e.g., "crop"
    parent_file: Optional[Path]  # Actual parent file if found
    child_values: List[str]  # Values in child CSV
    parent_codes: List[str]  # Codes in parent CSV (if found)
    is_valid: bool
    match_percentage: float
    missing_values: List[str]
    classification: str  # "VALID", "FALSE_POSITIVE", "MISSING_PARENT", "BROKEN"
    recommendation: str


@dataclass
class ValidationReport:
    """Complete validation report for all metadata forms"""
    total_forms: int
    potential_nested_lovs: int
    valid_nested_lovs: List[NestedLOVReference]
    false_positives: List[NestedLOVReference]
    missing_parents: List[NestedLOVReference]
    broken_references: List[NestedLOVReference]
    simple_forms: int


class NestedLOVValidator:
    """
    Validate referential integrity of nested LOVs in metadata CSV files.

    Single Responsibility: Verify nested LOV data integrity

    Validation checks:
    1. Parent form exists
    2. All child values exist in parent codes
    3. Data format matches (codes vs descriptive text)
    """

    # Pattern to detect parent reference columns (same as form_generator)
    PARENT_REF_PATTERNS = [
        r'.*_category$',
        r'.*_type$',
        r'.*_group$',
        r'^parent_.*',
        r'.*_parent$'
    ]

    def __init__(self, metadata_dir: Path, logger: Optional[logging.Logger] = None):
        """
        Initialize validator

        Args:
            metadata_dir: Directory containing CSV metadata files
            logger: Logger instance (optional)
        """
        self.metadata_dir = Path(metadata_dir)
        self.logger = logger or logging.getLogger('joget_utility.nested_lov_validator')
        self.csv_processor = CSVProcessor()
        self.references: List[NestedLOVReference] = []

    def validate_all(self) -> ValidationReport:
        """
        Validate all CSV files in metadata directory.

        Returns:
            ValidationReport with complete analysis
        """
        if not self.metadata_dir.exists():
            raise FileNotFoundError(f"Metadata directory not found: {self.metadata_dir}")

        csv_files = sorted(self.metadata_dir.glob('*.csv'))

        if not csv_files:
            raise ValueError(f"No CSV files found in: {self.metadata_dir}")

        self.logger.info(f"Validating {len(csv_files)} CSV files")

        # Scan for potential nested LOVs
        potential_refs = []
        for csv_file in csv_files:
            refs = self._scan_csv_for_nested_lovs(csv_file)
            potential_refs.extend(refs)

        self.logger.info(f"Found {len(potential_refs)} potential nested LOV references")

        # Validate each reference
        for ref in potential_refs:
            self._validate_reference(ref)
            self.references.append(ref)

        # Generate report
        return self._generate_report(len(csv_files))

    def _scan_csv_for_nested_lovs(self, csv_file: Path) -> List[NestedLOVReference]:
        """
        Scan CSV file for potential nested LOV columns.

        Args:
            csv_file: Path to CSV file

        Returns:
            List of potential NestedLOVReference objects (not yet validated)
        """
        try:
            records = self.csv_processor.read_file(csv_file)

            if not records:
                return []

            # Get columns (excluding 'id')
            columns = [col for col in records[0].keys() if col.lower() != 'id']

            # Find potential parent reference columns
            refs = []
            for col in columns:
                if self._is_parent_reference(col) and col not in ['code', 'name']:
                    # Extract unique values from this column
                    values = list(set([str(record.get(col, '')).strip()
                                     for record in records if record.get(col)]))

                    # Derive expected parent form name
                    parent_form = self._derive_parent_form_name(col)

                    ref = NestedLOVReference(
                        child_form=csv_file.stem,
                        child_file=csv_file,
                        column_name=col,
                        parent_form_expected=parent_form,
                        parent_file=None,  # Will be populated during validation
                        child_values=values,
                        parent_codes=[],  # Will be populated if parent found
                        is_valid=False,
                        match_percentage=0.0,
                        missing_values=[],
                        classification="UNKNOWN",
                        recommendation=""
                    )
                    refs.append(ref)

            return refs

        except Exception as e:
            self.logger.error(f"Error scanning {csv_file}: {e}")
            return []

    def _validate_reference(self, ref: NestedLOVReference) -> None:
        """
        Validate a single nested LOV reference.

        Updates the NestedLOVReference object in-place with validation results.

        Args:
            ref: NestedLOVReference to validate
        """
        # Step 1: Find parent form
        parent_file = self._find_parent_form(ref.column_name)
        ref.parent_file = parent_file

        if not parent_file:
            # No parent form found
            ref.classification = "MISSING_PARENT"
            ref.is_valid = False
            ref.recommendation = (
                f"No parent form found for '{ref.column_name}'. "
                f"Expected form name containing '{ref.parent_form_expected}'. "
                f"This is likely a FALSE POSITIVE - convert SelectBox to TextField."
            )
            return

        # Step 2: Load parent codes
        try:
            parent_records = self.csv_processor.read_file(parent_file)
            if not parent_records:
                ref.classification = "BROKEN"
                ref.is_valid = False
                ref.recommendation = f"Parent form {parent_file.name} is empty"
                return

            # Get unique codes from parent
            parent_codes = list(set([str(record.get('code', '')).strip()
                                   for record in parent_records if record.get('code')]))
            ref.parent_codes = parent_codes

        except Exception as e:
            ref.classification = "BROKEN"
            ref.is_valid = False
            ref.recommendation = f"Error reading parent form: {e}"
            return

        # Step 3: Check referential integrity
        missing = []
        for value in ref.child_values:
            if value and value not in parent_codes:
                missing.append(value)

        ref.missing_values = missing

        # Calculate match percentage
        if ref.child_values:
            matched = len(ref.child_values) - len(missing)
            ref.match_percentage = (matched / len(ref.child_values)) * 100
        else:
            ref.match_percentage = 0.0

        # Step 4: Classify result
        if ref.match_percentage == 100.0:
            ref.classification = "VALID"
            ref.is_valid = True
            ref.recommendation = (
                f"✓ Valid nested LOV. Parent: {parent_file.name}. "
                f"All {len(ref.child_values)} values match parent codes."
            )
        elif ref.match_percentage >= 80.0:
            ref.classification = "BROKEN"
            ref.is_valid = False
            ref.recommendation = (
                f"Partial match ({ref.match_percentage:.1f}%). "
                f"Parent: {parent_file.name}. "
                f"Missing values: {', '.join(missing)}. "
                f"Fix data or use TextField instead."
            )
        else:
            ref.classification = "FALSE_POSITIVE"
            ref.is_valid = False
            ref.recommendation = (
                f"Low match ({ref.match_percentage:.1f}%). "
                f"This appears to be descriptive text, not a foreign key. "
                f"Convert SelectBox to TextField in form JSON."
            )

    def _find_parent_form(self, column_name: str) -> Optional[Path]:
        """
        Find parent CSV file for a column reference.

        Search patterns:
        1. Exact match: md*{derived_name}.csv
        2. Partial match: md*{part_of_name}*.csv
        3. Category/type match: md*category.csv, md*type.csv

        Args:
            column_name: Column name like "crop_category", "tool_type"

        Returns:
            Path to parent CSV file or None if not found
        """
        # Derive base name from column
        # crop_category → crop
        # tool_type → tool
        # target_group → target OR targetGroup
        base_name = re.sub(r'_(category|type|group|parent)$', '', column_name, flags=re.IGNORECASE)

        # Search patterns in order of specificity
        search_patterns = [
            f"md*{base_name}.csv",  # md19crop.csv
            f"md*{base_name}*.csv",  # md19cropCategory.csv
            f"*{base_name}*.csv",  # cropCategory.csv
        ]

        # Also try camelCase conversion
        camel_case = self._to_camel_case(base_name)
        if camel_case != base_name:
            search_patterns.append(f"md*{camel_case}*.csv")

        for pattern in search_patterns:
            matches = list(self.metadata_dir.glob(pattern))

            if matches:
                # Prefer exact matches over partial
                # Sort by length (shorter = more exact)
                matches.sort(key=lambda p: len(p.stem))

                self.logger.debug(f"Found parent for '{column_name}': {matches[0].name}")
                return matches[0]

        self.logger.debug(f"No parent form found for column '{column_name}' (base: {base_name})")
        return None

    def _generate_report(self, total_forms: int) -> ValidationReport:
        """
        Generate validation report from collected references.

        Args:
            total_forms: Total number of CSV files scanned

        Returns:
            ValidationReport with categorized results
        """
        valid = [r for r in self.references if r.classification == "VALID"]
        false_positives = [r for r in self.references if r.classification == "FALSE_POSITIVE"]
        missing_parents = [r for r in self.references if r.classification == "MISSING_PARENT"]
        broken = [r for r in self.references if r.classification == "BROKEN"]

        simple_forms = total_forms - len(self.references)

        report = ValidationReport(
            total_forms=total_forms,
            potential_nested_lovs=len(self.references),
            valid_nested_lovs=valid,
            false_positives=false_positives,
            missing_parents=missing_parents,
            broken_references=broken,
            simple_forms=simple_forms
        )

        return report

    def print_report(self, report: ValidationReport) -> None:
        """
        Print human-readable validation report.

        Args:
            report: ValidationReport to print
        """
        print("\n" + "=" * 70)
        print("Nested LOV Validation Report")
        print("=" * 70)
        print(f"Total CSV files scanned: {report.total_forms}")
        print(f"Potential nested LOVs detected: {report.potential_nested_lovs}")
        print(f"Simple metadata forms: {report.simple_forms}")
        print()

        # Valid nested LOVs
        if report.valid_nested_lovs:
            print(f"✓ VALID Nested LOVs: {len(report.valid_nested_lovs)}")
            for ref in report.valid_nested_lovs:
                parent_name = ref.parent_file.name if ref.parent_file else "N/A"
                print(f"  • {ref.child_form} ({ref.column_name})")
                print(f"    Parent: {parent_name} | Values: {len(ref.child_values)} | Match: 100%")
            print()

        # False positives
        if report.false_positives:
            print(f"⚠ FALSE POSITIVES (Convert SelectBox → TextField): {len(report.false_positives)}")
            for ref in report.false_positives:
                print(f"  • {ref.child_form} ({ref.column_name})")
                print(f"    Reason: {ref.recommendation}")
            print()

        # Missing parents
        if report.missing_parents:
            print(f"❌ MISSING PARENT FORMS: {len(report.missing_parents)}")
            for ref in report.missing_parents:
                print(f"  • {ref.child_form} ({ref.column_name})")
                print(f"    Expected parent: {ref.parent_form_expected}")
                print(f"    Recommendation: {ref.recommendation}")
            print()

        # Broken references
        if report.broken_references:
            print(f"⚠ BROKEN REFERENCES (Data mismatch): {len(report.broken_references)}")
            for ref in report.broken_references:
                parent_name = ref.parent_file.name if ref.parent_file else "N/A"
                print(f"  • {ref.child_form} ({ref.column_name})")
                print(f"    Parent: {parent_name} | Match: {ref.match_percentage:.1f}%")
                print(f"    Missing values: {', '.join(ref.missing_values[:5])}")
                if len(ref.missing_values) > 5:
                    print(f"    ... and {len(ref.missing_values) - 5} more")
            print()

        # Summary and recommendations
        print("=" * 70)
        print("SUMMARY & RECOMMENDATIONS")
        print("=" * 70)

        deployable = len(report.valid_nested_lovs)
        needs_fix = len(report.false_positives) + len(report.missing_parents)
        needs_review = len(report.broken_references)

        print(f"✓ Ready to deploy: {deployable} nested LOVs + {report.simple_forms} simple forms = {deployable + report.simple_forms} total")

        if needs_fix > 0:
            print(f"🔧 Need fixing: {needs_fix} forms (convert SelectBox → TextField)")
            print(f"   Run: python joget_utility.py --fix-false-positives")

        if needs_review > 0:
            print(f"👁 Need manual review: {needs_review} forms (data integrity issues)")

        print()

    # Helper methods

    def _is_parent_reference(self, column_name: str) -> bool:
        """Check if column name matches parent reference patterns"""
        for pattern in self.PARENT_REF_PATTERNS:
            if re.match(pattern, column_name, re.IGNORECASE):
                return True
        return False

    def _derive_parent_form_name(self, column_name: str) -> str:
        """
        Derive expected parent form name from column name.

        Examples:
            crop_category → crop
            tool_type → tool
            target_group → targetGroup
        """
        base = re.sub(r'_(category|type|group|parent)$', '', column_name, flags=re.IGNORECASE)
        return self._to_camel_case(base)

    def _to_camel_case(self, snake_str: str) -> str:
        """Convert snake_case to camelCase"""
        parts = snake_str.split('_')
        if len(parts) == 1:
            return snake_str
        return parts[0] + ''.join(p.capitalize() for p in parts[1:])


# Standalone execution
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python nested_lov_validator.py <metadata_dir>")
        sys.exit(1)

    metadata_dir = Path(sys.argv[1])

    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # Run validation
    validator = NestedLOVValidator(metadata_dir)
    report = validator.validate_all()
    validator.print_report(report)
