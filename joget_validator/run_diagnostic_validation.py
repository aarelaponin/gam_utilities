#!/usr/bin/env python3
"""
Diagnostic Validation Runner
Compares validation spec against actual database state to identify plugin issues
"""

import argparse
import sys
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


class DiagnosticValidator:
    """
    Performs diagnostic validation comparing spec to actual database
    """

    def __init__(self, spec_file: str, verbose: bool = False):
        """Initialize with validation spec"""
        self.verbose = verbose
        self.spec = self._load_spec(spec_file)
        self.db_config = self._get_db_config()
        self.errors = []
        self.warnings = []
        self.passed = []
        self.stats = defaultdict(int)

    def _load_spec(self, spec_file: str) -> Dict:
        """Load validation specification"""
        with open(spec_file, 'r') as f:
            return yaml.safe_load(f)

    def _get_db_config(self) -> Dict:
        """Get database configuration from environment"""
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '3306')),
            'database': os.getenv('DB_NAME', ''),
            'user': os.getenv('DB_USER', ''),
            'password': os.getenv('DB_PASSWORD', '')
        }

    def connect_db(self) -> mysql.connector.MySQLConnection:
        """Connect to database"""
        return mysql.connector.connect(**self.db_config)

    def validate(self) -> Dict[str, Any]:
        """Run complete validation"""
        print("=" * 70)
        print("DIAGNOSTIC VALIDATION REPORT")
        print("=" * 70)
        print(f"Test Case: {self.spec['test_case']['id']}")
        print(f"Farmer: {self.spec['test_case']['farmer_name']}")
        print("-" * 70)

        conn = self.connect_db()
        cursor = conn.cursor(dictionary=True)

        results = {
            'test_case': self.spec['test_case'],
            'timestamp': datetime.now().isoformat(),
            'tables': {}
        }

        # Validate each table
        tables = self.spec['expected_state']['tables']
        for table_name, expected in tables.items():
            print(f"\n▶ Validating table: {table_name}")
            table_result = self._validate_table(cursor, table_name, expected)
            results['tables'][table_name] = table_result

            # Print summary for this table
            if table_result['status'] == 'PASS':
                print(f"  ✅ PASSED - {table_result['actual_count']} records found")
            elif table_result['status'] == 'PARTIAL':
                print(f"  ⚠️  PARTIAL - {table_result.get('passed_fields', 0)}/{table_result.get('total_fields', 0)} fields correct")
            else:
                error_msg = table_result.get('error', '') or ', '.join(table_result.get('errors', [])) or 'Unknown error'
                print(f"  ❌ FAILED - {error_msg}")

        cursor.close()
        conn.close()

        # Generate summary
        results['summary'] = self._generate_summary()

        return results

    def _validate_table(self, cursor, table_name: str, expected: Dict) -> Dict:
        """Validate a single table"""
        result = {
            'table_name': table_name,
            'expected_count': expected['record_count'],
            'actual_count': 0,
            'status': 'UNKNOWN',
            'errors': [],
            'field_results': []
        }

        try:
            # Check if table exists
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            if not cursor.fetchone():
                result['status'] = 'FAILED'
                result['error'] = f"Table does not exist"
                self.errors.append({
                    'type': 'MISSING_TABLE',
                    'table': table_name,
                    'message': f"Table {table_name} does not exist in database"
                })
                return result

            # Get actual records
            parent_id = self.spec['test_case']['id']

            # Build query based on table type
            if 'parent_link' in expected:
                # Grid table - filter by parent
                parent_field = expected['parent_link']
                query = f"SELECT * FROM {table_name} WHERE {parent_field} = %s"
                cursor.execute(query, (parent_id,))
            else:
                # Main form table - filter by id or c_parent_id
                query = f"SELECT * FROM {table_name} WHERE id = %s OR c_parent_id = %s"
                cursor.execute(query, (parent_id, parent_id))

            actual_records = cursor.fetchall()
            result['actual_count'] = len(actual_records)

            # Check record count
            if result['actual_count'] != expected['record_count']:
                result['status'] = 'FAILED'
                error_msg = f"Expected {expected['record_count']} records, found {result['actual_count']}"
                result['errors'].append(error_msg)
                self.errors.append({
                    'type': 'RECORD_COUNT_MISMATCH',
                    'table': table_name,
                    'expected': expected['record_count'],
                    'actual': result['actual_count'],
                    'message': error_msg
                })

                if result['actual_count'] == 0:
                    # No records at all - critical error
                    self.errors.append({
                        'type': 'NO_RECORDS',
                        'table': table_name,
                        'message': f"No records created in {table_name}"
                    })
                    return result
            else:
                # Record count matches, continue with field validation
                result['status'] = 'PASS'  # Will be updated based on field validation

            # Validate field values
            if actual_records and 'records' in expected:
                result['field_results'] = self._validate_fields(
                    table_name,
                    expected['records'],
                    actual_records
                )

                # Calculate pass rate
                total_fields = sum(len(r) for r in result['field_results'])
                passed_fields = sum(
                    1 for r in result['field_results']
                    for f in r.values()
                    if f.get('status') == 'PASS'
                )

                result['total_fields'] = total_fields
                result['passed_fields'] = passed_fields

                if passed_fields == total_fields:
                    result['status'] = 'PASS'
                elif passed_fields > 0:
                    result['status'] = 'PARTIAL'
                else:
                    result['status'] = 'FAILED'

        except Exception as e:
            result['status'] = 'ERROR'
            result['error'] = str(e)
            self.errors.append({
                'type': 'VALIDATION_ERROR',
                'table': table_name,
                'message': str(e)
            })

        return result

    def _validate_fields(self, table_name: str, expected_records: List[Dict],
                        actual_records: List[Dict]) -> List[Dict]:
        """Validate field values"""
        field_results = []

        for i, expected_record in enumerate(expected_records):
            if i >= len(actual_records):
                break

            actual_record = actual_records[i]
            record_result = {}

            for field_name, expected_value in expected_record.items():
                # Skip system fields
                if field_name in ['id', 'dateCreated', 'dateModified',
                                 'createdBy', 'modifiedBy']:
                    continue

                actual_value = actual_record.get(field_name)

                # Compare values
                if self._compare_values(expected_value, actual_value):
                    record_result[field_name] = {
                        'status': 'PASS',
                        'expected': expected_value,
                        'actual': actual_value
                    }
                    self.passed.append({
                        'table': table_name,
                        'field': field_name
                    })
                else:
                    record_result[field_name] = {
                        'status': 'FAIL',
                        'expected': expected_value,
                        'actual': actual_value
                    }

                    # Categorize the error
                    error_type = self._categorize_error(expected_value, actual_value)
                    self.errors.append({
                        'type': error_type,
                        'table': table_name,
                        'field': field_name,
                        'expected': expected_value,
                        'actual': actual_value,
                        'message': f"{field_name}: expected '{expected_value}', got '{actual_value}'"
                    })

            field_results.append(record_result)

        return field_results

    def _compare_values(self, expected: Any, actual: Any) -> bool:
        """Compare two values flexibly"""
        # Handle None/NULL
        if expected == '' and actual is None:
            return True
        if expected is None and actual == '':
            return True

        # Convert to strings for comparison
        expected_str = str(expected) if expected is not None else ''
        actual_str = str(actual) if actual is not None else ''

        # Case-insensitive comparison
        if expected_str.lower() == actual_str.lower():
            return True

        # Handle boolean variations
        bool_true = ['true', '1', 'yes', 't', 'y']
        bool_false = ['false', '0', 'no', 'f', 'n']

        if expected_str.lower() in bool_true and actual_str.lower() in bool_true:
            return True
        if expected_str.lower() in bool_false and actual_str.lower() in bool_false:
            return True

        return False

    def _categorize_error(self, expected: Any, actual: Any) -> str:
        """Categorize the type of error"""
        if actual is None or actual == '':
            if expected:
                return 'MISSING_VALUE'
        elif expected == '' and actual:
            return 'UNEXPECTED_VALUE'
        elif isinstance(expected, bool) or str(expected).lower() in ['true', 'false', 'yes', 'no']:
            return 'BOOLEAN_MISMATCH'
        elif str(expected).replace('-', '').isdigit() and str(actual).replace('-', '').isdigit():
            return 'NUMERIC_MISMATCH'
        else:
            return 'VALUE_MISMATCH'

    def _generate_summary(self) -> Dict:
        """Generate validation summary"""
        # Group errors by type
        error_groups = defaultdict(list)
        for error in self.errors:
            error_groups[error['type']].append(error)

        # Create summary
        summary = {
            'total_errors': len(self.errors),
            'total_warnings': len(self.warnings),
            'total_passed': len(self.passed),
            'error_groups': {}
        }

        # Add error groups with details
        for error_type, errors in error_groups.items():
            summary['error_groups'][error_type] = {
                'count': len(errors),
                'errors': errors[:5]  # First 5 examples
            }

        return summary

    def print_diagnostic_report(self, results: Dict):
        """Print detailed diagnostic report"""
        print("\n" + "=" * 70)
        print("DIAGNOSTIC SUMMARY")
        print("=" * 70)

        summary = results['summary']
        print(f"Total Errors: {summary['total_errors']}")
        print(f"Total Passed: {summary['total_passed']}")

        if summary['error_groups']:
            print("\n" + "=" * 70)
            print("ERROR ANALYSIS")
            print("=" * 70)

            for error_type, group in summary['error_groups'].items():
                print(f"\n▶ {error_type} ({group['count']} instances)")
                print("-" * 50)

                # Show examples
                for error in group['errors'][:3]:
                    if error_type == 'NO_RECORDS':
                        print(f"  • Table {error['table']}: No records created")
                    elif error_type == 'RECORD_COUNT_MISMATCH':
                        print(f"  • Table {error['table']}: Expected {error['expected']}, got {error['actual']}")
                    elif error_type == 'MISSING_VALUE':
                        print(f"  • {error['table']}.{error['field']}: No value saved")
                    else:
                        print(f"  • {error['table']}.{error['field']}: '{error['expected']}' → '{error['actual']}'")

                # Suggest fixes based on error type
                print("\n  💡 Suggested Fix:")
                if error_type == 'NO_RECORDS':
                    print("    - Check if form submission is reaching the database")
                    print("    - Verify TableDataHandler is processing this table")
                    print("    - Check for exceptions in plugin logs")
                elif error_type == 'MISSING_VALUE':
                    print("    - Check if field mapping exists in services.yml")
                    print("    - Verify GovStack path is correct")
                    print("    - Check JsonPathExtractor for this path")
                elif error_type == 'BOOLEAN_MISMATCH':
                    print("    - Add/fix boolean transformation for these fields")
                    print("    - Check yesNoBoolean transformer")
                elif error_type == 'VALUE_MISMATCH':
                    print("    - Check value mapping in services.yml")
                    print("    - Verify transformation is applied")

        print("\n" + "=" * 70)
        print("RECOMMENDED ACTIONS")
        print("=" * 70)

        # Prioritize fixes
        if 'NO_RECORDS' in summary['error_groups']:
            print("\n🔴 CRITICAL: Fix record creation first")
            print("   Tables with no records need immediate attention")
        elif 'RECORD_COUNT_MISMATCH' in summary['error_groups']:
            print("\n🟡 HIGH: Fix record count issues")
            print("   Some records are being created but not all")
        elif 'MISSING_VALUE' in summary['error_groups']:
            print("\n🟢 MEDIUM: Fix field mappings")
            print("   Records exist but fields are not populated")

        return results


def main():
    parser = argparse.ArgumentParser(
        description='Run diagnostic validation against database'
    )

    parser.add_argument(
        '--spec',
        default='generated/test-validation.yml',
        help='Path to validation specification'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--output',
        help='Save results to JSON file'
    )

    args = parser.parse_args()

    # Check spec file exists
    if not Path(args.spec).exists():
        print(f"Error: Validation spec not found: {args.spec}")
        print("Run generate_validation_spec.py first to create the spec")
        sys.exit(1)

    try:
        validator = DiagnosticValidator(args.spec, args.verbose)
        results = validator.validate()
        validator.print_diagnostic_report(results)

        # Save results if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\nResults saved to: {args.output}")

        # Exit with error code if validation failed
        if results['summary']['total_errors'] > 0:
            sys.exit(1)

    except Exception as e:
        print(f"Error running validation: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()