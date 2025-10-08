#!/usr/bin/env python3
"""
Database Schema Inspector for Joget
Connects to the actual database and extracts the real schema information
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
from typing import Dict, List, Any
import json
from datetime import datetime

# Load environment variables
load_dotenv()


class SchemaInspector:
    """Inspect actual database schema from MySQL"""

    def __init__(self):
        """Initialize with database credentials from .env"""
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '3306')),
            'database': os.getenv('DB_NAME', ''),
            'user': os.getenv('DB_USER', ''),
            'password': os.getenv('DB_PASSWORD', '')
        }

        if not self.config['database'] or not self.config['user']:
            raise ValueError("Database credentials not found in .env file")

        print(f"Connecting to database: {self.config['database']} on {self.config['host']}:{self.config['port']}")

    def connect(self):
        """Create database connection"""
        try:
            conn = mysql.connector.connect(**self.config)
            if conn.is_connected():
                print("✓ Successfully connected to database")
                return conn
        except Error as e:
            print(f"✗ Error connecting to database: {e}")
            raise

    def get_all_tables(self, conn) -> List[str]:
        """Get all tables in the database"""
        cursor = conn.cursor()
        tables = []

        try:
            # Get all tables
            cursor.execute("SHOW TABLES")
            all_tables = cursor.fetchall()

            # Filter for relevant tables
            for (table_name,) in all_tables:
                # Look for farmer-related tables
                if any(keyword in table_name.lower() for keyword in
                      ['farmer', 'farm', 'household', 'crop', 'livestock', 'income', 'declaration', 'registry']):
                    tables.append(table_name)

            print(f"\nFound {len(tables)} relevant tables")
            return sorted(tables)

        finally:
            cursor.close()

    def get_table_structure(self, conn, table_name: str) -> Dict[str, Any]:
        """Get detailed structure of a table"""
        cursor = conn.cursor(dictionary=True)
        structure = {
            'table_name': table_name,
            'columns': [],
            'primary_key': None,
            'foreign_keys': [],
            'indexes': [],
            'row_count': 0
        }

        try:
            # Get column information
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = cursor.fetchall()

            for col in columns:
                column_info = {
                    'name': col['Field'],
                    'type': col['Type'],
                    'nullable': col['Null'] == 'YES',
                    'key': col['Key'],
                    'default': col['Default'],
                    'extra': col['Extra']
                }
                structure['columns'].append(column_info)

                # Identify primary key
                if col['Key'] == 'PRI':
                    structure['primary_key'] = col['Field']

            # Get row count
            cursor.execute(f"SELECT COUNT(*) as count FROM `{table_name}`")
            result = cursor.fetchone()
            structure['row_count'] = result['count']

            # Get foreign keys from INFORMATION_SCHEMA
            cursor.execute("""
                SELECT
                    COLUMN_NAME,
                    REFERENCED_TABLE_NAME,
                    REFERENCED_COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = %s
                AND TABLE_NAME = %s
                AND REFERENCED_TABLE_NAME IS NOT NULL
            """, (self.config['database'], table_name))

            foreign_keys = cursor.fetchall()
            for fk in foreign_keys:
                structure['foreign_keys'].append({
                    'column': fk['COLUMN_NAME'],
                    'references_table': fk['REFERENCED_TABLE_NAME'],
                    'references_column': fk['REFERENCED_COLUMN_NAME']
                })

            # Get indexes
            cursor.execute(f"SHOW INDEX FROM `{table_name}`")
            indexes = cursor.fetchall()
            unique_indexes = {}
            for idx in indexes:
                index_name = idx['Key_name']
                if index_name not in unique_indexes:
                    unique_indexes[index_name] = {
                        'name': index_name,
                        'unique': not idx['Non_unique'],
                        'columns': []
                    }
                unique_indexes[index_name]['columns'].append(idx['Column_name'])

            structure['indexes'] = list(unique_indexes.values())

            return structure

        finally:
            cursor.close()

    def get_sample_data(self, conn, table_name: str, limit: int = 3) -> List[Dict]:
        """Get sample data from table"""
        cursor = conn.cursor(dictionary=True)
        samples = []

        try:
            cursor.execute(f"SELECT * FROM `{table_name}` LIMIT {limit}")
            samples = cursor.fetchall()

            # Convert datetime objects to strings for JSON serialization
            for sample in samples:
                for key, value in sample.items():
                    if isinstance(value, datetime):
                        sample[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(value, bytes):
                        sample[key] = value.decode('utf-8', errors='ignore')

            return samples

        finally:
            cursor.close()

    def inspect_schema(self) -> Dict[str, Any]:
        """Main method to inspect entire schema"""
        conn = self.connect()
        schema_info = {
            'database': self.config['database'],
            'inspected_at': datetime.now().isoformat(),
            'tables': {}
        }

        try:
            # Get all relevant tables
            tables = self.get_all_tables(conn)

            for table in tables:
                print(f"\nInspecting table: {table}")

                # Get table structure
                structure = self.get_table_structure(conn, table)

                # Get sample data if table has rows
                if structure['row_count'] > 0:
                    structure['sample_data'] = self.get_sample_data(conn, table)

                schema_info['tables'][table] = structure

                # Print summary
                print(f"  - Columns: {len(structure['columns'])}")
                print(f"  - Primary Key: {structure['primary_key']}")
                print(f"  - Row Count: {structure['row_count']}")

                # Show column names
                column_names = [col['name'] for col in structure['columns']]
                print(f"  - Column Names: {', '.join(column_names[:5])}")
                if len(column_names) > 5:
                    print(f"                  ... and {len(column_names) - 5} more")

            return schema_info

        finally:
            if conn.is_connected():
                conn.close()

    def generate_report(self, schema_info: Dict[str, Any]) -> str:
        """Generate markdown report of schema"""
        report = []
        report.append("# Database Schema Inspection Report")
        report.append(f"\n**Database:** `{schema_info['database']}`")
        report.append(f"**Inspected:** {schema_info['inspected_at']}")
        report.append(f"**Total Tables Found:** {len(schema_info['tables'])}")

        # Summary table
        report.append("\n## Tables Summary\n")
        report.append("| Table Name | Columns | Primary Key | Row Count |")
        report.append("|------------|---------|-------------|-----------|")

        for table_name, info in sorted(schema_info['tables'].items()):
            report.append(f"| `{table_name}` | {len(info['columns'])} | "
                         f"`{info['primary_key']}` | {info['row_count']:,} |")

        # Detailed table information
        report.append("\n## Detailed Table Structures\n")

        for table_name, info in sorted(schema_info['tables'].items()):
            report.append(f"\n### Table: `{table_name}`\n")
            report.append(f"- **Row Count:** {info['row_count']:,}")
            report.append(f"- **Primary Key:** `{info['primary_key']}`")

            # Columns
            report.append("\n#### Columns:\n")
            report.append("| Column Name | Type | Nullable | Key | Default | Extra |")
            report.append("|-------------|------|----------|-----|---------|-------|")

            for col in info['columns']:
                nullable = "YES" if col['nullable'] else "NO"
                key = col['key'] or "-"
                default = col['default'] if col['default'] is not None else "NULL"
                extra = col['extra'] or "-"

                report.append(f"| `{col['name']}` | {col['type']} | {nullable} | "
                             f"{key} | {default} | {extra} |")

            # Foreign Keys
            if info['foreign_keys']:
                report.append("\n#### Foreign Keys:\n")
                for fk in info['foreign_keys']:
                    report.append(f"- `{fk['column']}` → "
                                 f"`{fk['references_table']}.{fk['references_column']}`")

            # Sample Data
            if 'sample_data' in info and info['sample_data']:
                report.append("\n#### Sample Data:\n")
                report.append("```json")
                report.append(json.dumps(info['sample_data'][0], indent=2))
                report.append("```")

            report.append("\n---")

        return "\n".join(report)


def main():
    """Main function"""
    print("=" * 50)
    print("Joget Database Schema Inspector")
    print("=" * 50)

    try:
        inspector = SchemaInspector()

        # Inspect schema
        schema_info = inspector.inspect_schema()

        # Save raw data as JSON
        json_file = "schema_inspection.json"
        with open(json_file, 'w') as f:
            json.dump(schema_info, f, indent=2, default=str)
        print(f"\n✓ Raw schema data saved to: {json_file}")

        # Generate markdown report
        report = inspector.generate_report(schema_info)

        # Save report
        report_file = "ACTUAL_DATABASE_SCHEMA.md"
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"✓ Schema report saved to: {report_file}")

        # Print summary
        print("\n" + "=" * 50)
        print("SUMMARY OF FINDINGS:")
        print("-" * 50)

        # Check table naming convention
        app_fd_tables = [t for t in schema_info['tables'] if t.startswith('app_fd_')]
        other_tables = [t for t in schema_info['tables'] if not t.startswith('app_fd_')]

        if app_fd_tables:
            print(f"\n✓ Found {len(app_fd_tables)} tables with 'app_fd_' prefix:")
            for table in app_fd_tables[:5]:
                print(f"  - {table}")
            if len(app_fd_tables) > 5:
                print(f"  ... and {len(app_fd_tables) - 5} more")

        if other_tables:
            print(f"\n✓ Found {len(other_tables)} tables without 'app_fd_' prefix:")
            for table in other_tables[:5]:
                print(f"  - {table}")
            if len(other_tables) > 5:
                print(f"  ... and {len(other_tables) - 5} more")

        # Check column naming convention
        c_prefix_columns = 0
        total_columns = 0

        for table_info in schema_info['tables'].values():
            for col in table_info['columns']:
                total_columns += 1
                if col['name'].startswith('c_'):
                    c_prefix_columns += 1

        print(f"\n✓ Column naming convention:")
        print(f"  - {c_prefix_columns}/{total_columns} columns use 'c_' prefix")
        print(f"  - {(c_prefix_columns/total_columns*100):.1f}% of columns follow the convention")

        print("\n" + "=" * 50)
        print("Inspection complete!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()