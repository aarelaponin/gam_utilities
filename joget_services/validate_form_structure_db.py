#!/usr/bin/env python3
"""
Form Structure Database Validator
==================================
Validates form_structure.yaml against actual database schema and enriches it
with database validation metadata.

Features:
- Connects to MySQL database and validates all field mappings
- Updates form_structure.yaml with db_* validation metadata
- Generates comprehensive validation reports
- Detects missing tables, columns, and type mismatches

Usage:
    python validate_form_structure_db.py
    python validate_form_structure_db.py --dry-run
    python validate_form_structure_db.py --report-only
    python validate_form_structure_db.py --env /path/to/.env
"""

import os
import sys
import yaml
import pymysql
import json
import argparse
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from collections import defaultdict


@dataclass
class ColumnInfo:
    """Database column information."""
    name: str
    data_type: str
    max_length: Optional[int]
    nullable: bool
    key_type: str
    default_value: Optional[str]
    extra: str


@dataclass
class ValidationResult:
    """Validation result for a single field."""
    form_id: str
    field_id: str
    table_name: str
    column_name: str
    field_location: str  # 'sections.fields', 'all_fields', 'grids.sub_form_fields'

    # Validation status
    db_validated: bool = False
    db_table_exists: bool = False
    db_column_exists: bool = False

    # Column metadata
    db_column_type: Optional[str] = None
    db_nullable: Optional[bool] = None
    db_key_type: Optional[str] = None
    db_max_length: Optional[int] = None

    # Error/warning info
    db_error: Optional[str] = None
    db_warning: Optional[str] = None
    suggestions: List[str] = field(default_factory=list)


@dataclass
class ValidationSummary:
    """Overall validation summary."""
    total_forms: int = 0
    total_fields: int = 0
    validated_fields: int = 0
    failed_validations: int = 0
    missing_tables: int = 0
    missing_columns: int = 0
    warnings: int = 0

    # Coverage metrics
    table_coverage_pct: float = 0.0
    column_coverage_pct: float = 0.0

    # Lists
    missing_table_names: List[str] = field(default_factory=list)
    missing_column_details: List[Dict] = field(default_factory=list)


