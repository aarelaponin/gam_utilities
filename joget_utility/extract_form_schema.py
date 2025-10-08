#!/usr/bin/env python3
"""
Extract exact database schema from Joget form JSON definitions
This provides 100% accurate table and column mappings from the form definitions
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
import yaml


@dataclass
class FieldInfo:
    """Information about a form field"""
    field_id: str
    label: str = ""
    element_class: str = ""
    column_name: str = ""  # Derived from id with c_ prefix
    properties: Dict[str, Any] = field(default_factory=dict)
    is_grid: bool = False
    grid_fields: List['FieldInfo'] = field(default_factory=list)


@dataclass
class FormInfo:
    """Information about a form and its database mapping"""
    form_id: str
    form_name: str
    table_name: str
    primary_key: str = "id"
    fields: List[FieldInfo] = field(default_factory=list)
    grid_forms: List['FormInfo'] = field(default_factory=list)
    parent_field: Optional[str] = None


class FormSchemaExtractor:
    """Extract database schema from Joget form JSON definitions"""

    def __init__(self, forms_dir: str):
        self.forms_dir = Path(forms_dir)
        self.forms: Dict[str, FormInfo] = {}
        self.table_to_form: Dict[str, str] = {}

    def extract_all(self) -> Dict[str, FormInfo]:
        """Extract schema from all form JSON files"""
        json_files = list(self.forms_dir.glob("*.json"))
        print(f"Found {len(json_files)} form definition files")

        for json_file in sorted(json_files):
            print(f"\nProcessing: {json_file.name}")
            try:
                form_info = self.extract_form_schema(json_file)
                if form_info:
                    self.forms[form_info.form_id] = form_info
                    self.table_to_form[form_info.table_name] = form_info.form_id
                    print(f"  - Form ID: {form_info.form_id}")
                    print(f"  - Table: {form_info.table_name}")
                    print(f"  - Fields: {len(form_info.fields)}")
            except Exception as e:
                print(f"  ERROR: {e}")

        return self.forms

    def extract_form_schema(self, json_file: Path) -> Optional[FormInfo]:
        """Extract schema from a single form JSON file"""
        with open(json_file, 'r') as f:
            data = json.load(f)

        # Handle both direct form definition and wrapped formats
        form_def = None

        # Check for form structure
        if 'className' in data and 'Form' in data.get('className', ''):
            # Direct form definition (Joget export format)
            form_def = data
        elif 'formDefId' in data:
            form_def = data
        elif 'definition' in data:
            form_def = data['definition']
        elif isinstance(data, list) and len(data) > 0:
            form_def = data[0]

        if not form_def:
            print(f"  Could not find form definition in {json_file.name}")
            return None

        # Extract basic form info from properties if they exist
        props = form_def.get('properties', {})

        # Extract basic form info
        form_info = FormInfo(
            form_id=props.get('id', form_def.get('formDefId', '')),
            form_name=props.get('name', form_def.get('name', '')),
            table_name=props.get('tableName', form_def.get('tableName', ''))
        )

        # Extract fields from elements
        if 'elements' in form_def:
            self._extract_fields(form_def['elements'], form_info.fields)

        return form_info

    def _extract_fields(self, elements: List[Dict], target_fields: List[FieldInfo], prefix: str = ""):
        """Recursively extract fields from form elements"""
        for element in elements:
            if not isinstance(element, dict):
                continue

            element_class = element.get('className', '')
            element_id = element.get('properties', {}).get('id', '')
            element_label = element.get('properties', {}).get('label', '')

            # Skip elements without IDs (like sections, columns)
            if not element_id and element_class not in ['org.joget.apps.form.lib.Grid']:
                # Check for nested elements
                if 'elements' in element:
                    self._extract_fields(element['elements'], target_fields, prefix)
                continue

            # Handle different element types
            if 'TextField' in element_class or 'TextArea' in element_class:
                field_info = self._create_field_info(element, prefix)
                target_fields.append(field_info)

            elif 'SelectBox' in element_class or 'Radio' in element_class or 'CheckBox' in element_class:
                field_info = self._create_field_info(element, prefix)
                # Extract options if available
                options = element.get('properties', {}).get('options', [])
                if options:
                    field_info.properties['options'] = options
                target_fields.append(field_info)

            elif 'DatePicker' in element_class:
                field_info = self._create_field_info(element, prefix)
                field_info.properties['date_format'] = element.get('properties', {}).get('format', '')
                target_fields.append(field_info)

            elif 'Grid' in element_class:
                # Grid is a container for sub-form data
                grid_info = FieldInfo(
                    field_id=element_id or 'grid',
                    label=element_label,
                    element_class=element_class,
                    column_name=f"c_{element_id}" if element_id else "",
                    is_grid=True
                )

                # Extract grid columns/fields
                if 'elements' in element:
                    self._extract_fields(element['elements'], grid_info.grid_fields, prefix=element_id)

                target_fields.append(grid_info)

            elif 'SubForm' in element_class:
                # SubForm references another form
                subform_id = element.get('properties', {}).get('formDefId', '')
                parent_field = element.get('properties', {}).get('parentSubFormId', '')

                field_info = FieldInfo(
                    field_id=element_id,
                    label=element_label,
                    element_class=element_class,
                    column_name=f"c_{element_id}",
                    properties={
                        'subform_id': subform_id,
                        'parent_field': parent_field
                    }
                )
                target_fields.append(field_info)

            elif 'Column' in element_class or 'Section' in element_class:
                # These are containers, recursively extract their elements
                if 'elements' in element:
                    self._extract_fields(element['elements'], target_fields, prefix)

            else:
                # Generic field extraction for other types
                if element_id:
                    field_info = self._create_field_info(element, prefix)
                    target_fields.append(field_info)

    def _create_field_info(self, element: Dict, prefix: str = "") -> FieldInfo:
        """Create FieldInfo from element definition"""
        properties = element.get('properties', {})
        field_id = properties.get('id', '')

        # Determine column name (Joget convention: c_ prefix)
        column_name = f"c_{field_id}" if field_id else ""
        if prefix:
            column_name = f"c_{prefix}_{field_id}"

        return FieldInfo(
            field_id=field_id,
            label=properties.get('label', ''),
            element_class=element.get('className', ''),
            column_name=column_name,
            properties={
                'required': properties.get('required', '') == 'true',
                'readonly': properties.get('readonly', '') == 'true',
                'validator': properties.get('validator', {}),
                'value': properties.get('value', '')
            }
        )

    def generate_report(self) -> str:
        """Generate a detailed schema report"""
        report = ["# Form Database Schema Report", ""]
        report.append(f"Total Forms: {len(self.forms)}")
        report.append("")

        for form_id, form_info in sorted(self.forms.items()):
            report.append(f"## Form: {form_info.form_name or form_id}")
            report.append(f"- **Form ID:** `{form_info.form_id}`")
            report.append(f"- **Table Name:** `{form_info.table_name}`")
            report.append(f"- **Primary Key:** `{form_info.primary_key}`")
            report.append(f"- **Total Fields:** {len(form_info.fields)}")
            report.append("")

            if form_info.fields:
                report.append("### Fields:")
                report.append("| Field ID | Column Name | Type | Label | Required |")
                report.append("|----------|-------------|------|-------|----------|")

                for field in form_info.fields:
                    if field.is_grid:
                        report.append(f"| **{field.field_id}** (Grid) | - | Grid | {field.label} | - |")
                        # Show grid fields
                        for grid_field in field.grid_fields:
                            required = "Yes" if grid_field.properties.get('required') else "No"
                            report.append(f"| ↳ {grid_field.field_id} | {grid_field.column_name} | "
                                        f"{grid_field.element_class.split('.')[-1]} | "
                                        f"{grid_field.label} | {required} |")
                    else:
                        required = "Yes" if field.properties.get('required') else "No"
                        element_type = field.element_class.split('.')[-1]
                        report.append(f"| {field.field_id} | {field.column_name} | "
                                    f"{element_type} | {field.label} | {required} |")

            report.append("")
            report.append("---")
            report.append("")

        return "\n".join(report)

    def generate_validation_spec(self, services_yml_path: str) -> Dict:
        """Generate validation specification based on actual schema"""
        # Load services.yml for mapping reference
        with open(services_yml_path, 'r') as f:
            services = yaml.safe_load(f)

        validation = {
            'validation': {
                'description': 'Database validation specification based on actual schema',
                'tables': {}
            }
        }

        for form_id, form_info in self.forms.items():
            if not form_info.table_name:
                continue

            table_spec = {
                'tableName': form_info.table_name,
                'primaryKey': form_info.primary_key,
                'columns': []
            }

            for field in form_info.fields:
                if field.is_grid:
                    # Grid data is in separate table
                    continue

                column = {
                    'name': field.column_name,
                    'fieldId': field.field_id,
                    'type': field.element_class.split('.')[-1],
                    'required': field.properties.get('required', False)
                }

                # Add validation rules if present
                if field.properties.get('validator'):
                    column['validator'] = field.properties['validator']

                table_spec['columns'].append(column)

            validation['validation']['tables'][form_info.table_name] = table_spec

        return validation

    def save_json_schema(self, output_file: str):
        """Save extracted schema as JSON"""
        schema = {
            'forms': {form_id: asdict(form) for form_id, form in self.forms.items()},
            'table_mappings': self.table_to_form
        }

        with open(output_file, 'w') as f:
            json.dump(schema, f, indent=2)

        print(f"Schema saved to: {output_file}")


def main():
    """Main function"""
    # Check for forms directory argument
    if len(sys.argv) < 2:
        forms_dir = "/Users/aarelaponin/IdeaProjects/gs-plugins/doc-forms"
        print(f"Using default forms directory: {forms_dir}")
    else:
        forms_dir = sys.argv[1]

    if not os.path.exists(forms_dir):
        print(f"Error: Forms directory not found: {forms_dir}")
        sys.exit(1)

    # Extract schema
    extractor = FormSchemaExtractor(forms_dir)
    forms = extractor.extract_all()

    # Generate report
    print("\n" + "="*50)
    report = extractor.generate_report()
    print(report)

    # Save outputs
    output_dir = Path("/Users/aarelaponin/PycharmProjects/dev/gam_utilities/joget_utility/schema_output")
    output_dir.mkdir(exist_ok=True)

    # Save markdown report
    report_file = output_dir / "form_schema_report.md"
    with open(report_file, 'w') as f:
        f.write(report)
    print(f"\nReport saved to: {report_file}")

    # Save JSON schema
    json_file = output_dir / "form_schema.json"
    extractor.save_json_schema(str(json_file))

    # Generate validation spec
    services_yml = "/Users/aarelaponin/IdeaProjects/gs-plugins/processing-server/src/main/resources/docs-metadata/services.yml"
    if os.path.exists(services_yml):
        validation_spec = extractor.generate_validation_spec(services_yml)
        validation_file = output_dir / "validation_spec.yml"
        with open(validation_file, 'w') as f:
            yaml.dump(validation_spec, f, default_flow_style=False)
        print(f"Validation spec saved to: {validation_file}")


if __name__ == "__main__":
    main()