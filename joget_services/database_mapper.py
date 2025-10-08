#!/usr/bin/env python3
"""
Joget Database Mapper
=====================
Maps form fields to actual database tables based on real database data.
Works with output from form_parser.py

Usage:
    python database_mapper.py --template form_to_db_mapping_template.json
    python database_mapper.py --template form_to_db_mapping_template.json --output db_mapping.json
"""

import os
import sys
import json
import pymysql
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import argparse
from difflib import SequenceMatcher


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
class TableInfo:
    """Database table information."""
    table_name: str
    exists: bool
    columns: Dict[str, ColumnInfo] = field(default_factory=dict)
    row_count: int = 0


@dataclass
class FieldMapping:
    """Mapping between form field and database column."""
    field_id: str
    field_type: str
    expected_column: str
    actual_column: Optional[str] = None
    exists: bool = False
    column_info: Optional[ColumnInfo] = None
    similarity_score: float = 0.0
    suggestions: List[str] = field(default_factory=list)
    is_grid_container: bool = False
    status: str = "unknown"  # exact_match, similar_match, not_found, grid_container


@dataclass
class FormMapping:
    """Complete mapping for a form."""
    form_id: str
    form_name: str
    table_name: str
    primary_key: str
    table_info: Optional[TableInfo] = None
    field_mappings: List[FieldMapping] = field(default_factory=list)
    validation_summary: Dict = field(default_factory=dict)