class FormStructureValidator:
    """Validates form_structure.yaml against database schema."""

    def __init__(self, env_file: str = ".env", form_structure_file: str = "form_structure.yaml"):
        """Initialize validator."""
        load_dotenv(env_file)

        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME', 'jwdb'),
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }

        self.form_structure_file = form_structure_file
        self.connection = None
        self.form_data = None
        self.tables_cache: Dict[str, Dict[str, ColumnInfo]] = {}
        self.validation_results: List[ValidationResult] = []
        self.validation_timestamp = datetime.now().isoformat()

    def connect(self) -> bool:
        """Connect to database."""
        try:
            self.connection = pymysql.connect(**self.db_config)
            print(f"✓ Connected to database: {self.db_config['database']}@{self.db_config['host']}:{self.db_config['port']}")
            return True
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            return False

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            print("✓ Database connection closed")

    def load_form_structure(self) -> bool:
        """Load form_structure.yaml."""
        try:
            with open(self.form_structure_file, 'r', encoding='utf-8') as f:
                self.form_data = yaml.safe_load(f)
            print(f"✓ Loaded form structure: {self.form_structure_file}")
            return True
        except Exception as e:
            print(f"✗ Failed to load form structure: {e}")
            return False

    def get_table_columns(self, table_name: str) -> Optional[Dict[str, ColumnInfo]]:
        """Get all columns for a table (with caching)."""
        if table_name in self.tables_cache:
            return self.tables_cache[table_name]

        with self.connection.cursor() as cursor:
            # Try with original name first, then with app_fd_ prefix
            table_variants = [table_name]
            if not table_name.startswith('app_fd_'):
                table_variants.append(f'app_fd_{table_name}')

            actual_table_name = None
            for variant in table_variants:
                cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM information_schema.tables
                    WHERE table_schema = %s AND table_name = %s
                """, (self.db_config['database'], variant))

                result = cursor.fetchone()
                if result['count'] > 0:
                    actual_table_name = variant
                    break

            if actual_table_name is None:
                self.tables_cache[table_name] = None
                return None

            # Get columns (use actual_table_name which includes prefix if needed)
            cursor.execute("""
                SELECT
                    COLUMN_NAME as name,
                    DATA_TYPE as type,
                    CHARACTER_MAXIMUM_LENGTH as max_length,
                    IS_NULLABLE as nullable,
                    COLUMN_KEY as key_type,
                    COLUMN_DEFAULT as default_value,
                    EXTRA as extra
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ORDINAL_POSITION
            """, (self.db_config['database'], actual_table_name))

            columns = {}
            for col in cursor.fetchall():
                col_info = ColumnInfo(
                    name=col['name'],
                    data_type=col['type'],
                    max_length=col['max_length'],
                    nullable=col['nullable'] == 'YES',
                    key_type=col['key_type'] or '',
                    default_value=col['default_value'],
                    extra=col['extra'] or ''
                )
                columns[col['name']] = col_info

            self.tables_cache[table_name] = columns
            return columns

    def validate_field(self, form_id: str, field: Dict, location: str) -> ValidationResult:
        """Validate a single field against database."""
        field_id = field.get('field_id', 'unknown')
        table_name = field.get('table')
        column_name = field.get('column')

        result = ValidationResult(
            form_id=form_id,
            field_id=field_id,
            table_name=table_name or 'unknown',
            column_name=column_name or 'unknown',
            field_location=location
        )

        # Check if table/column properties exist
        if not table_name:
            result.db_error = "Missing 'table' property"
            return result

        if not column_name:
            result.db_error = "Missing 'column' property"
            return result

        # Get table columns
        columns = self.get_table_columns(table_name)

        if columns is None:
            result.db_table_exists = False
            result.db_error = f"Table '{table_name}' not found in database"
            return result

        result.db_table_exists = True

        # Check if column exists
        if column_name not in columns:
            result.db_column_exists = False
            result.db_error = f"Column '{column_name}' not found in table '{table_name}'"

            # Suggest similar columns
            similar = self.find_similar_columns(column_name, list(columns.keys()))
            if similar:
                result.suggestions = similar[:5]

            return result

        # Column exists - get metadata
        col_info = columns[column_name]
        result.db_column_exists = True
        result.db_validated = True
        result.db_column_type = col_info.data_type
        result.db_nullable = col_info.nullable
        result.db_key_type = col_info.key_type
        result.db_max_length = col_info.max_length

        # Type compatibility check
        field_type = field.get('type', '')
        if not self.is_type_compatible(field_type, col_info.data_type):
            result.db_warning = (f"Potential type mismatch: Joget field type '{field_type}' "
                                f"vs DB column type '{col_info.data_type}'")

        return result

    def find_similar_columns(self, target: str, available: List[str], threshold: float = 0.6) -> List[str]:
        """Find similar column names."""
        from difflib import SequenceMatcher

        similar = []
        target_clean = target.replace('c_', '').replace('_', '').lower()

        for col in available:
            col_clean = col.replace('c_', '').replace('_', '').lower()
            score = SequenceMatcher(None, target_clean, col_clean).ratio()
            if score >= threshold:
                similar.append((col, score))

        return [col for col, _ in sorted(similar, key=lambda x: x[1], reverse=True)]

    def is_type_compatible(self, joget_type: str, db_type: str) -> bool:
        """Check if Joget field type is compatible with database column type."""
        # Type mapping
        type_map = {
            'text': ['varchar', 'char', 'text', 'longtext'],
            'textarea': ['text', 'longtext', 'mediumtext'],
            'number': ['int', 'bigint', 'decimal', 'float', 'double', 'tinyint', 'smallint'],
            'date': ['date', 'datetime', 'timestamp'],
            'select': ['varchar', 'char', 'int', 'text'],
            'radio': ['varchar', 'char', 'int'],
            'checkbox': ['varchar', 'text', 'int'],
            'hidden': ['varchar', 'char', 'int', 'bigint', 'text'],
            'html': ['text', 'longtext', 'mediumtext'],
            'signature': ['text', 'longtext', 'blob', 'mediumblob'],
            'id_generator': ['varchar', 'char'],
        }

        if joget_type not in type_map:
            return True  # Unknown type, assume compatible

        compatible_types = type_map[joget_type]
        return any(db_type.startswith(t) for t in compatible_types)

    def validate_all_fields(self):
        """Validate all fields in all forms."""
        forms = self.form_data.get('forms', {})
        total_forms = len(forms)

        print(f"\n{'='*80}")
        print(f"Validating {total_forms} forms...")
        print(f"{'='*80}\n")

        for form_idx, (form_id, form_data) in enumerate(forms.items(), 1):
            form_name = form_data.get('form_name', form_id)
            table_name = form_data.get('table_name', 'unknown')

            print(f"[{form_idx}/{total_forms}] Validating: {form_name}")
            print(f"  Table: {table_name}")

            # Validate sections.fields
            sections = form_data.get('sections', [])
            for section in sections:
                fields = section.get('fields', [])
                for field in fields:
                    if 'field_id' in field and 'type' in field:
                        result = self.validate_field(form_id, field, 'sections.fields')
                        self.validation_results.append(result)

            # Validate all_fields
            all_fields = form_data.get('all_fields', [])
            for field in all_fields:
                if 'field_id' in field and 'type' in field:
                    result = self.validate_field(form_id, field, 'all_fields')
                    self.validation_results.append(result)

            # Validate grids.sub_form_fields
            grids = form_data.get('grids', [])
            for grid in grids:
                sub_form_fields = grid.get('sub_form_fields', [])
                for field in sub_form_fields:
                    if 'field_id' in field and 'type' in field:
                        result = self.validate_field(form_id, field, 'grids.sub_form_fields')
                        self.validation_results.append(result)

            # Also check grids within sections
            for section in sections:
                section_grids = section.get('grids', [])
                for grid in section_grids:
                    sub_form_fields = grid.get('sub_form_fields', [])
                    for field in sub_form_fields:
                        if 'field_id' in field and 'type' in field:
                            result = self.validate_field(form_id, field, 'sections.grids.sub_form_fields')
                            self.validation_results.append(result)

            # Show summary for this form
            form_results = [r for r in self.validation_results if r.form_id == form_id]
            validated = sum(1 for r in form_results if r.db_validated)
            failed = sum(1 for r in form_results if not r.db_validated and r.db_error)
            warnings = sum(1 for r in form_results if r.db_warning)

            status = "✓" if failed == 0 else "⚠"
            print(f"  {status} Results: {validated} validated, {failed} failed, {warnings} warnings\n")

    def generate_summary(self) -> ValidationSummary:
        """Generate validation summary statistics."""
        summary = ValidationSummary()

        summary.total_forms = len(set(r.form_id for r in self.validation_results))
        summary.total_fields = len(self.validation_results)
        summary.validated_fields = sum(1 for r in self.validation_results if r.db_validated)
        summary.failed_validations = sum(1 for r in self.validation_results if r.db_error)
        summary.warnings = sum(1 for r in self.validation_results if r.db_warning)

        # Count missing tables and columns
        missing_tables = set()
        for result in self.validation_results:
            if not result.db_table_exists:
                missing_tables.add(result.table_name)
            if result.db_table_exists and not result.db_column_exists:
                summary.missing_columns += 1
                summary.missing_column_details.append({
                    'form': result.form_id,
                    'field': result.field_id,
                    'table': result.table_name,
                    'column': result.column_name,
                    'suggestions': result.suggestions
                })

        summary.missing_tables = len(missing_tables)
        summary.missing_table_names = sorted(list(missing_tables))

        # Calculate coverage
        if summary.total_fields > 0:
            summary.table_coverage_pct = ((summary.total_fields - summary.missing_tables) /
                                          summary.total_fields * 100)
            summary.column_coverage_pct = (summary.validated_fields / summary.total_fields * 100)

        return summary

    def update_yaml_with_validation(self, dry_run: bool = False):
        """Update form_structure.yaml with validation metadata."""
        if dry_run:
            print("\n[DRY RUN] Would update form_structure.yaml with validation metadata")
            return

        print(f"\nUpdating {self.form_structure_file} with validation metadata...")

        # Create a mapping of results for quick lookup
        results_map = {}
        for result in self.validation_results:
            key = (result.form_id, result.field_id, result.field_location)
            results_map[key] = result

        # Update the form data
        forms = self.form_data.get('forms', {})
        updated_count = 0

        for form_id, form_data in forms.items():
            # Update sections.fields
            sections = form_data.get('sections', [])
            for section in sections:
                fields = section.get('fields', [])
                for field in fields:
                    if 'field_id' in field and 'type' in field:
                        key = (form_id, field['field_id'], 'sections.fields')
                        if key in results_map:
                            self._add_validation_metadata(field, results_map[key])
                            updated_count += 1

            # Update all_fields
            all_fields = form_data.get('all_fields', [])
            for field in all_fields:
                if 'field_id' in field and 'type' in field:
                    key = (form_id, field['field_id'], 'all_fields')
                    if key in results_map:
                        self._add_validation_metadata(field, results_map[key])
                        updated_count += 1

            # Update grids.sub_form_fields
            grids = form_data.get('grids', [])
            for grid in grids:
                sub_form_fields = grid.get('sub_form_fields', [])
                for field in sub_form_fields:
                    if 'field_id' in field and 'type' in field:
                        key = (form_id, field['field_id'], 'grids.sub_form_fields')
                        if key in results_map:
                            self._add_validation_metadata(field, results_map[key])
                            updated_count += 1

            # Update grids within sections
            for section in sections:
                section_grids = section.get('grids', [])
                for grid in section_grids:
                    sub_form_fields = grid.get('sub_form_fields', [])
                    for field in sub_form_fields:
                        if 'field_id' in field and 'type' in field:
                            key = (form_id, field['field_id'], 'sections.grids.sub_form_fields')
                            if key in results_map:
                                self._add_validation_metadata(field, results_map[key])
                                updated_count += 1

        # Write back to file
        with open(self.form_structure_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.form_data, f, default_flow_style=False, sort_keys=False,
                     allow_unicode=True, width=1000)

        print(f"✓ Updated {updated_count} field definitions in {self.form_structure_file}")

    def _add_validation_metadata(self, field: Dict, result: ValidationResult):
        """Add validation metadata to a field dict."""
        field['db_validated'] = result.db_validated
        field['db_table_exists'] = result.db_table_exists
        field['db_column_exists'] = result.db_column_exists

        if result.db_column_type:
            # Format type with length if applicable
            if result.db_max_length:
                field['db_column_type'] = f"{result.db_column_type}({result.db_max_length})"
            else:
                field['db_column_type'] = result.db_column_type

        if result.db_nullable is not None:
            field['db_nullable'] = result.db_nullable

        if result.db_key_type:
            field['db_key_type'] = result.db_key_type

        if result.db_error:
            field['db_error'] = result.db_error

        if result.db_warning:
            field['db_warning'] = result.db_warning

        field['db_validation_timestamp'] = self.validation_timestamp

    def generate_json_report(self, output_file: str = "validation_report.json"):
        """Generate JSON validation report."""
        summary = self.generate_summary()

        report = {
            'metadata': {
                'validation_timestamp': self.validation_timestamp,
                'database': f"{self.db_config['database']}@{self.db_config['host']}:{self.db_config['port']}",
                'form_structure_file': self.form_structure_file
            },
            'summary': asdict(summary),
            'validation_results': [
                {
                    'form_id': r.form_id,
                    'field_id': r.field_id,
                    'location': r.field_location,
                    'table': r.table_name,
                    'column': r.column_name,
                    'validated': r.db_validated,
                    'table_exists': r.db_table_exists,
                    'column_exists': r.db_column_exists,
                    'column_type': r.db_column_type,
                    'nullable': r.db_nullable,
                    'error': r.db_error,
                    'warning': r.db_warning,
                    'suggestions': r.suggestions
                }
                for r in self.validation_results
            ]
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        print(f"✓ Generated JSON report: {output_file}")

    def generate_markdown_report(self, output_file: str = "validation_report.md"):
        """Generate Markdown validation report."""
        summary = self.generate_summary()

        lines = []
        lines.append("# Form Structure Database Validation Report")
        lines.append(f"\n**Validation Date:** {self.validation_timestamp}")
        lines.append(f"**Database:** `{self.db_config['database']}@{self.db_config['host']}:{self.db_config['port']}`")
        lines.append(f"**Form Structure File:** `{self.form_structure_file}`")

        lines.append("\n## Summary\n")
        lines.append(f"- **Total Forms:** {summary.total_forms}")
        lines.append(f"- **Total Fields:** {summary.total_fields}")
        lines.append(f"- **Validated Fields:** {summary.validated_fields} ({summary.column_coverage_pct:.1f}%)")
        lines.append(f"- **Failed Validations:** {summary.failed_validations}")
        lines.append(f"- **Warnings:** {summary.warnings}")
        lines.append(f"- **Missing Tables:** {summary.missing_tables}")
        lines.append(f"- **Missing Columns:** {summary.missing_columns}")

        # Validation Status
        if summary.failed_validations == 0:
            lines.append("\n### ✅ Validation Status: PASSED")
            lines.append("\nAll fields are correctly mapped to existing database tables and columns!")
        else:
            lines.append("\n### ⚠️ Validation Status: ISSUES FOUND")
            lines.append(f"\nFound {summary.failed_validations} validation issues that need attention.")

        # Missing Tables
        if summary.missing_table_names:
            lines.append("\n## Missing Tables\n")
            lines.append("The following tables are referenced in form_structure.yaml but do not exist in the database:\n")
            for table in summary.missing_table_names:
                lines.append(f"- `{table}`")

        # Missing Columns
        if summary.missing_column_details:
            lines.append("\n## Missing Columns\n")
            lines.append("| Form | Field | Table | Expected Column | Suggestions |")
            lines.append("|------|-------|-------|----------------|-------------|")
            for detail in summary.missing_column_details:
                suggestions = ', '.join(f"`{s}`" for s in detail['suggestions'][:3]) if detail['suggestions'] else "None"
                lines.append(f"| `{detail['form']}` | `{detail['field']}` | `{detail['table']}` | "
                           f"`{detail['column']}` | {suggestions} |")

        # Warnings
        warnings = [r for r in self.validation_results if r.db_warning]
        if warnings:
            lines.append("\n## Warnings\n")
            for w in warnings:
                lines.append(f"- **{w.form_id}.{w.field_id}**: {w.db_warning}")

        # Per-Form Summary
        lines.append("\n## Per-Form Validation Results\n")
        forms_summary = defaultdict(lambda: {'total': 0, 'validated': 0, 'failed': 0})
        for result in self.validation_results:
            forms_summary[result.form_id]['total'] += 1
            if result.db_validated:
                forms_summary[result.form_id]['validated'] += 1
            if result.db_error:
                forms_summary[result.form_id]['failed'] += 1

        lines.append("| Form | Total Fields | Validated | Failed | Status |")
        lines.append("|------|--------------|-----------|--------|--------|")
        for form_id, stats in sorted(forms_summary.items()):
            status = "✓" if stats['failed'] == 0 else "⚠"
            lines.append(f"| `{form_id}` | {stats['total']} | {stats['validated']} | "
                        f"{stats['failed']} | {status} |")

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"✓ Generated Markdown report: {output_file}")

    def print_console_summary(self):
        """Print validation summary to console."""
        summary = self.generate_summary()

        print(f"\n{'='*80}")
        print("VALIDATION SUMMARY")
        print(f"{'='*80}")
        print(f"Database: {self.db_config['database']}@{self.db_config['host']}:{self.db_config['port']}")
        print(f"Timestamp: {self.validation_timestamp}")
        print(f"{'='*80}")
        print(f"Total Forms:           {summary.total_forms}")
        print(f"Total Fields:          {summary.total_fields}")
        print(f"Validated Fields:      {summary.validated_fields} ({summary.column_coverage_pct:.1f}%)")
        print(f"Failed Validations:    {summary.failed_validations}")
        print(f"Warnings:              {summary.warnings}")
        print(f"Missing Tables:        {summary.missing_tables}")
        print(f"Missing Columns:       {summary.missing_columns}")
        print(f"{'='*80}")

        if summary.failed_validations == 0 and summary.warnings == 0:
            print("✅ VALIDATION PASSED - All fields correctly mapped!")
        elif summary.failed_validations > 0:
            print(f"⚠️  VALIDATION ISSUES - {summary.failed_validations} errors found")
        else:
            print(f"⚠️  VALIDATION WARNINGS - {summary.warnings} warnings")

        print(f"{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Validate form_structure.yaml against database schema',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate and update form_structure.yaml
  python validate_form_structure_db.py

  # Dry-run (show what would change)
  python validate_form_structure_db.py --dry-run

  # Generate reports only (no YAML update)
  python validate_form_structure_db.py --report-only

  # Custom env file
  python validate_form_structure_db.py --env /path/to/.env
        """
    )

    parser.add_argument(
        '--env',
        default='.env',
        help='Path to .env file (default: .env)'
    )

    parser.add_argument(
        '--form-structure',
        default='form_structure.yaml',
        help='Path to form_structure.yaml (default: form_structure.yaml)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be updated without modifying files'
    )

    parser.add_argument(
        '--report-only',
        action='store_true',
        help='Generate reports only, do not update YAML'
    )

    parser.add_argument(
        '--output-dir',
        default='.',
        help='Output directory for reports (default: current directory)'
    )

    args = parser.parse_args()

    # Create validator
    validator = FormStructureValidator(
        env_file=args.env,
        form_structure_file=args.form_structure
    )

    # Load form structure
    if not validator.load_form_structure():
        sys.exit(1)

    # Connect to database
    if not validator.connect():
        sys.exit(1)

    try:
        # Validate all fields
        validator.validate_all_fields()

        # Print console summary
        validator.print_console_summary()

        # Update YAML (unless report-only or dry-run)
        if not args.report_only:
            validator.update_yaml_with_validation(dry_run=args.dry_run)

        # Generate reports
        print(f"\n{'='*80}")
        print("GENERATING REPORTS")
        print(f"{'='*80}\n")

        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        validator.generate_json_report(str(output_dir / "validation_report.json"))
        validator.generate_markdown_report(str(output_dir / "validation_report.md"))

        print(f"\n{'='*80}")
        print("VALIDATION COMPLETE")
        print(f"{'='*80}")

        summary = validator.generate_summary()
        if summary.failed_validations > 0:
            sys.exit(1)

    finally:
        validator.close()


if __name__ == '__main__':
    main()
