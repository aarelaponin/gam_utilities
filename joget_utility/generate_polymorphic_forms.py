#!/usr/bin/env python3
"""
Generate polymorphic forms for md25equipment and md27input

These are special cases: multi-field forms with parent references and sparse columns.
The standard form generator treats them as nested LOVs, but we need ALL fields visible.
"""

import json
import pandas as pd
from pathlib import Path

def create_md25equipment_form():
    """Create md25equipment form with all 21 fields + parent SelectBox"""

    # Read CSV to get actual columns
    csv_file = Path('data/metadata/md25equipment.csv')
    df = pd.read_csv(csv_file, nrows=1)
    columns = list(df.columns)

    # Build field elements
    fields = []

    #1. Code field (required)
    fields.append({
        "className": "org.joget.apps.form.lib.TextField",
        "properties": {
            "requiredSanitize": "",
            "maxlength": "",
            "validator": {
                "className": "org.joget.apps.form.lib.DefaultValidator",
                "properties": {"mandatory": "true"}
            },
            "label": "Code",
            "id": "code",
            "placeholder": "",
            "value": "",
            "readonlyLabel": ""
        }
    })

    # 2. Name field (required)
    fields.append({
        "className": "org.joget.apps.form.lib.TextField",
        "properties": {
            "requiredSanitize": "",
            "maxlength": "",
            "validator": {
                "className": "org.joget.apps.form.lib.DefaultValidator",
                "properties": {"mandatory": "true"}
            },
            "label": "Name",
            "id": "name",
            "placeholder": "",
            "value": "",
            "readonlyLabel": ""
        }
    })

    # 3. Equipment Category SelectBox (CRITICAL - parent reference)
    fields.append({
        "className": "org.joget.apps.form.lib.SelectBox",
        "properties": {
            "label": "Equipment Category",
            "id": "equipment_category",
            "optionsBinder": {
                "className": "org.joget.apps.form.lib.FormOptionsBinder",
                "properties": {
                    "formDefId": "md25equipmentCategory",
                    "idColumn": "code",
                    "labelColumn": "name",
                    "addEmptyOption": "true",
                    "useAjax": "false"
                }
            },
            "validator": {
                "className": "org.joget.apps.form.lib.DefaultValidator",
                "properties": {"mandatory": "true"}
            }
        }
    })

    # 4-21. All other columns as TextFields
    skip_columns = ['code', 'name', 'equipment_category']
    for col in columns:
        if col in skip_columns:
            continue

        # Format label: estimated_cost_lsl → Estimated Cost Lsl
        label = col.replace('_', ' ').title()

        fields.append({
            "className": "org.joget.apps.form.lib.TextField",
            "properties": {
                "label": label,
                "id": col,
                "placeholder": "",
                "value": ""
            }
        })

    # Build complete form JSON
    form_json = {
        "elements": [{
            "elements": [{
                "elements": fields,
                "className": "org.joget.apps.form.model.Column",
                "properties": {"width": "100%"}
            }],
            "className": "org.joget.apps.form.model.Section",
            "properties": {
                "label": "Section",
                "id": "section1"
            }
        }],
        "className": "org.joget.apps.form.model.Form",
        "properties": {
            "noPermissionMessage": "",
            "loadBinder": {
                "className": "org.joget.apps.form.lib.WorkflowFormBinder",
                "properties": {}
            },
            "name": "MD.25 - Equipment",
            "description": "Equipment catalog with parent category reference. Polymorphic data - different fields apply to different categories.",
            "postProcessorRunOn": "create",
            "permission": {
                "className": "",
                "properties": {}
            },
            "id": "md25equipment",
            "postProcessor": {
                "className": "",
                "properties": {}
            },
            "storeBinder": {
                "className": "org.joget.apps.form.lib.WorkflowFormBinder",
                "properties": {}
            },
            "tableName": "md25equipment"
        }
    }

    return form_json