class DatabaseMapper:
    """Maps form fields to database columns."""

    def __init__(self, env_file: str = ".env"):
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

        self.connection = None
        self.form_mappings: Dict[str, FormMapping] = {}
        self.tables_cache: Dict[str, TableInfo] = {}

    def connect(self) -> bool:
        """Connect to database."""
        try:
            self.connection = pymysql.connect(**self.db_config)
            print(f"✓ Connected to database: {self.db_config['database']}")
            return True
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            return False

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            print("✓ Database connection closed")

    def get_table_info(self, table_name: str) -> TableInfo:
        """Get complete table information from database."""
        if table_name in self.tables_cache:
            return self.tables_cache[table_name]

        with self.connection.cursor() as cursor:
            # Check if table exists
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_schema = %s AND table_name = %s
            """, (self.db_config['database'], table_name))

            result = cursor.fetchone()
            if result['count'] == 0:
                table_info = TableInfo(table_name=table_name, exists=False)
                self.tables_cache[table_name] = table_info
                return table_info

            # Get columns
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
            """, (self.db_config['database'], table_name))

            columns = {}
            for col in cursor.fetchall():
                col_info = ColumnInfo(
                    name=col['name'],
                    data_type=col['type'],
                    max_length=col['max_length'],
                    nullable=col['nullable'] == 'YES',
                    key_type=col['key_type'],
                    default_value=col['default_value'],
                    extra=col['extra']
                )
                columns[col['name']] = col_info

            # Get row count
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            row_count = cursor.fetchone()['count']

            table_info = TableInfo(
                table_name=table_name,
                exists=True,
                columns=columns,
                row_count=row_count
            )

            self.tables_cache[table_name] = table_info
            return table_info

    def calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings."""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

    def find_similar_columns(self, target_column: str, available_columns: List[str], threshold: float = 0.6) -> List[
        Tuple[str, float]]:
        """Find similar column names."""
        similar = []

        target_clean = target_column.replace('c_', '').replace('_', '').lower()

        for col in available_columns:
            col_clean = col.replace('c_', '').replace('_', '').lower()

            # Exact match without prefix
            if target_clean == col_clean:
                similar.append((col, 1.0))
                continue

            # Similarity score
            score = self.calculate_similarity(target_clean, col_clean)
            if score >= threshold:
                similar.append((col, score))

        return sorted(similar, key=lambda x: x[1], reverse=True)

    def is_grid_container(self, field_id: str, field_type: str) -> bool:
        """Check if field is a grid container."""
        grid_patterns = ['Members', 'Management', 'Details']

        if field_type == 'grid':
            return True

        for pattern in grid_patterns:
            if pattern in field_id:
                return True

        return False

    def map_field_to_column(self, field_data: Dict, table_info: TableInfo) -> FieldMapping:
        """Map a single field to database column."""
        field_id = field_data['field_id']
        field_type = field_data.get('type', field_data.get('field_type', 'unknown'))
        expected_column = field_data['expected_column']

        # Check if this is a grid container
        is_grid = self.is_grid_container(field_id, field_type)

        if is_grid:
            return FieldMapping(
                field_id=field_id,
                field_type=field_type,
                expected_column=expected_column,
                is_grid_container=True,
                status='grid_container'
            )

        # Table doesn't exist
        if not table_info.exists:
            return FieldMapping(
                field_id=field_id,
                field_type=field_type,
                expected_column=expected_column,
                exists=False,
                status='table_not_found'
            )

        # Check exact match
        if expected_column in table_info.columns:
            return FieldMapping(
                field_id=field_id,
                field_type=field_type,
                expected_column=expected_column,
                actual_column=expected_column,
                exists=True,
                column_info=table_info.columns[expected_column],
                similarity_score=1.0,
                status='exact_match'
            )

        # Find similar columns
        available_columns = list(table_info.columns.keys())
        similar = self.find_similar_columns(expected_column, available_columns)

        if similar:
            best_match, score = similar[0]
            suggestions = [col for col, _ in similar[:5]]

            return FieldMapping(
                field_id=field_id,
                field_type=field_type,
                expected_column=expected_column,
                actual_column=best_match,
                exists=True,
                column_info=table_info.columns[best_match],
                similarity_score=score,
                suggestions=suggestions,
                status='similar_match' if score >= 0.8 else 'possible_match'
            )

        # No match found
        return FieldMapping(
            field_id=field_id,
            field_type=field_type,
            expected_column=expected_column,
            exists=False,
            status='not_found'
        )

    def map_form(self, form_data: Dict) -> FormMapping:
        """Map all fields in a form."""
        form_id = form_data['form_id']
        form_name = form_data.get('form_name', form_id)
        table_name = form_data['table_name']
        primary_key = form_data.get('primary_key', 'c_id')

        print(f"\nMapping form: {form_name}")
        print(f"  Table: {table_name}")

        # Get table info
        table_info = self.get_table_info(table_name)

        if not table_info.exists:
            print(f"  ⚠ Table does not exist")
        else:
            print(f"  ✓ Found {len(table_info.columns)} columns, {table_info.row_count} rows")

        # Map each field
        field_mappings = []
        fields = form_data.get('fields', [])

        for field_data in fields:
            mapping = self.map_field_to_column(field_data, table_info)
            field_mappings.append(mapping)

        # Validation summary
        exact_matches = sum(1 for m in field_mappings if m.status == 'exact_match')
        similar_matches = sum(1 for m in field_mappings if m.status in ['similar_match', 'possible_match'])
        grid_containers = sum(1 for m in field_mappings if m.status == 'grid_container')
        not_found = sum(1 for m in field_mappings if m.status == 'not_found')

        validation_summary = {
            'exact_matches': exact_matches,
            'similar_matches': similar_matches,
            'grid_containers': grid_containers,
            'not_found': not_found,
            'total_fields': len(field_mappings)
        }

        print(
            f"  Results: {exact_matches} exact, {similar_matches} similar, {grid_containers} grids, {not_found} missing")

        return FormMapping(
            form_id=form_id,
            form_name=form_name,
            table_name=table_name,
            primary_key=primary_key,
            table_info=table_info,
            field_mappings=field_mappings,
            validation_summary=validation_summary
        )

    def process_template(self, template_file: str):
        """Process mapping template from form parser."""
        try:
            with open(template_file, 'r') as f:
                template = json.load(f)

            forms = template.get('forms', {})

            print(f"\nProcessing {len(forms)} forms...")
            print("=" * 80)

            for form_id, form_data in forms.items():
                form_mapping = self.map_form(form_data)
                self.form_mappings[form_id] = form_mapping

        except Exception as e:
            print(f"✗ Error processing template: {e}")
            sys.exit(1)

    def generate_text_report(self, output_file: str = "database_mapping.txt"):
        """Generate detailed text report."""
        with open(output_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("DATABASE MAPPING REPORT\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Database: {self.db_config['database']}@{self.db_config['host']}\n")
            f.write(f"Total Forms: {len(self.form_mappings)}\n")
            f.write("=" * 80 + "\n\n")

            # Overall statistics
            total_fields = sum(len(fm.field_mappings) for fm in self.form_mappings.values())
            total_exact = sum(fm.validation_summary['exact_matches'] for fm in self.form_mappings.values())
            total_similar = sum(fm.validation_summary['similar_matches'] for fm in self.form_mappings.values())
            total_grids = sum(fm.validation_summary['grid_containers'] for fm in self.form_mappings.values())
            total_missing = sum(fm.validation_summary['not_found'] for fm in self.form_mappings.values())

            f.write("OVERALL SUMMARY\n")
            f.write("-" * 80 + "\n")
            f.write(f"Total Fields:      {total_fields}\n")
            f.write(f"Exact Matches:     {total_exact} ({total_exact / total_fields * 100:.1f}%)\n")
            f.write(f"Similar Matches:   {total_similar} ({total_similar / total_fields * 100:.1f}%)\n")
            f.write(f"Grid Containers:   {total_grids} (info only)\n")
            f.write(f"Not Found:         {total_missing} ({total_missing / total_fields * 100:.1f}%)\n")
            f.write("\n\n")

            # Per-form details
            for form_id, form_mapping in sorted(self.form_mappings.items()):
                f.write("=" * 80 + "\n")
                f.write(f"FORM: {form_mapping.form_name}\n")
                f.write("=" * 80 + "\n")
                f.write(f"Form ID:        {form_mapping.form_id}\n")
                f.write(f"Table:          {form_mapping.table_name}\n")
                f.write(f"Primary Key:    {form_mapping.primary_key}\n")

                if form_mapping.table_info and form_mapping.table_info.exists:
                    f.write(f"Table Columns:  {len(form_mapping.table_info.columns)}\n")
                    f.write(f"Table Rows:     {form_mapping.table_info.row_count}\n")
                else:
                    f.write(f"Table Status:   NOT FOUND\n")

                f.write(f"\nValidation:\n")
                summary = form_mapping.validation_summary
                f.write(f"  Exact Matches:   {summary['exact_matches']}\n")
                f.write(f"  Similar Matches: {summary['similar_matches']}\n")
                f.write(f"  Grid Containers: {summary['grid_containers']}\n")
                f.write(f"  Not Found:       {summary['not_found']}\n")

                f.write("\n" + "-" * 80 + "\n")
                f.write("FIELD MAPPINGS:\n")
                f.write("-" * 80 + "\n\n")

                # Group by status
                by_status = {
                    'exact_match': [],
                    'similar_match': [],
                    'possible_match': [],
                    'grid_container': [],
                    'not_found': [],
                    'table_not_found': []
                }

                for mapping in form_mapping.field_mappings:
                    by_status[mapping.status].append(mapping)

                # Exact matches
                if by_status['exact_match']:
                    f.write("✓ EXACT MATCHES:\n\n")
                    for mapping in by_status['exact_match']:
                        f.write(f"  {mapping.field_id}\n")
                        f.write(f"    Column: {mapping.actual_column}\n")
                        if mapping.column_info:
                            f.write(f"    Type:   {mapping.column_info.data_type}")
                            if mapping.column_info.max_length:
                                f.write(f"({mapping.column_info.max_length})")
                            f.write("\n")
                        f.write("\n")

                # Similar matches (need review)
                if by_status['similar_match'] or by_status['possible_match']:
                    f.write("⚠ SIMILAR MATCHES (Review Recommended):\n\n")
                    for mapping in by_status['similar_match'] + by_status['possible_match']:
                        f.write(f"  {mapping.field_id}\n")
                        f.write(f"    Expected:    {mapping.expected_column}\n")
                        f.write(f"    Found:       {mapping.actual_column}\n")
                        f.write(f"    Similarity:  {mapping.similarity_score * 100:.1f}%\n")
                        if mapping.column_info:
                            f.write(f"    Type:        {mapping.column_info.data_type}\n")
                        if mapping.suggestions:
                            f.write(f"    Alternatives: {', '.join(mapping.suggestions[:3])}\n")
                        f.write("\n")

                # Grid containers
                if by_status['grid_container']:
                    f.write("ℹ GRID CONTAINERS (No Column Needed):\n\n")
                    for mapping in by_status['grid_container']:
                        f.write(f"  {mapping.field_id}\n")
                        f.write(f"    Status: Grid reference field\n\n")

                # Not found
                if by_status['not_found']:
                    f.write("✗ NOT FOUND:\n\n")
                    for mapping in by_status['not_found']:
                        f.write(f"  {mapping.field_id}\n")
                        f.write(f"    Expected: {mapping.expected_column}\n")
                        f.write(f"    Action:   Column needs to be created or field name is incorrect\n\n")

                f.write("\n\n")

        print(f"✓ Generated text report: {output_file}")

    def generate_json_report(self, output_file: str = "database_mapping.json"):
        """Generate JSON report."""
        report = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'database': f"{self.db_config['database']}@{self.db_config['host']}",
                'total_forms': len(self.form_mappings)
            },
            'forms': {}
        }

        for form_id, form_mapping in self.form_mappings.items():
            form_dict = {
                'form_id': form_mapping.form_id,
                'form_name': form_mapping.form_name,
                'table_name': form_mapping.table_name,
                'primary_key': form_mapping.primary_key,
                'table_exists': form_mapping.table_info.exists if form_mapping.table_info else False,
                'validation_summary': form_mapping.validation_summary,
                'field_mappings': []
            }

            for mapping in form_mapping.field_mappings:
                mapping_dict = {
                    'field_id': mapping.field_id,
                    'field_type': mapping.field_type,
                    'expected_column': mapping.expected_column,
                    'actual_column': mapping.actual_column,
                    'exists': mapping.exists,
                    'status': mapping.status,
                    'similarity_score': mapping.similarity_score
                }

                if mapping.column_info:
                    mapping_dict['column_info'] = {
                        'data_type': mapping.column_info.data_type,
                        'max_length': mapping.column_info.max_length,
                        'nullable': mapping.column_info.nullable
                    }

                if mapping.suggestions:
                    mapping_dict['suggestions'] = mapping.suggestions

                form_dict['field_mappings'].append(mapping_dict)

            report['forms'][form_id] = form_dict

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"✓ Generated JSON report: {output_file}")

    def generate_services_yml_corrections(self, output_file: str = "services_yml_corrections.txt"):
        """Generate corrections for services.yml."""
        corrections = []

        for form_id, form_mapping in self.form_mappings.items():
            for mapping in form_mapping.field_mappings:
                if mapping.status in ['similar_match', 'possible_match']:
                    corrections.append({
                        'form': form_mapping.form_name,
                        'field': mapping.field_id,
                        'expected': mapping.expected_column,
                        'actual': mapping.actual_column,
                        'confidence': mapping.similarity_score
                    })

        if not corrections:
            print("ℹ No corrections needed for services.yml")
            return

        with open(output_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("SERVICES.YML CORRECTIONS\n")
            f.write("=" * 80 + "\n")
            f.write(f"Total Corrections Needed: {len(corrections)}\n")
            f.write("=" * 80 + "\n\n")

            for correction in corrections:
                f.write(f"Form: {correction['form']}\n")
                f.write(f"Field: {correction['field']}\n")
                f.write(f"  Expected: {correction['expected']}\n")
                f.write(f"  Actual:   {correction['actual']}\n")
                f.write(f"  Confidence: {correction['confidence'] * 100:.1f}%\n")
                f.write(f"\n  Add to services.yml:\n")
                f.write(f"  - joget: \"{correction['field']}\"\n")
                f.write(f"    column: \"{correction['actual']}\"\n")
                f.write("\n" + "-" * 80 + "\n\n")

        print(f"✓ Generated corrections: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Map form fields to database tables based on actual data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Map using template from form parser
  python database_mapper.py --template form_to_db_mapping_template.json

  # Custom output directory
  python database_mapper.py --template form_to_db_mapping_template.json --output reports/
        """
    )

    parser.add_argument(
        '--template',
        required=True,
        help='Mapping template from form parser (JSON)'
    )

    parser.add_argument(
        '--output',
        default='.',
        help='Output directory for reports (default: current directory)'
    )

    parser.add_argument(
        '--env',
        default='.env',
        help='Path to .env file'
    )

    args = parser.parse_args()

    # Create mapper
    mapper = DatabaseMapper(env_file=args.env)

    if not mapper.connect():
        sys.exit(1)

    try:
        # Process template
        mapper.process_template(args.template)

        # Generate reports
        print("\n" + "=" * 80)
        print("GENERATING REPORTS")
        print("=" * 80 + "\n")

        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)

        mapper.generate_text_report(str(output_dir / "database_mapping.txt"))
        mapper.generate_json_report(str(output_dir / "database_mapping.json"))
        mapper.generate_services_yml_corrections(str(output_dir / "services_yml_corrections.txt"))

        print("\n" + "=" * 80)
        print("MAPPING COMPLETE")
        print("=" * 80)
        print("\nGenerated files:")
        print("  - database_mapping.txt: Detailed mapping report")
        print("  - database_mapping.json: Machine-readable mapping")
        print("  - services_yml_corrections.txt: Corrections for services.yml")

    finally:
        mapper.close()


if __name__ == '__main__':
    main()