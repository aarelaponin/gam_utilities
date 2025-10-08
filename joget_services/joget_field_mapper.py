#!/usr/bin/env python3
"""
Joget Field Mapper Utility
===========================
Maps Joget form fields from services.yml to their actual database table columns.

This utility:
1. Reads services.yml configuration
2. Connects to Joget MySQL database
3. Inspects actual table structures
4. Maps each form field to its database column
5. Validates the mappings
6. Auto-fixes common mapping issues
7. Generates comprehensive reports

Author: Farmers Registry Team
Version: 2.0 - Now with auto-fix capability!
"""

import os
import sys
import yaml
import pymysql
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime
from dotenv import load_dotenv
import json
import csv
import shutil
from pathlib import Path


@dataclass
class FieldMapping:
    """Represents a field mapping from services.yml to database."""
    section: str
    form_id: str
    table_name: str
    joget_field: str
    column_name: str
    govstack_path: str
    json_path: Optional[str] = None
    required: bool = False
    transform: Optional[str] = None
    is_grid: bool = False
    parent_field: Optional[str] = None
    exists_in_db: bool = False
    column_type: Optional[str] = None
    validation_status: str = "unknown"
    notes: List[str] = field(default_factory=list)
    is_grid_container: bool = False  # NEW: marks grid container fields
    auto_fix_suggested: Optional[str] = None  # NEW: auto-fix suggestion


@dataclass
class MappingFix:
    """Represents a suggested fix for a mapping issue."""
    section: str
    field: str
    issue_type: str
    current_column: str
    suggested_column: Optional[str]
    reason: str
    confidence: str  # high, medium, low


