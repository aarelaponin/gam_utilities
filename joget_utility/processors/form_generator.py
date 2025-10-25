#!/usr/bin/env python3
"""
Metadata Form Generator
Generates Joget form JSON definitions from CSV metadata files.

SINGLE RESPONSIBILITY: Transform CSV structure → Joget Form JSON
Does NOT: Deploy forms, check existence, or populate data

CRITICAL JOGET FORM STRUCTURE REQUIREMENTS:

1. SelectBox with FormOptionsBinder:
   ✅ CORRECT:   "optionsBinder": { "className": "FormOptionsBinder", ... }
   ❌ WRONG:     "options": [{ "className": "FormOptionsBinder", ... }]

   Joget will REJECT forms with array-wrapped options. The optionsBinder
   must be a direct property, not an array element.

2. Table Name Constraints:
   - Maximum 20 characters
   - Must detect collisions when truncating
   - Validated in _validate_table_name()

3. Parent Form ID Resolution:
   - Scan metadata directory for actual form IDs
   - Match by removing mdNN prefix
   - Fallback to camelCase derivation if no match
   - Implemented in _derive_parent_form_id()

See: docs/FORM_GENERATOR_GUIDE.md for complete documentation
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging

from .csv_processor import CSVProcessor


@dataclass
class CSVStructure:
    """Structure analysis result for a CSV file"""
    columns: List[str]
    column_count: int
    has_parent_ref: bool
    parent_ref_column: Optional[str]
    field_types: Dict[str, str]
    form_type: str  # 'simple', 'nested_lov', 'nested_lov_pattern2', 'multi_field'

    # Pattern 2 specific fields
    is_pattern2_child: bool = False
    pattern2_parent_form: Optional[str] = None
    pattern2_fk_field: Optional[str] = None
    pattern2_category_value: Optional[str] = None


class MetadataFormGenerator:
    """
    Generate Joget form JSON definitions from CSV metadata files.

    Single Responsibility: CSV structure → Form JSON

    Supported form types:
    - Simple metadata: code + name (2 fields)
    - Nested LOV: code + parent_ref + name (3+ fields with parent reference)
    - Multi-field: code + name + additional fields
    """

    # Pattern to detect parent reference columns
    PARENT_REF_PATTERNS = [
        r'.*_category$',
        r'.*_type$',
        r'.*_group$',
        r'^parent_.*',
        r'.*_parent$'
    ]

    def __init__(self,
                 config: Optional[Dict[str, Any]] = None,
                 templates_dir: Optional[str] = None,
                 logger: Optional[logging.Logger] = None):
        """
        Initialize form generator

        Args:
            config: Configuration dictionary (from joget.yaml) with subcategory_mappings
            templates_dir: Directory containing form templates (optional)
            logger: Logger instance (optional)
        """
        self.config = config or {}
        self.templates_dir = Path(templates_dir) if templates_dir else None
        self.logger = logger or logging.getLogger('joget_utility.form_generator')
        self.csv_processor = CSVProcessor()

        # Load Pattern 2 mappings from config
        self.subcategory_mappings = self.config.get('subcategory_mappings', {})

        # Track generated table names to detect collisions
        self.generated_table_names = set()

    def generate_from_csv(self, csv_path: Path, form_id: Optional[str] = None,
                          form_name: Optional[str] = None,
                          table_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate Joget form JSON definition from CSV file.

        Args:
            csv_path: Path to CSV file
            form_id: Override form ID (default: derived from filename)
            form_name: Override form name (default: derived from filename)
            table_name: Override table name (default: same as form_id)

        Returns:
            Joget form JSON definition as dictionary

        Raises:
            ValueError: If CSV structure is invalid
            FileNotFoundError: If CSV file doesn't exist
        """
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        # Analyze CSV structure
        structure = self.analyze_csv_structure(csv_path)

        # Derive form properties from filename if not provided
        if not form_id:
            form_id = self._derive_form_id(csv_path)
        if not form_name:
            form_name = self._derive_form_name(csv_path)
        if not table_name:
            table_name = form_id

        # Validate table name length and check for collisions
        table_name = self._validate_table_name(table_name, form_id)

        self.logger.info(f"Generating form: {form_id} (type: {structure.form_type})")
        self.logger.info(f"  Columns: {', '.join(structure.columns)}")
        if structure.has_parent_ref:
            self.logger.info(f"  Parent reference: {structure.parent_ref_column}")

        # Generate form based on type
        if structure.form_type == 'simple':
            form_json = self.generate_simple_form(form_id, form_name, table_name, structure)
        elif structure.form_type == 'nested_lov':
            form_json = self.generate_nested_lov_form(form_id, form_name, table_name, structure)
        elif structure.form_type == 'nested_lov_pattern2':
            # Pattern 2: FK field must be INJECTED
            form_json = self.generate_pattern2_nested_lov_form(form_id, form_name, table_name, structure)
        else:  # multi_field
            form_json = self.generate_multi_field_form(form_id, form_name, table_name, structure)

        return form_json

    def analyze_csv_structure(self, csv_path: Path) -> CSVStructure:
        """
        Analyze CSV file to determine form requirements.

        Args:
            csv_path: Path to CSV file

        Returns:
            CSVStructure with analysis results
        """
        # Read CSV to get column structure
        records = self.csv_processor.read_file(csv_path)

        if not records:
            raise ValueError(f"CSV file is empty: {csv_path}")

        # Get columns (excluding 'id' if present)
        all_columns = list(records[0].keys())
        columns = [col for col in all_columns if col.lower() != 'id']

        # Detect parent reference column
        parent_ref_column = None
        has_parent_ref = False

        for col in columns:
            if self._is_parent_reference(col):
                parent_ref_column = col
                has_parent_ref = True
                break

        # Infer field types (basic type inference)
        field_types = {}
        for col in columns:
            if col == 'code' or col == parent_ref_column:
                field_types[col] = 'code'
            elif col == 'name':
                field_types[col] = 'name'
            else:
                field_types[col] = 'text'

        # Check for Pattern 2 (subcategory source) relationship
        pattern2_info = self._detect_pattern2_relationship(csv_path.stem)

        # Determine form type
        if pattern2_info:
            form_type = 'nested_lov_pattern2'
            is_pattern2_child = True
            pattern2_parent_form = pattern2_info['parent_form']
            pattern2_fk_field = pattern2_info['fk_field']
            pattern2_category_value = pattern2_info['category_value']
        elif len(columns) == 2 and 'code' in columns and 'name' in columns:
            form_type = 'simple'
            is_pattern2_child = False
            pattern2_parent_form = None
            pattern2_fk_field = None
            pattern2_category_value = None
        elif has_parent_ref:
            form_type = 'nested_lov'
            is_pattern2_child = False
            pattern2_parent_form = None
            pattern2_fk_field = None
            pattern2_category_value = None
        else:
            form_type = 'multi_field'
            is_pattern2_child = False
            pattern2_parent_form = None
            pattern2_fk_field = None
            pattern2_category_value = None

        return CSVStructure(
            columns=columns,
            column_count=len(columns),
            has_parent_ref=has_parent_ref or is_pattern2_child,
            parent_ref_column=parent_ref_column or pattern2_fk_field,
            field_types=field_types,
            form_type=form_type,
            is_pattern2_child=is_pattern2_child,
            pattern2_parent_form=pattern2_parent_form,
            pattern2_fk_field=pattern2_fk_field,
            pattern2_category_value=pattern2_category_value
        )

    def generate_simple_form(self, form_id: str, form_name: str, table_name: str,
                            structure: CSVStructure) -> Dict[str, Any]:
        """
        Generate simple metadata form (code + name).

        Based on md01maritalStatus.json structure.

        Args:
            form_id: Form identifier
            form_name: Form display name
            table_name: Database table name
            structure: CSV structure analysis

        Returns:
            Joget form JSON definition
        """
        # Create TextField for code
        code_field = {
            "className": "org.joget.apps.form.lib.TextField",
            "properties": {
                "requiredSanitize": "",
                "maxlength": "",
                "validator": {
                    "className": "",
                    "properties": {}
                },
                "label": "Code",
                "encryption": "",
                "readonly": "",
                "size": "",
                "workflowVariable": "",
                "style": "",
                "id": "code",
                "placeholder": "",
                "value": "",
                "readonlyLabel": "",
                "storeNumeric": ""
            }
        }

        # Create TextField for name
        name_field = {
            "className": "org.joget.apps.form.lib.TextField",
            "properties": {
                "requiredSanitize": "",
                "maxlength": "",
                "validator": {
                    "className": "",
                    "properties": {}
                },
                "label": "Name",
                "encryption": "",
                "readonly": "",
                "size": "",
                "workflowVariable": "",
                "style": "",
                "id": "name",
                "placeholder": "",
                "value": "",
                "readonlyLabel": "",
                "storeNumeric": ""
            }
        }

        # Build form structure
        form_json = {
            "elements": [{
                "elements": [{
                    "elements": [code_field, name_field],
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
                "name": form_name,
                "description": "",
                "postProcessorRunOn": "create",
                "permission": {
                    "className": "",
                    "properties": {}
                },
                "id": form_id,
                "postProcessor": {
                    "className": "",
                    "properties": {}
                },
                "storeBinder": {
                    "className": "org.joget.apps.form.lib.WorkflowFormBinder",
                    "properties": {}
                },
                "tableName": table_name
            }
        }

        return form_json

    def generate_nested_lov_form(self, form_id: str, form_name: str, table_name: str,
                                 structure: CSVStructure) -> Dict[str, Any]:
        """
        Generate nested LOV form with SelectBox for parent reference.

        CRITICAL: SelectBox must use "optionsBinder" property, NOT "options" array.
        Joget DX8 will reject forms with array-wrapped FormOptionsBinder.

        Based on NESTED_LOV_GUIDE.md structure.
        For CSV like: code, name, crop_category
        Generates: TextField(code) + SelectBox(crop_category) + TextField(name)

        Args:
            form_id: Unique form identifier
            form_name: Human-readable form name
            table_name: Database table name (max 20 chars)
            structure: Analyzed CSV structure

        Returns:
            Joget form JSON with SelectBox using correct optionsBinder structure

        Raises:
            ValueError: If parent form cannot be resolved
        """
        parent_col = structure.parent_ref_column

        # Derive parent form ID from column name
        # e.g., crop_category → cropCategory or md26cropCategory
        parent_form_id = self._derive_parent_form_id(parent_col)

        # Create TextField for code
        code_field = {
            "className": "org.joget.apps.form.lib.TextField",
            "properties": {
                "requiredSanitize": "",
                "maxlength": "",
                "validator": {
                    "className": "",
                    "properties": {}
                },
                "label": "Code",
                "id": "code",
                "placeholder": "",
                "value": "",
                "readonlyLabel": ""
            }
        }

        # ============================================================
        # CRITICAL: SelectBox MUST use "optionsBinder" property
        # NOT "options" array. Joget will reject array structure.
        # See Case Study 3 in CLAUDE.md for details.
        # ============================================================
        # Create SelectBox for parent reference
        # This is CRITICAL for nested LOV - must be SelectBox, not TextField
        parent_field = {
            "className": "org.joget.apps.form.lib.SelectBox",
            "properties": {
                "label": self._format_label(parent_col),
                "id": parent_col,
                "optionsBinder": {
                    "className": "org.joget.apps.form.lib.FormOptionsBinder",
                    "properties": {
                        "formDefId": parent_form_id,
                        "idColumn": "code",
                        "labelColumn": "name",
                        "addEmptyOption": "true",
                        "useAjax": "false"
                    }
                },
                "validator": {
                    "className": "org.joget.apps.form.lib.DefaultValidator",
                    "properties": {
                        "mandatory": "true"
                    }
                }
            }
        }

        # Create TextField for name
        name_field = {
            "className": "org.joget.apps.form.lib.TextField",
            "properties": {
                "label": "Name",
                "id": "name",
                "placeholder": "",
                "value": ""
            }
        }

        # Build form structure with all three fields
        form_json = {
            "elements": [{
                "elements": [{
                    "elements": [code_field, parent_field, name_field],
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
                "name": form_name,
                "description": f"Nested LOV form with parent reference: {parent_col}",
                "postProcessorRunOn": "create",
                "permission": {
                    "className": "",
                    "properties": {}
                },
                "id": form_id,
                "postProcessor": {
                    "className": "",
                    "properties": {}
                },
                "storeBinder": {
                    "className": "org.joget.apps.form.lib.WorkflowFormBinder",
                    "properties": {}
                },
                "tableName": table_name
            }
        }

        return form_json

    def generate_multi_field_form(self, form_id: str, form_name: str, table_name: str,
                                  structure: CSVStructure) -> Dict[str, Any]:
        """
        Generate multi-field form with dynamic fields based on CSV columns.

        Args:
            form_id: Form identifier
            form_name: Form display name
            table_name: Database table name
            structure: CSV structure analysis

        Returns:
            Joget form JSON definition with all CSV columns as fields
        """
        # Generate fields for all columns
        fields = []

        for col in structure.columns:
            field_type = structure.field_types.get(col, 'text')

            field = {
                "className": "org.joget.apps.form.lib.TextField",
                "properties": {
                    "label": self._format_label(col),
                    "id": col,
                    "placeholder": "",
                    "value": ""
                }
            }

            fields.append(field)

        # Build form structure
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
                "name": form_name,
                "description": "",
                "postProcessorRunOn": "create",
                "permission": {
                    "className": "",
                    "properties": {}
                },
                "id": form_id,
                "postProcessor": {
                    "className": "",
                    "properties": {}
                },
                "storeBinder": {
                    "className": "org.joget.apps.form.lib.WorkflowFormBinder",
                    "properties": {}
                },
                "tableName": table_name
            }
        }

        return form_json

    def generate_pattern2_nested_lov_form(self, form_id: str, form_name: str, table_name: str,
                                          structure: CSVStructure) -> Dict[str, Any]:
        """
        Generate Pattern 2 nested LOV form with INJECTED FK SelectBox.

        CRITICAL: Child CSV does NOT contain FK column, but form MUST have it!
        The FK column and value will be injected during data population.

        Example:
            CSV columns: code, name, power_source
            Generated form fields: code, equipment_category_code (injected!), name, power_source

        Args:
            form_id: Form identifier
            form_name: Form display name
            table_name: Database table name
            structure: CSV structure analysis with Pattern 2 info

        Returns:
            Joget form JSON definition with injected FK SelectBox
        """
        if not structure.is_pattern2_child:
            raise ValueError(f"Form {form_id} is not a Pattern 2 child form")

        parent_form_id = structure.pattern2_parent_form
        fk_field = structure.pattern2_fk_field

        self.logger.info(
            f"Generating Pattern 2 form: {form_id} → Parent: {parent_form_id}, "
            f"Injected FK: {fk_field}"
        )

        # Generate fields
        fields = []

        # 1. Code field (primary key) with DuplicateValueValidator
        code_field = {
            "className": "org.joget.apps.form.lib.TextField",
            "properties": {
                "requiredSanitize": "",
                "maxlength": "",
                "validator": {
                    "className": "org.joget.apps.form.lib.DuplicateValueValidator",
                    "properties": {
                        "formDefId": form_id,
                        "fieldId": "code",
                        "mandatory": "true"
                    }
                },
                "label": "Code",
                "id": "code",
                "placeholder": "",
                "value": ""
            }
        }
        fields.append(code_field)

        # 2. INJECTED FK SelectBox field (NOT in CSV!)
        # This is CRITICAL for nested LOV to work
        fk_field_element = {
            "className": "org.joget.apps.form.lib.SelectBox",
            "properties": {
                "label": self._format_label(fk_field),
                "id": fk_field,
                "optionsBinder": {
                    "className": "org.joget.apps.form.lib.FormOptionsBinder",
                    "properties": {
                        "formDefId": parent_form_id,
                        "idColumn": "code",
                        "labelColumn": "name",
                        "groupingColumn": "",
                        "addEmptyOption": "true",
                        "useAjax": ""
                    }
                },
                "validator": {
                    "className": "org.joget.apps.form.lib.DefaultValidator",
                    "properties": {
                        "mandatory": "true"
                    }
                }
            }
        }
        fields.append(fk_field_element)

        # 3. Other fields from CSV
        for col in structure.columns:
            if col == 'code':
                continue  # Already added

            field = {
                "className": "org.joget.apps.form.lib.TextField",
                "properties": {
                    "label": self._format_label(col),
                    "id": col,
                    "placeholder": "",
                    "value": ""
                }
            }
            fields.append(field)

        # Build form structure
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
                "name": form_name,
                "description": f"Pattern 2 nested LOV: {fk_field} → {parent_form_id} (FK injected)",
                "postProcessorRunOn": "create",
                "permission": {
                    "className": "",
                    "properties": {}
                },
                "id": form_id,
                "postProcessor": {
                    "className": "",
                    "properties": {}
                },
                "storeBinder": {
                    "className": "org.joget.apps.form.lib.WorkflowFormBinder",
                    "properties": {}
                },
                "tableName": table_name
            }
        }

        return form_json

    def save_form_json(self, form_json: Dict[str, Any], output_path: Path) -> None:
        """
        Save generated form JSON to file.

        Args:
            form_json: Form JSON definition
            output_path: Output file path
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(form_json, f, indent=4, ensure_ascii=False)

        self.logger.info(f"Saved form JSON to: {output_path}")

    # Helper methods

    def _detect_pattern2_relationship(self, form_id: str) -> Optional[Dict[str, Any]]:
        """
        Detect if this form is a Pattern 2 child (subcategory source).

        Checks subcategory_mappings config to see if this form is referenced
        as a child of any parent form.

        Args:
            form_id: Form identifier (CSV stem)

        Returns:
            Dictionary with pattern2 info if found, None otherwise:
            {
                'parent_form': 'md25equipmentCategory',
                'category_value': 'TILLAGE',
                'fk_field': 'equipment_category_code'
            }
        """
        for parent_form, category_mappings in self.subcategory_mappings.items():
            for category_value, child_form in category_mappings.items():
                if child_form == form_id:
                    # Found! This is a Pattern 2 child
                    fk_field = self._derive_fk_field_name_from_parent(parent_form)

                    self.logger.debug(
                        f"Pattern 2 detected: {form_id} is child of {parent_form} "
                        f"(category: {category_value})"
                    )

                    return {
                        'parent_form': parent_form,
                        'category_value': category_value,
                        'fk_field': fk_field
                    }

        return None

    def _derive_fk_field_name_from_parent(self, parent_form: str) -> str:
        """
        Derive FK field name from parent form name.

        Examples:
        - md25equipmentCategory → equipment_category_code
        - md27inputCategory → input_category_code
        - md03district → district_code

        Args:
            parent_form: Parent form ID

        Returns:
            FK field name (snake_case with _code suffix)
        """
        # Remove md prefix and number
        name = re.sub(r'^md\d+', '', parent_form)

        # Convert camelCase to snake_case
        name = re.sub(r'([A-Z])', r'_\1', name).lower()
        name = name.lstrip('_')

        # Add _code suffix if not present
        if not name.endswith('_code'):
            name = name + '_code'

        return name

    def _is_parent_reference(self, column_name: str) -> bool:
        """Check if column name matches parent reference patterns"""
        for pattern in self.PARENT_REF_PATTERNS:
            if re.match(pattern, column_name, re.IGNORECASE):
                return True
        return False

    def _validate_table_name(self, table_name: str, form_id: str) -> str:
        """
        Validate table name length and detect collisions.
        Joget table names must be <= 20 characters.

        Args:
            table_name: Proposed table name
            form_id: Form identifier (for error messages)

        Returns:
            Validated table name (truncated if necessary)

        Raises:
            ValueError: If truncation causes collision with existing table
        """
        MAX_LENGTH = 20

        if len(table_name) > MAX_LENGTH:
            truncated = table_name[:MAX_LENGTH]

            # Check for collision
            if truncated in self.generated_table_names:
                raise ValueError(
                    f"Table name collision detected!\n"
                    f"  Form ID: {form_id}\n"
                    f"  Original table name: {table_name} ({len(table_name)} chars)\n"
                    f"  Truncated to: {truncated}\n"
                    f"  This conflicts with an existing table name.\n"
                    f"  Please rename the form to avoid collision."
                )

            self.logger.warning(
                f"Table name truncated: {table_name} ({len(table_name)} chars) → {truncated} (20 chars)"
            )
            table_name = truncated

        # Track this table name
        self.generated_table_names.add(table_name)
        return table_name

    def _derive_form_id(self, csv_path: Path) -> str:
        """
        Derive form ID from CSV filename.

        Examples:
            md01maritalStatus.csv → md01maritalStatus
            md19crops.csv → md19crops
        """
        return csv_path.stem

    def _derive_form_name(self, csv_path: Path) -> str:
        """
        Derive human-readable form name from CSV filename.

        Examples:
            md01maritalStatus.csv → MD.01 - Marital Status
            md19crops.csv → MD.19 - Crops
        """
        stem = csv_path.stem

        # Extract number if present (md01 → 01)
        match = re.match(r'md(\d+)(.+)', stem, re.IGNORECASE)
        if match:
            number = match.group(1)
            name_part = match.group(2)

            # Convert camelCase to Title Case
            readable_name = re.sub(r'([A-Z])', r' \1', name_part).strip().title()

            return f"MD.{number} - {readable_name}"
        else:
            # Fallback: just title case
            return stem.replace('_', ' ').title()

    def _derive_parent_form_id(self, parent_column: str) -> str:
        """
        Derive parent form ID from parent reference column name by finding actual form.

        Searches for matching form IDs in the metadata directory.

        Examples:
            target_group → md30targetGroup (if md30targetGroup.csv exists)
            applies_to_type → appliesTo (fallback if no match found)
        """
        # Remove _category, _type, _group, _parent suffixes to get base name
        base_name = re.sub(r'_(category|type|group|parent)$', '', parent_column, flags=re.IGNORECASE)

        # Get metadata CSV directory from config or use default
        metadata_dir = Path(self.config.get('metadata', {}).get('csv_path', './data/metadata'))

        if not metadata_dir.exists():
            # Fallback to old behavior if directory not found
            self.logger.warning(f"Metadata directory not found: {metadata_dir}, using derived name")
            return self._derive_camel_case(base_name)

        # Build list of available forms by scanning CSV files
        available_forms = []
        for csv_file in metadata_dir.glob('md*.csv'):
            form_id = csv_file.stem
            available_forms.append(form_id)

        # Try to find a matching form ID
        # 1. Exact match (case-insensitive)
        for form_id in available_forms:
            if form_id.lower() == base_name.lower():
                return form_id

        # 2. Match by removing md prefix and comparing
        base_lower = base_name.lower()
        for form_id in available_forms:
            # Remove mdNN prefix (e.g., md30targetGroup → targetGroup)
            form_name_part = re.sub(r'^md\d+', '', form_id, flags=re.IGNORECASE).lower()
            if form_name_part == base_lower:
                self.logger.info(f"Matched parent column '{parent_column}' → form '{form_id}'")
                return form_id

        # 3. Fuzzy match: check if base_name is contained in form_id
        for form_id in available_forms:
            if base_lower in form_id.lower():
                self.logger.warning(
                    f"Fuzzy matched parent column '{parent_column}' → form '{form_id}' "
                    f"(verify this is correct!)"
                )
                return form_id

        # No match found - return camelCase version as fallback
        fallback = self._derive_camel_case(base_name)
        self.logger.warning(
            f"No matching form found for column '{parent_column}', "
            f"using fallback: '{fallback}'"
        )
        return fallback

    def _derive_camel_case(self, snake_case_name: str) -> str:
        """Convert snake_case to camelCase"""
        parts = snake_case_name.split('_')
        if len(parts) > 1:
            return parts[0] + ''.join(p.capitalize() for p in parts[1:])
        else:
            return snake_case_name

    def _format_label(self, column_name: str) -> str:
        """
        Format column name as human-readable label.

        Examples:
            crop_category → Crop Category
            livestock_type → Livestock Type
        """
        # Replace underscores with spaces and title case
        return column_name.replace('_', ' ').title()


# Standalone execution
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python form_generator.py <csv_file> [output_json]")
        sys.exit(1)

    csv_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else csv_file.with_suffix('.json')

    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # Generate form
    generator = MetadataFormGenerator()
    form_json = generator.generate_from_csv(csv_file)
    generator.save_form_json(form_json, output_file)

    print(f"\n✓ Generated form JSON: {output_file}")
