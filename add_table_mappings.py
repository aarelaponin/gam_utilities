#!/usr/bin/env python3
"""
Script to add 'table' property to all fields in form_structure.yaml
Preserves existing 'column' properties and adds 'table' property after 'type'
"""

import yaml
import sys
from pathlib import Path

def add_table_to_fields(data):
    """Add table property to all fields in the form structure"""

    stats = {
        'forms_processed': 0,
        'fields_updated': 0,
        'sections_fields': 0,
        'all_fields': 0,
        'grid_fields': 0
    }

    forms = data.get('forms', {})

    for form_key, form_data in forms.items():
        stats['forms_processed'] += 1
        table_name = form_data.get('table_name')

        if not table_name:
            print(f"Warning: Form {form_key} has no table_name")
            continue

        # Process sections.fields
        sections = form_data.get('sections', [])
        for section in sections:
            fields = section.get('fields', [])
            for field in fields:
                if 'type' in field and 'table' not in field:
                    # Insert 'table' after 'type'
                    field_copy = dict(field)
                    field.clear()
                    for key, value in field_copy.items():
                        field[key] = value
                        if key == 'type':
                            field['table'] = table_name
                    stats['fields_updated'] += 1
                    stats['sections_fields'] += 1

        # Process all_fields
        all_fields = form_data.get('all_fields', [])
        for field in all_fields:
            if 'type' in field and 'table' not in field:
                # Insert 'table' after 'type'
                field_copy = dict(field)
                field.clear()
                for key, value in field_copy.items():
                    field[key] = value
                    if key == 'type':
                        field['table'] = table_name
                stats['fields_updated'] += 1
                stats['all_fields'] += 1

        # Process grids (both in sections and all_fields)
        all_grids = []

        # Collect grids from sections
        for section in sections:
            all_grids.extend(section.get('grids', []))

        # Collect grids from all_fields level
        all_grids.extend(form_data.get('grids', []))

        for grid in all_grids:
            sub_form_id = grid.get('sub_form_id')
            if sub_form_id and sub_form_id in forms:
                sub_form_table = forms[sub_form_id].get('table_name')
                if sub_form_table:
                    sub_form_fields = grid.get('sub_form_fields', [])
                    for field in sub_form_fields:
                        if 'type' in field and 'table' not in field:
                            # Insert 'table' after 'type'
                            field_copy = dict(field)
                            field.clear()
                            for key, value in field_copy.items():
                                field[key] = value
                                if key == 'type':
                                    field['table'] = sub_form_table
                            stats['fields_updated'] += 1
                            stats['grid_fields'] += 1

    return stats

def main():
    yaml_file = Path('/Users/aarelaponin/PycharmProjects/dev/gam/joget_services/form_structure.yaml')

    if not yaml_file.exists():
        print(f"Error: File not found: {yaml_file}")
        sys.exit(1)

    print(f"Reading {yaml_file}...")
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    print("Adding table properties to fields...")
    stats = add_table_to_fields(data)

    # Write back
    output_file = yaml_file
    print(f"Writing updated YAML to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=1000)

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Forms processed: {stats['forms_processed']}")
    print(f"Total fields updated: {stats['fields_updated']}")
    print(f"  - Section fields: {stats['sections_fields']}")
    print(f"  - All_fields array: {stats['all_fields']}")
    print(f"  - Grid sub_form_fields: {stats['grid_fields']}")
    print("="*60)

    return 0

if __name__ == '__main__':
    sys.exit(main())