class JogetFieldMapper:
    """Maps Joget form fields to database columns."""

    def __init__(self, env_file: str = ".env", services_yml: str = "services.yml"):
        """Initialize the mapper with configuration files."""
        self.env_file = env_file
        self.services_yml = services_yml
        self.connection = None
        self.field_mappings: List[FieldMapping] = []
        self.table_structures: Dict[str, Dict] = {}
        self.mapping_fixes: List[MappingFix] = []
        self.grid_sections: Set[str] = set()  # Track grid sections

        # Load environment variables
        load_dotenv(self.env_file)

        # Database connection parameters
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME', 'jwdb'),
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }

    def connect_to_database(self) -> bool:
        """Establish connection to MySQL database."""
        try:
            self.connection = pymysql.connect(**self.db_config)
            print(f"✓ Connected to database: {self.db_config['database']}")
            return True
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            return False

    def close_connection(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            print("✓ Database connection closed")

    def load_services_yml(self) -> Dict:
        """Load and parse services.yml file."""
        try:
            with open(self.services_yml, 'r') as f:
                config = yaml.safe_load(f)
            print(f"✓ Loaded services.yml")
            return config
        except Exception as e:
            print(f"✗ Failed to load services.yml: {e}")
            sys.exit(1)

    def get_table_structure(self, table_name: str) -> Dict:
        """Get the structure of a database table."""
        if table_name in self.table_structures:
            return self.table_structures[table_name]

        try:
            with self.connection.cursor() as cursor:
                # Check if table exists
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM information_schema.tables 
                    WHERE table_schema = %s AND table_name = %s
                """, (self.db_config['database'], table_name))

                result = cursor.fetchone()
                if result['count'] == 0:
                    print(f"⚠ Table not found: {table_name}")
                    self.table_structures[table_name] = {'exists': False, 'columns': {}}
                    return self.table_structures[table_name]

                # Get column information
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
                    columns[col['name']] = {
                        'type': col['type'],
                        'max_length': col['max_length'],
                        'nullable': col['nullable'] == 'YES',
                        'key_type': col['key_type'],
                        'default_value': col['default_value'],
                        'extra': col['extra']
                    }

                self.table_structures[table_name] = {
                    'exists': True,
                    'columns': columns
                }

                print(f"✓ Analyzed table: {table_name} ({len(columns)} columns)")
                return self.table_structures[table_name]

        except Exception as e:
            print(f"✗ Error analyzing table {table_name}: {e}")
            self.table_structures[table_name] = {'exists': False, 'columns': {}}
            return self.table_structures[table_name]

    def derive_column_name(self, joget_field: str, explicit_column: Optional[str] = None) -> str:
        """Derive database column name from Joget field ID."""
        if explicit_column:
            return explicit_column

        # Standard Joget convention: prefix with 'c_'
        if not joget_field.startswith('c_'):
            return f"c_{joget_field}"
        return joget_field

    def identify_grid_sections(self, config: Dict):
        """Identify which sections are grid/array types."""
        form_mappings = config.get('formMappings', {})
        for section_name, section_config in form_mappings.items():
            if section_config.get('type') == 'array':
                self.grid_sections.add(section_name)

    def is_grid_container_field(self, field_name: str, section_name: str) -> bool:
        """
        Determine if a field is a grid container (doesn't have a real column).
        Grid containers are references to sub-forms and don't store data directly.
        """
        # Common patterns for grid container fields
        grid_patterns = [
            'householdMembers',
            'cropManagement',
            'livestockDetails',
            'Members',  # any field ending in Members
            'Management',  # any field ending in Management
            'Details'  # any field ending in Details
        ]

        # Check if field name matches grid patterns
        for pattern in grid_patterns:
            if pattern in field_name:
                return True

        # Check if this field references a known grid section
        if field_name in self.grid_sections:
            return True

        return False

    def find_similar_columns(self, target_column: str, table_name: str) -> List[str]:
        """Find similar column names in the table (fuzzy matching)."""
        if table_name not in self.table_structures:
            return []

        if not self.table_structures[table_name]['exists']:
            return []

        columns = list(self.table_structures[table_name]['columns'].keys())
        similar = []

        # Remove c_ prefix for comparison
        target_clean = target_column.replace('c_', '').lower()

        for col in columns:
            col_clean = col.replace('c_', '').lower()

            # Exact match without prefix
            if target_clean == col_clean:
                similar.append(col)
                continue

            # Partial match
            if target_clean in col_clean or col_clean in target_clean:
                similar.append(col)
                continue

            # Check for common variations
            # e.g., mainSourceAgriculturalInfo vs main_source_agric_info
            target_snake = target_clean.replace('_', '')
            col_snake = col_clean.replace('_', '')

            if target_snake in col_snake or col_snake in target_snake:
                similar.append(col)

        return similar

    def suggest_fix(self, mapping: FieldMapping, table_struct: Dict) -> Optional[MappingFix]:
        """Suggest a fix for a problematic mapping."""

        # Case 1: Grid container field (doesn't need a column)
        if self.is_grid_container_field(mapping.joget_field, mapping.section):
            return MappingFix(
                section=mapping.section,
                field=mapping.joget_field,
                issue_type='grid_container',
                current_column=mapping.column_name,
                suggested_column=None,
                reason=f"'{mapping.joget_field}' is a grid container field that references a sub-form. It doesn't need a database column.",
                confidence='high'
            )

        # Case 2: Column not found - look for similar columns
        if not mapping.exists_in_db and table_struct['exists']:
            similar_columns = self.find_similar_columns(mapping.column_name, mapping.table_name)

            if similar_columns:
                return MappingFix(
                    section=mapping.section,
                    field=mapping.joget_field,
                    issue_type='column_not_found',
                    current_column=mapping.column_name,
                    suggested_column=similar_columns[0],
                    reason=f"Column '{mapping.column_name}' not found. Did you mean '{similar_columns[0]}'? Similar columns: {', '.join(similar_columns)}",
                    confidence='medium' if len(similar_columns) > 1 else 'high'
                )
            else:
                return MappingFix(
                    section=mapping.section,
                    field=mapping.joget_field,
                    issue_type='column_not_found',
                    current_column=mapping.column_name,
                    reason=f"Column '{mapping.column_name}' not found in table '{mapping.table_name}'. The column may need to be created or the field name in services.yml is incorrect.",
                    suggested_column=None,
                    confidence='low'
                )

        # Case 3: Table doesn't exist
        if not table_struct['exists']:
            return MappingFix(
                section=mapping.section,
                field=mapping.joget_field,
                issue_type='table_not_found',
                current_column=mapping.column_name,
                suggested_column=None,
                reason=f"Table '{mapping.table_name}' does not exist in database. Create the form in Joget to generate the table.",
                confidence='high'
            )

        return None

    def process_field_mappings(self, config: Dict):
        """Process all field mappings from services.yml."""
        form_mappings = config.get('formMappings', {})

        # First pass: identify grid sections
        self.identify_grid_sections(config)

        for section_name, section_config in form_mappings.items():
            form_id = section_config.get('formId')
            table_name = section_config.get('tableName')
            is_grid = section_config.get('type') == 'array'
            parent_field = section_config.get('parentField')

            if not table_name:
                print(f"⚠ No table name for section: {section_name}")
                continue

            # Get table structure
            table_struct = self.get_table_structure(table_name)

            # Process fields
            fields = section_config.get('fields', [])
            for field_def in fields:
                joget_field = field_def.get('joget')
                if not joget_field:
                    continue

                # Check if this is a grid container field
                is_grid_container = self.is_grid_container_field(joget_field, section_name)

                # Derive column name
                explicit_column = field_def.get('column')
                column_name = self.derive_column_name(joget_field, explicit_column)

                # Check if column exists in database
                exists_in_db = False
                column_type = None
                notes = []

                if is_grid_container:
                    # Grid containers don't have actual columns
                    validation_status = "grid_container"
                    notes.append(f"Grid container field - references sub-form, no database column needed")
                elif table_struct['exists']:
                    if column_name in table_struct['columns']:
                        exists_in_db = True
                        column_type = table_struct['columns'][column_name]['type']
                        validation_status = "valid"
                    else:
                        notes.append(f"Column '{column_name}' not found in table")
                        validation_status = "missing"
                else:
                    notes.append(f"Table '{table_name}' does not exist")
                    validation_status = "table_missing"

                # Create field mapping
                mapping = FieldMapping(
                    section=section_name,
                    form_id=form_id,
                    table_name=table_name,
                    joget_field=joget_field,
                    column_name=column_name,
                    govstack_path=field_def.get('govstack', ''),
                    json_path=field_def.get('jsonPath'),
                    required=field_def.get('required', False),
                    transform=field_def.get('transform'),
                    is_grid=is_grid,
                    parent_field=parent_field,
                    exists_in_db=exists_in_db,
                    column_type=column_type,
                    validation_status=validation_status,
                    notes=notes,
                    is_grid_container=is_grid_container
                )

                # Suggest fixes for problematic mappings
                if validation_status in ['missing', 'table_missing']:
                    fix = self.suggest_fix(mapping, table_struct)
                    if fix:
                        self.mapping_fixes.append(fix)
                        mapping.auto_fix_suggested = fix.suggested_column

                self.field_mappings.append(mapping)

    def generate_fixes_report(self, output_file: str = "field_mapping_fixes.txt"):
        """Generate a report of suggested fixes."""
        if not self.mapping_fixes:
            print("✓ No issues found - all mappings are valid!")
            return

        with open(output_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("JOGET FIELD MAPPING - SUGGESTED FIXES\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Issues: {len(self.mapping_fixes)}\n")
            f.write("=" * 80 + "\n\n")

            # Group by issue type
            by_type = defaultdict(list)
            for fix in self.mapping_fixes:
                by_type[fix.issue_type].append(fix)

            # Grid container fields (not really issues)
            if 'grid_container' in by_type:
                f.write("INFO: Grid Container Fields (No Action Needed)\n")
                f.write("-" * 80 + "\n")
                f.write("These fields reference sub-forms and don't need database columns.\n\n")

                for fix in by_type['grid_container']:
                    f.write(f"✓ {fix.section}.{fix.field}\n")
                    f.write(f"   Current: {fix.current_column}\n")
                    f.write(f"   Status:  {fix.reason}\n\n")

                f.write("\n")

            # Missing columns with suggestions
            if 'column_not_found' in by_type:
                f.write("ACTION REQUIRED: Missing Columns\n")
                f.write("-" * 80 + "\n\n")

                high_confidence = [f for f in by_type['column_not_found'] if f.confidence == 'high']
                medium_confidence = [f for f in by_type['column_not_found'] if f.confidence == 'medium']
                low_confidence = [f for f in by_type['column_not_found'] if f.confidence == 'low']

                if high_confidence:
                    f.write("HIGH CONFIDENCE FIXES:\n\n")
                    for fix in high_confidence:
                        f.write(f"Issue: {fix.section}.{fix.field}\n")
                        f.write(f"   Looking for: {fix.current_column}\n")
                        if fix.suggested_column:
                            f.write(f"   → SUGGESTED FIX: Use column '{fix.suggested_column}'\n")
                            f.write(f"   \n")
                            f.write(f"   Add to services.yml:\n")
                            f.write(f"   - joget: \"{fix.field}\"\n")
                            f.write(f"     column: \"{fix.suggested_column}\"\n")
                        f.write(f"   Reason: {fix.reason}\n\n")

                if medium_confidence:
                    f.write("\nMEDIUM CONFIDENCE FIXES:\n\n")
                    for fix in medium_confidence:
                        f.write(f"Issue: {fix.section}.{fix.field}\n")
                        f.write(f"   Looking for: {fix.current_column}\n")
                        if fix.suggested_column:
                            f.write(f"   → POSSIBLE FIX: Use column '{fix.suggested_column}'\n")
                            f.write(f"   (Review other similar columns mentioned in reason)\n")
                        f.write(f"   Reason: {fix.reason}\n\n")

                if low_confidence:
                    f.write("\nNEEDS INVESTIGATION:\n\n")
                    for fix in low_confidence:
                        f.write(f"Issue: {fix.section}.{fix.field}\n")
                        f.write(f"   Looking for: {fix.current_column}\n")
                        f.write(f"   Reason: {fix.reason}\n\n")

            # Missing tables
            if 'table_not_found' in by_type:
                f.write("\nACTION REQUIRED: Missing Tables\n")
                f.write("-" * 80 + "\n\n")

                for fix in by_type['table_not_found']:
                    f.write(f"Issue: {fix.section}\n")
                    f.write(f"   Reason: {fix.reason}\n\n")

            f.write("=" * 80 + "\n")
            f.write("NEXT STEPS:\n")
            f.write("=" * 80 + "\n")
            f.write("1. Review HIGH CONFIDENCE fixes - these are likely correct\n")
            f.write("2. For grid containers - no action needed, these are working as designed\n")
            f.write("3. For missing columns - update services.yml with 'column' mappings\n")
            f.write("4. For missing tables - create the forms in Joget\n")
            f.write("5. Re-run this utility to verify fixes\n")

        print(f"✓ Generated fixes report: {output_file}")

    def auto_fix_services_yml(self, backup: bool = True) -> bool:
        """
        Automatically fix services.yml based on high-confidence suggestions.
        Creates a backup before making changes.
        """
        if backup:
            backup_file = f"services.yml.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(self.services_yml, backup_file)
            print(f"✓ Created backup: {backup_file}")

        # Load current config
        with open(self.services_yml, 'r') as f:
            config = yaml.safe_load(f)

        changes_made = 0

        # Apply high-confidence fixes
        high_confidence_fixes = [
            f for f in self.mapping_fixes
            if f.confidence == 'high' and f.suggested_column
        ]

        if not high_confidence_fixes:
            print("ℹ No high-confidence auto-fixes available")
            return False

        print(f"\nApplying {len(high_confidence_fixes)} high-confidence fixes...")

        for fix in high_confidence_fixes:
            # Find the field in config
            section_config = config['formMappings'].get(fix.section)
            if not section_config:
                continue

            fields = section_config.get('fields', [])
            for field_def in fields:
                if field_def.get('joget') == fix.field:
                    # Add column mapping
                    field_def['column'] = fix.suggested_column
                    changes_made += 1
                    print(f"  ✓ Fixed {fix.section}.{fix.field}: {fix.current_column} → {fix.suggested_column}")
                    break

        if changes_made > 0:
            # Write updated config
            with open(self.services_yml, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)

            print(f"\n✓ Applied {changes_made} fixes to services.yml")
            return True

        return False

    def generate_mapping_report(self, output_file: str = "field_mapping_report.txt"):
        """Generate a comprehensive text report of field mappings."""
        with open(output_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("JOGET FIELD MAPPING REPORT\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Database: {self.db_config['database']}@{self.db_config['host']}\n")
            f.write(f"Total Mappings: {len(self.field_mappings)}\n")
            f.write("=" * 80 + "\n\n")

            # Group by section
            sections = defaultdict(list)
            for mapping in self.field_mappings:
                sections[mapping.section].append(mapping)

            # Statistics
            valid_count = sum(1 for m in self.field_mappings if m.validation_status == "valid")
            missing_count = sum(1 for m in self.field_mappings if m.validation_status == "missing")
            grid_container_count = sum(1 for m in self.field_mappings if m.validation_status == "grid_container")

            f.write("SUMMARY STATISTICS\n")
            f.write("-" * 80 + "\n")
            f.write(f"Valid Mappings:        {valid_count} ({valid_count / len(self.field_mappings) * 100:.1f}%)\n")
            f.write(f"Grid Containers:       {grid_container_count} (info only)\n")
            f.write(f"Missing Columns:       {missing_count} ({missing_count / len(self.field_mappings) * 100:.1f}%)\n")
            f.write(f"Total Sections:        {len(sections)}\n")
            f.write(f"Total Tables:          {len(self.table_structures)}\n")
            f.write("\n")

            # Detailed mappings by section
            for section_name in sorted(sections.keys()):
                mappings = sections[section_name]
                f.write("=" * 80 + "\n")
                f.write(f"SECTION: {section_name}\n")
                f.write("=" * 80 + "\n")
                f.write(f"Form ID:      {mappings[0].form_id}\n")
                f.write(f"Table Name:   {mappings[0].table_name}\n")
                f.write(f"Is Grid:      {'Yes' if mappings[0].is_grid else 'No'}\n")
                if mappings[0].parent_field:
                    f.write(f"Parent Field: {mappings[0].parent_field}\n")
                f.write(f"Fields:       {len(mappings)}\n")
                f.write("-" * 80 + "\n\n")

                for mapping in mappings:
                    if mapping.validation_status == "valid":
                        status_icon = "✓"
                    elif mapping.validation_status == "grid_container":
                        status_icon = "ℹ"
                    else:
                        status_icon = "✗"

                    f.write(f"{status_icon} {mapping.joget_field}\n")
                    f.write(f"   Column:        {mapping.column_name}\n")
                    if mapping.column_type:
                        f.write(f"   Type:          {mapping.column_type}\n")
                    f.write(f"   GovStack Path: {mapping.govstack_path}\n")
                    if mapping.json_path:
                        f.write(f"   JSON Path:     {mapping.json_path}\n")
                    if mapping.required:
                        f.write(f"   Required:      Yes\n")
                    if mapping.transform:
                        f.write(f"   Transform:     {mapping.transform}\n")
                    if mapping.auto_fix_suggested:
                        f.write(f"   → Suggested:   {mapping.auto_fix_suggested}\n")
                    if mapping.notes:
                        f.write(f"   Notes:         {'; '.join(mapping.notes)}\n")
                    f.write("\n")

                f.write("\n")

        print(f"✓ Generated text report: {output_file}")

    def generate_csv_report(self, output_file: str = "field_mapping_report.csv"):
        """Generate a CSV report of field mappings."""
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'Section',
                'Form ID',
                'Table Name',
                'Joget Field',
                'Column Name',
                'Column Type',
                'GovStack Path',
                'JSON Path',
                'Required',
                'Transform',
                'Is Grid',
                'Parent Field',
                'Exists in DB',
                'Is Grid Container',
                'Status',
                'Suggested Fix',
                'Notes'
            ])

            # Data rows
            for mapping in self.field_mappings:
                writer.writerow([
                    mapping.section,
                    mapping.form_id,
                    mapping.table_name,
                    mapping.joget_field,
                    mapping.column_name,
                    mapping.column_type or '',
                    mapping.govstack_path,
                    mapping.json_path or '',
                    'Yes' if mapping.required else 'No',
                    mapping.transform or '',
                    'Yes' if mapping.is_grid else 'No',
                    mapping.parent_field or '',
                    'Yes' if mapping.exists_in_db else 'No',
                    'Yes' if mapping.is_grid_container else 'No',
                    mapping.validation_status,
                    mapping.auto_fix_suggested or '',
                    '; '.join(mapping.notes)
                ])

        print(f"✓ Generated CSV report: {output_file}")

    def generate_json_report(self, output_file: str = "field_mapping_report.json"):
        """Generate a JSON report of field mappings."""
        report = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'database': f"{self.db_config['database']}@{self.db_config['host']}",
                'total_mappings': len(self.field_mappings),
                'valid_mappings': sum(1 for m in self.field_mappings if m.validation_status == "valid"),
                'grid_containers': sum(1 for m in self.field_mappings if m.validation_status == "grid_container"),
                'missing_mappings': sum(1 for m in self.field_mappings if m.validation_status == "missing"),
                'fixes_suggested': len(self.mapping_fixes)
            },
            'tables': {},
            'mappings': [],
            'suggested_fixes': []
        }

        # Add table structures
        for table_name, struct in self.table_structures.items():
            if struct['exists']:
                report['tables'][table_name] = {
                    'columns': list(struct['columns'].keys()),
                    'column_details': struct['columns']
                }

        # Add field mappings
        for mapping in self.field_mappings:
            report['mappings'].append({
                'section': mapping.section,
                'form_id': mapping.form_id,
                'table_name': mapping.table_name,
                'joget_field': mapping.joget_field,
                'column_name': mapping.column_name,
                'column_type': mapping.column_type,
                'govstack_path': mapping.govstack_path,
                'json_path': mapping.json_path,
                'required': mapping.required,
                'transform': mapping.transform,
                'is_grid': mapping.is_grid,
                'is_grid_container': mapping.is_grid_container,
                'parent_field': mapping.parent_field,
                'exists_in_db': mapping.exists_in_db,
                'validation_status': mapping.validation_status,
                'auto_fix_suggested': mapping.auto_fix_suggested,
                'notes': mapping.notes
            })

        # Add fixes
        for fix in self.mapping_fixes:
            report['suggested_fixes'].append({
                'section': fix.section,
                'field': fix.field,
                'issue_type': fix.issue_type,
                'current_column': fix.current_column,
                'suggested_column': fix.suggested_column,
                'reason': fix.reason,
                'confidence': fix.confidence
            })

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"✓ Generated JSON report: {output_file}")

    def validate_mappings(self) -> Tuple[int, int, int]:
        """Validate all mappings and return (valid_count, grid_container_count, invalid_count)."""
        valid = 0
        grid_containers = 0
        invalid = 0

        print("\n" + "=" * 80)
        print("VALIDATION RESULTS")
        print("=" * 80)

        issues_by_table = defaultdict(list)
        grid_info_by_table = defaultdict(list)

        for mapping in self.field_mappings:
            if mapping.validation_status == "valid":
                valid += 1
            elif mapping.validation_status == "grid_container":
                grid_containers += 1
                grid_info_by_table[mapping.table_name].append(mapping)
            else:
                invalid += 1
                issues_by_table[mapping.table_name].append(mapping)

        # Show grid container info
        if grid_containers > 0:
            print(f"\nℹ Found {grid_containers} grid container field(s) - these are normal:\n")
            for table_name, mappings in sorted(grid_info_by_table.items()):
                print(f"Table: {table_name}")
                for mapping in mappings:
                    print(f"  ℹ {mapping.joget_field} → (grid container, no column needed)")
                print()

        # Show actual issues
        if invalid > 0:
            print(f"⚠ Found {invalid} actual issue(s) across {len(issues_by_table)} table(s):\n")

            for table_name, mappings in sorted(issues_by_table.items()):
                print(f"Table: {table_name}")
                for mapping in mappings:
                    print(f"  ✗ {mapping.joget_field} → {mapping.column_name}")
                    for note in mapping.notes:
                        print(f"      {note}")
                    if mapping.auto_fix_suggested:
                        print(f"      → Suggested fix: use column '{mapping.auto_fix_suggested}'")
                print()
        else:
            print("\n✓ All actual field mappings validated successfully!")
            print("  (Grid containers excluded - they don't need database columns)")

        print(f"\nValidation Summary:")
        print(f"  Valid Fields:      {valid} ({valid / len(self.field_mappings) * 100:.1f}%)")
        print(f"  Grid Containers:   {grid_containers} (info only)")
        print(f"  Issues:            {invalid} ({invalid / len(self.field_mappings) * 100:.1f}%)")

        return valid, grid_containers, invalid

    def run(self, auto_fix: bool = False):
        """Run the complete field mapping analysis."""
        print("\n" + "=" * 80)
        print("JOGET FIELD MAPPER UTILITY v2.0")
        print("=" * 80 + "\n")

        # Step 1: Connect to database
        if not self.connect_to_database():
            sys.exit(1)

        try:
            # Step 2: Load services.yml
            config = self.load_services_yml()

            # Step 3: Process field mappings
            print("\nProcessing field mappings...")
            self.process_field_mappings(config)
            print(f"✓ Processed {len(self.field_mappings)} field mappings")

            # Step 4: Validate mappings
            valid, grid_containers, invalid = self.validate_mappings()

            # Step 5: Generate reports
            print("\nGenerating reports...")
            self.generate_mapping_report()
            self.generate_csv_report()
            self.generate_json_report()

            # Step 6: Generate fixes report
            if self.mapping_fixes:
                self.generate_fixes_report()

            # Step 7: Auto-fix if requested
            if auto_fix and self.mapping_fixes:
                print("\n" + "=" * 80)
                print("AUTO-FIX MODE")
                print("=" * 80)

                high_conf = sum(1 for f in self.mapping_fixes if f.confidence == 'high' and f.suggested_column)
                if high_conf > 0:
                    response = input(f"\nApply {high_conf} high-confidence fixes to services.yml? (yes/no): ")
                    if response.lower() in ['yes', 'y']:
                        if self.auto_fix_services_yml():
                            print("\n✓ Auto-fix complete! Re-run the utility to verify.")
                    else:
                        print("Auto-fix cancelled")
                else:
                    print("No high-confidence fixes available for auto-fix")

            print("\n" + "=" * 80)
            print("ANALYSIS COMPLETE")
            print("=" * 80)
            print("\nGenerated files:")
            print("  - field_mapping_report.txt (detailed text report)")
            print("  - field_mapping_report.csv (spreadsheet-compatible)")
            print("  - field_mapping_report.json (machine-readable)")
            if self.mapping_fixes:
                print("  - field_mapping_fixes.txt (suggested fixes)")

            if invalid > 0:
                print("\n⚠ Issues found! Review field_mapping_fixes.txt for solutions.")

        finally:
            # Clean up
            self.close_connection()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Joget Field Mapper v2.0 - Maps form fields to database columns with auto-fix',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python joget_field_mapper.py
  python joget_field_mapper.py --auto-fix
  python joget_field_mapper.py --env .env.production --services custom_services.yml

Files generated:
  - field_mapping_report.txt: Detailed human-readable report
  - field_mapping_report.csv: Spreadsheet-compatible format
  - field_mapping_report.json: Machine-readable format
  - field_mapping_fixes.txt: Suggested fixes for issues
        """
    )

    parser.add_argument(
        '--env',
        default='.env',
        help='Path to .env file (default: .env)'
    )

    parser.add_argument(
        '--services',
        default='services.yml',
        help='Path to services.yml file (default: services.yml)'
    )

    parser.add_argument(
        '--auto-fix',
        action='store_true',
        help='Automatically fix high-confidence issues in services.yml'
    )

    args = parser.parse_args()

    # Create and run mapper
    mapper = JogetFieldMapper(env_file=args.env, services_yml=args.services)
    mapper.run(auto_fix=args.auto_fix)


if __name__ == '__main__':
    main()