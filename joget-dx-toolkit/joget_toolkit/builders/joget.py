"""
Joget DX platform builder.

Converts canonical format to Joget DX form JSON definitions.

CRITICAL Joget DX Requirements:
1. SelectBox with options must use "optionsBinder" property (NOT "options" array)
2. Table names must be <= 20 characters
3. Form ID must match table name
"""

import json
from pathlib import Path
from typing import Union, Dict, Any, List
import logging

from joget_toolkit.builders.base import BaseBuilder
from joget_toolkit.specs.schema import (
    AppSpec,
    FormSpec,
    FieldSpec,
    FieldType,
    SelectOption,
)


class JogetBuilder(BaseBuilder):
    """Builder for Joget DX platform"""

    # Joget field class names
    FIELD_CLASSES = {
        FieldType.TEXT: "org.joget.apps.form.lib.TextField",
        FieldType.TEXTAREA: "org.joget.apps.form.lib.TextArea",
        FieldType.NUMBER: "org.joget.apps.form.lib.TextField",  # with storeNumeric
        FieldType.SELECT: "org.joget.apps.form.lib.SelectBox",
        FieldType.RADIO: "org.joget.apps.form.lib.Radio",
        FieldType.CHECKBOX: "org.joget.apps.form.lib.CheckBox",
        FieldType.DATE: "org.joget.apps.form.lib.DatePicker",
        FieldType.DATETIME: "org.joget.apps.form.lib.DatePicker",  # with format
        FieldType.TIME: "org.joget.apps.form.lib.TextField",  # with time format
        FieldType.FILE: "org.joget.apps.form.lib.FileUpload",
        FieldType.FOREIGN_KEY: "org.joget.apps.form.lib.SelectBox",  # with FormOptionsBinder
        FieldType.HIDDEN: "org.joget.apps.form.lib.HiddenField",
    }

    def __init__(self, logger: logging.Logger = None):
        """Initialize Joget builder"""
        self.logger = logger or logging.getLogger('joget_toolkit.builders.joget')

    def build(self, app_spec: AppSpec, output_dir: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """
        Build Joget form JSONs from canonical AppSpec.

        Args:
            app_spec: Canonical app specification
            output_dir: Directory to write JSON files
            **kwargs: Options
                overwrite: Overwrite existing files (default: False)

        Returns:
            Dictionary with build results
        """
        output_path = self._ensure_output_dir(output_dir)
        overwrite = kwargs.get('overwrite', False)

        results = {
            'forms_created': [],
            'forms_skipped': [],
            'errors': []
        }

        for form_spec in app_spec.forms:
            try:
                # Build form JSON
                form_json = self.build_form(form_spec)

                # Save to file
                output_file = output_path / f"{form_spec.id}.json"

                if output_file.exists() and not overwrite:
                    self.logger.warning(f"Skipping existing file: {output_file}")
                    results['forms_skipped'].append(form_spec.id)
                    continue

                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(form_json, f, indent=4, ensure_ascii=False)

                self.logger.info(f"✓ Created: {output_file}")
                results['forms_created'].append(str(output_file))

            except Exception as e:
                error_msg = f"Error building form '{form_spec.id}': {e}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)

        return results

    def build_form(self, form_spec: FormSpec, **kwargs) -> Dict[str, Any]:
        """
        Build Joget form JSON from FormSpec.

        Args:
            form_spec: Canonical form specification
            **kwargs: Options (reserved for future use)

        Returns:
            Joget form JSON as dictionary
        """
        # Validate table name length (Joget limit: 20 chars)
        if len(form_spec.table) > 20:
            self.logger.warning(
                f"Form '{form_spec.id}': table name '{form_spec.table}' exceeds 20 characters. "
                f"This may cause issues in Joget DX."
            )

        # Build field elements
        field_elements = []
        for field in form_spec.fields:
            field_element = self._build_field(field, form_spec)
            if field_element:
                field_elements.append(field_element)

        # Build form structure
        form_json = {
            "elements": [{
                "elements": [{
                    "elements": field_elements,
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
                "name": form_spec.name,
                "description": form_spec.description or "",
                "postProcessorRunOn": "create",
                "permission": {
                    "className": "",
                    "properties": {}
                },
                "id": form_spec.id,
                "postProcessor": {
                    "className": "",
                    "properties": {}
                },
                "storeBinder": {
                    "className": "org.joget.apps.form.lib.WorkflowFormBinder",
                    "properties": {}
                },
                "tableName": form_spec.table
            }
        }

        return form_json

    def _build_field(self, field: FieldSpec, form_spec: FormSpec) -> Dict[str, Any]:
        """Build Joget field element from FieldSpec"""
        class_name = self.FIELD_CLASSES.get(field.type)
        if not class_name:
            self.logger.warning(f"Unsupported field type '{field.type}' for field '{field.id}'")
            return None

        # Build base properties
        properties = {
            "label": field.label,
            "id": field.id,
            "placeholder": field.placeholder or "",
            "value": self._convert_default_value(field.default) if field.default else "",
        }

        # Add size/maxlength
        if field.size:
            properties["maxlength"] = str(field.size)
            if field.type == FieldType.TEXT:
                properties["size"] = str(min(field.size, 50))  # Display width

        # Add readonly
        if field.readonly or field.primary_key:
            properties["readonly"] = "true"

        # Add validator (required)
        if field.required or field.unique or field.primary_key:
            if field.unique or field.primary_key:
                # Use DuplicateValueValidator for unique fields
                properties["validator"] = {
                    "className": "org.joget.apps.form.lib.DuplicateValueValidator",
                    "properties": {
                        "formDefId": form_spec.id,
                        "fieldId": field.id,
                        "mandatory": "true" if field.required else ""
                    }
                }
            else:
                # Regular required validator
                properties["validator"] = {
                    "className": "org.joget.apps.form.lib.DefaultValidator",
                    "properties": {
                        "mandatory": "true"
                    }
                }
        else:
            properties["validator"] = {
                "className": "",
                "properties": {}
            }

        # Field-type specific properties
        if field.type == FieldType.NUMBER:
            properties["storeNumeric"] = "true"

        elif field.type == FieldType.DATETIME:
            properties["format"] = "yyyy-MM-dd HH:mm:ss"
            properties["timeFormat"] = "24"

        elif field.type in (FieldType.SELECT, FieldType.RADIO, FieldType.CHECKBOX, FieldType.FOREIGN_KEY):
            # CRITICAL: Use optionsBinder property, NOT options array!
            if field.references:
                # Foreign key: Use FormOptionsBinder
                properties["optionsBinder"] = {
                    "className": "org.joget.apps.form.lib.FormOptionsBinder",
                    "properties": {
                        "formDefId": field.references.form,
                        "idColumn": field.references.field,
                        "labelColumn": field.references.label_field,
                        "groupingColumn": "",
                        "addEmptyOption": "true",
                        "useAjax": ""
                    }
                }
            elif field.options:
                # Static options: Use hardcoded options
                # For Joget, we need to build options list
                options_list = []
                for opt in field.options:
                    options_list.append({
                        "value": opt.value,
                        "label": opt.label or opt.value
                    })

                # For SelectBox with static options, we still use optionsBinder with StaticDatalistSource
                # Or we can use direct options property (different from FormOptionsBinder case!)
                # Actually, for static options, Joget uses "options" array of objects
                properties["options"] = options_list

        # Build field element
        field_element = {
            "className": class_name,
            "properties": properties
        }

        return field_element

    def _convert_default_value(self, default: str) -> str:
        """Convert canonical default values to Joget format"""
        if not default:
            return ""

        # Special default values
        special_defaults = {
            'uuid': '',  # Joget handles UUID via hash variables
            'currentUser': '{currentUser}',  # Joget hash variable
            'currentDateTime': '{currentDateTime}',  # Joget hash variable
        }

        return special_defaults.get(default, default)
