#!/usr/bin/env python3
"""
Nested LOV False Positive Fixer
Fixes false positive nested LOVs by converting SelectBox → TextField.

SINGLE RESPONSIBILITY: Transform form JSONs to fix detection errors
Does NOT: Validate, generate, or deploy
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

from .nested_lov_validator import ValidationReport, NestedLOVReference


class NestedLOVFixer:
    """
    Fix false positive nested LOVs by converting SelectBox to TextField.

    Single Responsibility: Transform form JSON structure

    Fixes:
    1. Convert SelectBox elements to TextField
    2. Preserve field ID and label
    3. Remove SelectBox-specific properties (options, etc.)
    """

    def __init__(self, forms_dir: Path, logger: Optional[logging.Logger] = None):
        """
        Initialize fixer

        Args:
            forms_dir: Directory containing form JSON files
            logger: Logger instance (optional)
        """
        self.forms_dir = Path(forms_dir)
        self.logger = logger or logging.getLogger('joget_utility.nested_lov_fixer')
        self.backup_dir = self.forms_dir / '.backups'

    def fix_all_false_positives(self, report: ValidationReport, create_backup: bool = True) -> Dict[str, Any]:
        """
        Fix all false positive nested LOVs from validation report.

        Args:
            report: ValidationReport from nested_lov_validator
            create_backup: Whether to backup original files before modifying

        Returns:
            Summary dict with fix results
        """
        # Collect all references that need fixing
        to_fix = report.false_positives + report.missing_parents

        if not to_fix:
            self.logger.info("No false positives to fix")
            return {
                'total': 0,
                'fixed': 0,
                'failed': 0,
                'results': []
            }

        self.logger.info(f"Fixing {len(to_fix)} false positive nested LOVs")

        # Create backup directory if needed
        if create_backup:
            self.backup_dir.mkdir(exist_ok=True)

        results = {
            'total': len(to_fix),
            'fixed': 0,
            'failed': 0,
            'results': []
        }

        for ref in to_fix:
            result = self._fix_single_reference(ref, create_backup)
            results['results'].append(result)

            if result['success']:
                results['fixed'] += 1
            else:
                results['failed'] += 1

        return results

    def _fix_single_reference(self, ref: NestedLOVReference, create_backup: bool) -> Dict[str, Any]:
        """
        Fix a single false positive nested LOV reference.

        Args:
            ref: NestedLOVReference to fix
            create_backup: Whether to backup before modifying

        Returns:
            Result dict with fix details
        """
        result = {
            'form': ref.child_form,
            'column': ref.column_name,
            'success': False,
            'error': None
        }

        try:
            # Find form JSON file
            form_file = self.forms_dir / f"{ref.child_form}.json"

            if not form_file.exists():
                result['error'] = f"Form file not found: {form_file}"
                return result

            # Load form JSON
            with open(form_file, 'r', encoding='utf-8') as f:
                form_json = json.load(f)

            # Backup if requested
            if create_backup:
                backup_file = self.backup_dir / f"{ref.child_form}.json.backup"
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(form_json, f, indent=4, ensure_ascii=False)
                result['backup'] = str(backup_file)

            # Find and convert SelectBox to TextField
            modified = self._convert_selectbox_to_textfield(form_json, ref.column_name)

            if not modified:
                result['error'] = f"SelectBox for '{ref.column_name}' not found in form"
                return result

            # Save modified form
            with open(form_file, 'w', encoding='utf-8') as f:
                json.dump(form_json, f, indent=4, ensure_ascii=False)

            result['success'] = True
            result['file'] = str(form_file)
            self.logger.info(f"✓ Fixed {ref.child_form} ({ref.column_name}): SelectBox → TextField")

        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"✗ Failed to fix {ref.child_form}: {e}")

        return result

    def _convert_selectbox_to_textfield(self, form_json: Dict[str, Any], field_id: str) -> bool:
        """
        Find SelectBox element and convert it to TextField.

        Recursively searches form structure and modifies in-place.

        Args:
            form_json: Form JSON structure
            field_id: Field ID to find and convert

        Returns:
            True if element was found and converted, False otherwise
        """
        return self._recursive_convert(form_json, field_id)

    def _recursive_convert(self, obj: Any, field_id: str) -> bool:
        """
        Recursively search and convert SelectBox to TextField.

        Args:
            obj: Current object in form structure (dict or list)
            field_id: Field ID to find

        Returns:
            True if element was found and converted
        """
        if isinstance(obj, dict):
            # Check if this is the SelectBox we're looking for
            if (obj.get('className') == 'org.joget.apps.form.lib.SelectBox' and
                obj.get('properties', {}).get('id') == field_id):

                # Convert to TextField
                label = obj.get('properties', {}).get('label', field_id.replace('_', ' ').title())

                obj['className'] = 'org.joget.apps.form.lib.TextField'
                obj['properties'] = {
                    'label': label,
                    'id': field_id,
                    'placeholder': '',
                    'value': '',
                    'requiredSanitize': '',
                    'maxlength': '',
                    'validator': {
                        'className': '',
                        'properties': {}
                    },
                    'encryption': '',
                    'readonly': '',
                    'size': '',
                    'workflowVariable': '',
                    'style': '',
                    'readonlyLabel': '',
                    'storeNumeric': ''
                }

                return True

            # Recursively search in nested dicts
            for value in obj.values():
                if self._recursive_convert(value, field_id):
                    return True

        elif isinstance(obj, list):
            # Recursively search in lists
            for item in obj:
                if self._recursive_convert(item, field_id):
                    return True

        return False

    def print_fix_summary(self, results: Dict[str, Any]) -> None:
        """
        Print human-readable fix summary.

        Args:
            results: Results dict from fix_all_false_positives
        """
        print("\n" + "=" * 70)
        print("Nested LOV Fix Summary")
        print("=" * 70)
        print(f"Total forms to fix: {results['total']}")
        print(f"Successfully fixed: {results['fixed']}")
        print(f"Failed: {results['failed']}")
        print()

        if results['fixed'] > 0:
            print("✓ Fixed forms:")
            for result in results['results']:
                if result['success']:
                    print(f"  • {result['form']} ({result['column']})")
                    if 'backup' in result:
                        print(f"    Backup: {result['backup']}")
            print()

        if results['failed'] > 0:
            print("✗ Failed to fix:")
            for result in results['results']:
                if not result['success']:
                    print(f"  • {result['form']} ({result['column']})")
                    print(f"    Error: {result['error']}")
            print()

        if results['fixed'] > 0:
            print(f"✓ {results['fixed']} form(s) ready for deployment!")
            print()


# Standalone execution
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        print("Usage: python nested_lov_fixer.py <metadata_dir> <forms_dir>")
        sys.exit(1)

    from nested_lov_validator import NestedLOVValidator

    metadata_dir = Path(sys.argv[1])
    forms_dir = Path(sys.argv[2])

    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # Run validation
    print("Step 1: Validating nested LOVs...")
    validator = NestedLOVValidator(metadata_dir)
    report = validator.validate_all()
    validator.print_report(report)

    # Run fixer
    print("\nStep 2: Fixing false positives...")
    fixer = NestedLOVFixer(forms_dir)
    results = fixer.fix_all_false_positives(report, create_backup=True)
    fixer.print_fix_summary(results)
