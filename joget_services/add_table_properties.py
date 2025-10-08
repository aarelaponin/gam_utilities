#!/usr/bin/env python3
"""Quick script to add 'table' property to all fields in form_structure.yaml"""

import yaml

# Read YAML
with open('form_structure.yaml', 'r') as f:
    data = yaml.safe_load(f)

count = 0
forms = data.get('forms', {})

for form_key, form_data in forms.items():
    table_name = form_data.get('table_name')
    if not table_name:
        continue

    # Update sections.fields
    for section in form_data.get('sections', []):
        for field in section.get('fields', []):
            if 'type' in field and 'table' not in field:
                field['table'] = table_name
                count += 1

        # Update grids.sub_form_fields in sections
        for grid in section.get('grids', []):
            sub_form_id = grid.get('sub_form_id')
            if sub_form_id and sub_form_id in forms:
                sub_table = forms[sub_form_id].get('table_name')
                if sub_table:
                    for field in grid.get('sub_form_fields', []):
                        if 'type' in field and 'table' not in field:
                            field['table'] = sub_table
                            count += 1

    # Update all_fields
    for field in form_data.get('all_fields', []):
        if 'type' in field and 'table' not in field:
            field['table'] = table_name
            count += 1

    # Update grids.sub_form_fields at form level
    for grid in form_data.get('grids', []):
        sub_form_id = grid.get('sub_form_id')
        if sub_form_id and sub_form_id in forms:
            sub_table = forms[sub_form_id].get('table_name')
            if sub_table:
                for field in grid.get('sub_form_fields', []):
                    if 'type' in field and 'table' not in field:
                        field['table'] = sub_table
                        count += 1

# Write back
with open('form_structure.yaml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=1000)

print(f"Added 'table' property to {count} fields")