def create_md27input_form():
    """Create md27input form with all 10 fields + parent SelectBox"""

    # Read CSV to get actual columns
    csv_file = Path('data/metadata/md27input.csv')
    df = pd.read_csv(csv_file, nrows=1)
    columns = list(df.columns)

    # Build field elements
    fields = []

    # 1. Code field (required)
    fields.append({
        "className": "org.joget.apps.form.lib.TextField",
        "properties": {
            "requiredSanitize": "",
            "maxlength": "",
            "validator": {
                "className": "org.joget.apps.form.lib.DefaultValidator",
                "properties": {"mandatory": "true"}
            },
            "label": "Code",
            "id": "code",
            "placeholder": "",
            "value": "",
            "readonlyLabel": ""
        }
    })

    # 2. Name field (required)
    fields.append({
        "className": "org.joget.apps.form.lib.TextField",
        "properties": {
            "requiredSanitize": "",
            "maxlength": "",
            "validator": {
                "className": "org.joget.apps.form.lib.DefaultValidator",
                "properties": {"mandatory": "true"}
            },
            "label": "Name",
            "id": "name",
            "placeholder": "",
            "value": "",
            "readonlyLabel": ""
        }
    })

    # 3. Input Category SelectBox (CRITICAL - parent reference)
    fields.append({
        "className": "org.joget.apps.form.lib.SelectBox",
        "properties": {
            "label": "Input Category",
            "id": "input_category",
            "optionsBinder": {
                "className": "org.joget.apps.form.lib.FormOptionsBinder",
                "properties": {
                    "formDefId": "md27inputCategory",
                    "idColumn": "code",
                    "labelColumn": "name",
                    "addEmptyOption": "true",
                    "useAjax": "false"
                }
            },
            "validator": {
                "className": "org.joget.apps.form.lib.DefaultValidator",
                "properties": {"mandatory": "true"}
            }
        }
    })

    # 4-10. All other columns as TextFields
    skip_columns = ['code', 'name', 'input_category']
    for col in columns:
        if col in skip_columns:
            continue

        # Format label
        label = col.replace('_', ' ').title()

        fields.append({
            "className": "org.joget.apps.form.lib.TextField",
            "properties": {
                "label": label,
                "id": col,
                "placeholder": "",
                "value": ""
            }
        })

    # Build complete form JSON
    form_json = {
        "elements": [{
            "elements": [{
                "elements": fields,
                "className": "org.joget.apps.form.model.Column",
                "properties": {"width": "100%"}
            }],
            "className": "org.joget.apps.form.model.Section",
            "properties": {
                "label": "Section",
                "id": "section1"
            }
        }],
        "className": "org.joget.apps.form.model.Form",
        "properties": {
            "noPermissionMessage": "",
            "loadBinder": {
                "className": "org.joget.apps.form.lib.WorkflowFormBinder",
                "properties": {}
            },
            "name": "MD.27 - Input",
            "description": "Agricultural input catalog with parent category reference. Polymorphic data - different fields apply to different categories.",
            "postProcessorRunOn": "create",
            "permission": {
                "className": "",
                "properties": {}
            },
            "id": "md27input",
            "postProcessor": {
                "className": "",
                "properties": {}
            },
            "storeBinder": {
                "className": "org.joget.apps.form.lib.WorkflowFormBinder",
                "properties": {}
            },
            "tableName": "md27input"
        }
    }

    return form_json


if __name__ == '__main__':
    print("=" * 80)
    print("GENERATING POLYMORPHIC FORMS")
    print("=" * 80)
    print()

    # Generate md25equipment
    print("Generating md25equipment.json...")
    md25_form = create_md25equipment_form()
    output_file = Path('data/metadata_forms/md25equipment.json')
    with open(output_file, 'w') as f:
        json.dump(md25_form, f, indent=4)

    field_count = len(md25_form['elements'][0]['elements'][0]['elements'])
    print(f"✓ Created: {output_file}")
    print(f"  Fields: {field_count}")
    print(f"  Table: {md25_form['properties']['tableName']}")
    print()

    # Generate md27input
    print("Generating md27input.json...")
    md27_form = create_md27input_form()
    output_file = Path('data/metadata_forms/md27input.json')
    with open(output_file, 'w') as f:
        json.dump(md27_form, f, indent=4)

    field_count = len(md27_form['elements'][0]['elements'][0]['elements'])
    print(f"✓ Created: {output_file}")
    print(f"  Fields: {field_count}")
    print(f"  Table: {md27_form['properties']['tableName']}")
    print()

    print("=" * 80)
    print("✓ Generation complete!")
    print("=" * 80)
