#!/usr/bin/env python3
"""
Joget Form Parser - Enhanced Version
====================================
Extracts complete structure from Joget JSON form definitions.
Properly handles parent-child relationships and multi-tab forms.

Key improvements:
- Identifies parent vs. child forms
- No duplication of referenced form content
- Proper grid parent container tracking
- Control field relationships
- Accurate primary key naming
"""

import json
import os
import sys
import yaml
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path
import argparse
from collections import defaultdict


@dataclass
class FormField:
    """Represents a single form field."""
    field_id: str
    field_type: str
    label: str
    table_column: str
    required: bool = False
    validator_type: Optional[str] = None
    max_length: Optional[str] = None
    store_numeric: bool = False
    options: List[Dict] = field(default_factory=list)
    options_binder: Optional[Dict] = None
    control_field: Optional[str] = None
    control_value: Optional[str] = None
    transform_hint: Optional[str] = None
    path: str = ""
    depth: int = 0


@dataclass
class GridField:
    """Represents a grid/subform field."""
    grid_id: str
    form_id: str
    label: str
    sub_form_id: str
    foreign_key: str
    parent_form_id: str = ""  # NEW: Which form contains this grid
    parent_field_id: str = ""  # NEW: Field ID that holds the grid
    parent_section_id: str = ""  # NEW: Section containing the grid
    min_rows: Optional[int] = None
    max_rows: Optional[int] = None
    columns: List[Dict] = field(default_factory=list)
    fields: List[FormField] = field(default_factory=list)
    control_field: Optional[str] = None
    control_value: Optional[str] = None
    path: str = ""
    depth: int = 0


@dataclass
class FormSection:
    """Represents a form section."""
    section_id: str
    label: str
    fields: List[FormField] = field(default_factory=list)
    grids: List[GridField] = field(default_factory=list)
    subsections: List['FormSection'] = field(default_factory=list)
    path: str = ""
    depth: int = 0


@dataclass
class FormTab:
    """Represents a tab in multi-tabbed form - REFERENCE ONLY."""
    tab_id: str
    tab_label: str
    form_def_id: str
    parent_field_id: str = ""  # NEW: Field in parent that holds tab data
    subform_parent_id: str = ""  # NEW: Field in tab form that links to parent


@dataclass
class FormDefinition:
    """Complete form definition."""
    form_id: str
    form_name: str
    table_name: str
    primary_key: str
    is_parent_form: bool = False  # NEW: Is this the orchestrating parent?
    is_multi_tab: bool = False
    multi_tab_plugin: str = ""  # NEW: Plugin class name
    tabs: List[FormTab] = field(default_factory=list)
    sections: List[FormSection] = field(default_factory=list)
    all_fields: List[FormField] = field(default_factory=list)
    all_grids: List[GridField] = field(default_factory=list)
    referenced_forms: Set[str] = field(default_factory=set)
    parent_of: Set[str] = field(default_factory=set)  # NEW: Forms this is parent of
    child_of: Optional[str] = None  # NEW: Parent form if this is a child
    metadata: Dict = field(default_factory=dict)
    max_depth: int = 0


class JogetFormParser:
    """Parses Joget JSON form definitions."""

    def __init__(self, forms_directory: str):
        self.forms_dir = Path(forms_directory)
        self.forms: Dict[str, FormDefinition] = {}
        self.form_files: Dict[str, Path] = {}
        self.field_types_map = self._build_field_type_map()
        self.parsing_stack: List[str] = []
        self.form_hierarchy: Dict[str, Set[str]] = defaultdict(set)  # NEW: Track hierarchy
        self.current_parent_form: Optional[str] = None  # NEW: Track current parent context

        self._scan_forms_directory()

    def _scan_forms_directory(self):
        """Scan directory and catalog all form files."""
        if not self.forms_dir.exists():
            print(f"✗ Forms directory not found: {self.forms_dir}")
            sys.exit(1)

        json_files = list(self.forms_dir.glob("**/*.json"))

        print(f"Scanning forms directory: {self.forms_dir}")
        print(f"Found {len(json_files)} JSON files")
        print("-" * 80)

        for file_path in json_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    form_id = data.get('properties', {}).get('id')
                    if form_id:
                        self.form_files[form_id] = file_path
                        print(f"  • {form_id:<40} {file_path.name}")
            except Exception as e:
                print(f"  ⚠ Error reading {file_path.name}: {e}")

        print(f"\nCataloged {len(self.form_files)} forms")
        print("=" * 80 + "\n")

    def _build_field_type_map(self) -> Dict[str, str]:
        """Map Joget class names to readable field types."""
        return {
            'org.joget.apps.form.lib.TextField': 'text',
            'org.joget.apps.form.lib.TextArea': 'textarea',
            'org.joget.apps.form.lib.SelectBox': 'select',
            'org.joget.apps.form.lib.Radio': 'radio',
            'org.joget.apps.form.lib.CheckBox': 'checkbox',
            'org.joget.apps.form.lib.DatePicker': 'date',
            'org.joget.apps.form.lib.HiddenField': 'hidden',
            'org.joget.apps.form.lib.IdGeneratorField': 'id_generator',
            'org.joget.plugin.enterprise.FormGrid': 'grid',
            'org.joget.plugin.enterprise.Signature': 'signature',
            'org.joget.plugin.enterprise.MultiPagedForm': 'multi_page',
            'org.joget.apps.form.lib.CustomHTML': 'html',
        }

    def derive_column_name(self, field_id: str) -> str:
        """Derive database column name from field ID."""
        if field_id.startswith('c_'):
            return field_id
        return f"c_{field_id}"

    def derive_primary_key(self, table_name: str, form_id: str) -> str:
        """
        Derive proper primary key based on Joget conventions.
        Joget typically uses c_id for all tables unless specifically overridden.
        """
        if not table_name:
            return "c_id"

        # Standard Joget convention: all tables use c_id
        return "c_id"

    def suggest_transform(self, field_type: str, properties: Dict) -> Optional[str]:
        """Suggest data transformation based on field type."""
        if field_type == 'date':
            return 'date_ISO8601'
        if properties.get('storeNumeric') == 'true':
            return 'numeric'
        if field_type == 'checkbox':
            return 'multiCheckbox'
        if field_type == 'signature':
            return 'base64'
        return None

    def find_multi_paged_form(self, elements: List[Dict]) -> Optional[Dict]:
        """Recursively find MultiPagedForm element anywhere in the structure."""
        for element in elements:
            class_name = element.get('className', '')

            if 'MultiPagedForm' in class_name:
                return element

            child_elements = element.get('elements', [])
            if child_elements:
                found = self.find_multi_paged_form(child_elements)
                if found:
                    return found

        return None

    def parse_field(self, element: Dict, path: str = "", depth: int = 0) -> Optional[FormField]:
        """Parse a single field element."""
        class_name = element.get('className', '')
        properties = element.get('properties', {})

        if class_name not in self.field_types_map:
            return None

        field_id = properties.get('id')
        if not field_id:
            return None

        field_type = self.field_types_map[class_name]

        validator = properties.get('validator', {})
        validator_props = validator.get('properties', {}) if isinstance(validator, dict) else {}

        options = []
        raw_options = properties.get('options', [])
        if isinstance(raw_options, list):
            for opt in raw_options:
                if isinstance(opt, dict):
                    options.append({
                        'value': opt.get('value'),
                        'label': opt.get('label')
                    })

        options_binder = properties.get('optionsBinder')
        if options_binder and isinstance(options_binder, dict):
            binder_props = options_binder.get('properties', {})
            options_binder = {
                'form_def_id': binder_props.get('formDefId'),
                'id_column': binder_props.get('idColumn'),
                'label_column': binder_props.get('labelColumn')
            }

        return FormField(
            field_id=field_id,
            field_type=field_type,
            label=properties.get('label', ''),
            table_column=self.derive_column_name(field_id),
            required=validator_props.get('mandatory') == 'true',
            validator_type=validator_props.get('type'),
            max_length=properties.get('maxlength'),
            store_numeric=properties.get('storeNumeric') == 'true',
            options=options,
            options_binder=options_binder,
            control_field=properties.get('controlField'),
            control_value=properties.get('controlValue'),
            transform_hint=self.suggest_transform(field_type, properties),
            path=path,
            depth=depth
        )

    def parse_grid(self, element: Dict, parent_form_id: str, parent_section_id: str,
                   path: str = "", depth: int = 0) -> Optional[GridField]:
        """Parse a grid/subform element with parent context."""
        properties = element.get('properties', {})

        grid_id = properties.get('id')
        if not grid_id:
            return None

        load_binder = properties.get('loadBinder', {})
        binder_props = load_binder.get('properties', {}) if isinstance(load_binder, dict) else {}

        sub_form_id = binder_props.get('formDefId', '')
        foreign_key = binder_props.get('foreignKey', '')

        columns = []
        raw_columns = properties.get('options', [])
        if isinstance(raw_columns, list):
            for col in raw_columns:
                if isinstance(col, dict):
                    columns.append({
                        'value': col.get('value'),
                        'label': col.get('label'),
                        'format_type': col.get('formatType'),
                        'width': col.get('width')
                    })

        grid = GridField(
            grid_id=grid_id,
            form_id=properties.get('formDefId', ''),
            label=properties.get('label', ''),
            sub_form_id=sub_form_id,
            foreign_key=foreign_key,
            parent_form_id=parent_form_id,  # NEW
            parent_field_id=grid_id,  # NEW: Grid field ID
            parent_section_id=parent_section_id,  # NEW
            min_rows=self._parse_int(properties.get('validateMinRow')),
            max_rows=self._parse_int(properties.get('validateMaxRow')),
            columns=columns,
            control_field=properties.get('controlField'),
            control_value=properties.get('controlValue'),
            path=path,
            depth=depth
        )

        # Parse sub-form fields
        if sub_form_id and sub_form_id in self.form_files:
            sub_form_fields = self._parse_referenced_form(sub_form_id, depth + 1)
            grid.fields = sub_form_fields

            # Track hierarchy
            if parent_form_id:
                self.form_hierarchy[parent_form_id].add(sub_form_id)

        return grid

    def _parse_referenced_form(self, form_id: str, depth: int) -> List[FormField]:
        """Parse a referenced sub-form and extract its fields."""
        if form_id in self.parsing_stack:
            print(f"  ⚠ Circular reference detected: {form_id}")
            return []

        if form_id not in self.form_files:
            print(f"  ⚠ Referenced form not found: {form_id}")
            return []

        self.parsing_stack.append(form_id)

        try:
            with open(self.form_files[form_id], 'r') as f:
                form_data = json.load(f)

            elements = form_data.get('elements', [])
            fields, _, _ = self.parse_elements(elements, form_id, "", f"/{form_id}", depth)

            return fields

        except Exception as e:
            print(f"  ✗ Error parsing referenced form {form_id}: {e}")
            return []

        finally:
            self.parsing_stack.pop()

    def parse_multi_paged_form(self, element: Dict, parent_form_id: str, path: str = "", depth: int = 0) -> List[
        FormTab]:
        """Parse multi-tabbed form - REFERENCE ONLY, no content duplication."""
        properties = element.get('properties', {})
        tabs = []

        print(f"\n  [DEBUG] MultiPagedForm found at depth {depth}")

        number_of_page = properties.get('numberOfPage', {})

        if not isinstance(number_of_page, dict):
            print(f"  ⚠ numberOfPage is not a dict: {type(number_of_page)}")
            return tabs

        num_pages_str = number_of_page.get('className', '0')
        try:
            num_pages = int(num_pages_str)
            print(f"  [DEBUG] Number of tabs: {num_pages}")
        except (ValueError, TypeError):
            print(f"  ⚠ Invalid numberOfPage.className: {num_pages_str}")
            return tabs

        page_props = number_of_page.get('properties', {})

        if not isinstance(page_props, dict):
            print(f"  ⚠ numberOfPage.properties is not a dict: {type(page_props)}")
            return tabs

        for page_num in range(1, num_pages + 1):
            page_label_key = f'page{page_num}_label'
            page_form_id_key = f'page{page_num}_formDefId'
            page_parent_field_key = f'page{page_num}_parentSubFormId'
            page_subform_parent_key = f'page{page_num}_subFormParentId'

            page_label = page_props.get(page_label_key)
            page_form_id = page_props.get(page_form_id_key)
            parent_field_id = page_props.get(page_parent_field_key, '')
            subform_parent_id = page_props.get(page_subform_parent_key, '')

            if not page_label or not page_form_id:
                print(f"  ⚠ Tab {page_num}: Missing configuration")
                continue

            print(f"  → Tab {page_num}: {page_label} ({page_form_id})")

            tab = FormTab(
                tab_id=f"tab_{page_num}",
                tab_label=page_label,
                form_def_id=page_form_id,
                parent_field_id=parent_field_id,
                subform_parent_id=subform_parent_id
            )

            tabs.append(tab)

            # Track hierarchy
            self.form_hierarchy[parent_form_id].add(page_form_id)

        print(f"  [DEBUG] Total tabs parsed: {len(tabs)}\n")
        return tabs

    def _parse_int(self, value: Any) -> Optional[int]:
        """Safely parse integer value."""
        if value is None or value == '':
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def parse_elements(self, elements: List[Dict], current_form_id: str, current_section_id: str,
                       path: str = "", depth: int = 0) -> tuple:
        """Parse a list of form elements recursively with context."""
        fields = []
        grids = []
        sections = []

        for i, element in enumerate(elements):
            class_name = element.get('className', '')
            current_path = f"{path}/element[{i}]"

            # Skip MultiPagedForm - it's handled at form level
            if 'MultiPagedForm' in class_name:
                continue

            # Handle sections
            if 'Section' in class_name:
                section_props = element.get('properties', {})
                section_id = section_props.get('id', f'section_{i}')
                section_label = section_props.get('label', '')

                section_elements = element.get('elements', [])
                sec_fields, sec_grids, sec_subsections = self.parse_elements(
                    section_elements,
                    current_form_id,
                    section_id,  # Pass section context
                    f"{current_path}/{section_id}",
                    depth + 1
                )

                section = FormSection(
                    section_id=section_id,
                    label=section_label,
                    fields=sec_fields,
                    grids=sec_grids,
                    subsections=sec_subsections,
                    path=current_path,
                    depth=depth
                )
                sections.append(section)
                fields.extend(sec_fields)
                grids.extend(sec_grids)

            # Handle columns
            elif 'Column' in class_name:
                col_elements = element.get('elements', [])
                col_fields, col_grids, col_sections = self.parse_elements(
                    col_elements,
                    current_form_id,
                    current_section_id,
                    f"{current_path}/column",
                    depth
                )
                fields.extend(col_fields)
                grids.extend(col_grids)
                sections.extend(col_sections)

            # Handle grids - WITH PARENT CONTEXT
            elif 'FormGrid' in class_name:
                grid = self.parse_grid(
                    element,
                    current_form_id,
                    current_section_id,
                    current_path,
                    depth
                )
                if grid:
                    grids.append(grid)

            # Handle regular fields
            else:
                field = self.parse_field(element, current_path, depth)
                if field:
                    fields.append(field)

        return fields, grids, sections

    def parse_form(self, form_data: Dict, depth: int = 0, is_entry_point: bool = False) -> FormDefinition:
        """Parse a complete form definition."""
        properties = form_data.get('properties', {})
        elements = form_data.get('elements', [])

        form_id = properties.get('id', 'unknown')
        form_name = properties.get('name', '')
        table_name = properties.get('tableName', '')

        print(f"{'  ' * depth}Parsing: {form_name} ({form_id})")

        # Derive proper primary key
        primary_key = self.derive_primary_key(table_name, form_id)

        # CRITICAL: Search for MultiPagedForm anywhere in the element tree
        multi_paged_element = self.find_multi_paged_form(elements)

        is_multi_tab = multi_paged_element is not None
        is_parent_form = is_entry_point and is_multi_tab  # NEW
        multi_tab_plugin = ""

        if multi_paged_element:
            multi_tab_plugin = multi_paged_element.get('className', '')

        tabs = []
        all_fields = []
        all_grids = []
        sections = []
        referenced_forms = set()
        max_depth = depth

        if is_multi_tab:
            print(f"{'  ' * depth}  → Multi-tab form detected")
            print(f"{'  ' * depth}  → Is parent form: {is_parent_form}")

            tabs = self.parse_multi_paged_form(multi_paged_element, form_id, f"/{form_id}", depth)

            # IMPORTANT: Don't parse tab content here - just record references
            for tab in tabs:
                referenced_forms.add(tab.form_def_id)

            max_depth = depth + 1
        else:
            # Non-multi-tab form: parse normally
            all_fields, all_grids, sections = self.parse_elements(
                elements,
                form_id,
                "",  # No section initially
                f"/{form_id}",
                depth
            )

        # Track grid references
        for grid in all_grids:
            if grid.sub_form_id:
                referenced_forms.add(grid.sub_form_id)

        if all_fields:
            max_depth = max(max_depth, max((f.depth for f in all_fields), default=depth))

        metadata = {
            'description': properties.get('description', ''),
            'load_binder': properties.get('loadBinder', {}).get('className', ''),
            'store_binder': properties.get('storeBinder', {}).get('className', ''),
        }

        form_def = FormDefinition(
            form_id=form_id,
            form_name=form_name,
            table_name=table_name,
            primary_key=primary_key,
            is_parent_form=is_parent_form,  # NEW
            is_multi_tab=is_multi_tab,
            multi_tab_plugin=multi_tab_plugin,  # NEW
            tabs=tabs,
            sections=sections,
            all_fields=all_fields,
            all_grids=all_grids,
            referenced_forms=referenced_forms,
            metadata=metadata,
            max_depth=max_depth
        )

        print(
            f"{'  ' * depth}  ✓ Fields: {len(all_fields)}, Grids: {len(all_grids)}, Tabs: {len(tabs)}, Sections: {len(sections)}")

        return form_def

    def parse_form_file(self, file_path: Path, entry_point: bool = False) -> Optional[FormDefinition]:
        """Parse a form from JSON file."""
        try:
            with open(file_path, 'r') as f:
                form_data = json.load(f)

            depth = 0 if entry_point else 1
            form_def = self.parse_form(form_data, depth, is_entry_point=entry_point)
            self.forms[form_def.form_id] = form_def

            return form_def

        except Exception as e:
            print(f"✗ Error parsing {file_path}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def finalize_hierarchy(self):
        """Finalize parent-child relationships after all forms parsed."""
        for parent_id, children in self.form_hierarchy.items():
            if parent_id in self.forms:
                self.forms[parent_id].parent_of = children

            for child_id in children:
                if child_id in self.forms:
                    self.forms[child_id].child_of = parent_id

    def generate_yaml_report(self, output_file: str = "form_structure.yaml"):
        """Generate YAML report with proper hierarchy."""
        # Identify entry points (forms with no parent)
        entry_points = [
            form_id for form_id, form_def in self.forms.items()
            if form_def.child_of is None
        ]

        # Identify grid forms (forms used as subforms in grids)
        grid_form_ids = set()
        for form_def in self.forms.values():
            for grid in form_def.all_grids:
                if grid.sub_form_id:
                    grid_form_ids.add(grid.sub_form_id)

        report = {
            'metadata': {
                'total_forms': len(self.forms),
                'forms_directory': str(self.forms_dir),
                'entry_points': entry_points,
                'parent_forms': [
                    form_id for form_id, form_def in self.forms.items()
                    if form_def.is_parent_form
                ],
                'grid_forms': sorted(list(grid_form_ids))
            },
            'form_hierarchy': {},
            'forms': {}
        }

        # Build hierarchy tree
        for form_id, form_def in self.forms.items():
            if form_def.parent_of:
                report['form_hierarchy'][form_id] = sorted(list(form_def.parent_of))

        # Generate form definitions
        for form_id, form_def in sorted(self.forms.items()):
            form_dict = {
                'form_name': form_def.form_name,
                'table_name': form_def.table_name,
                'primary_key': form_def.primary_key,
                'is_parent_form': form_def.is_parent_form,
                'is_multi_tab': form_def.is_multi_tab,
            }

            if form_def.multi_tab_plugin:
                form_dict['multi_tab_plugin'] = form_def.multi_tab_plugin

            if form_def.child_of:
                form_dict['child_of'] = form_def.child_of

            if form_def.parent_of:
                form_dict['parent_of'] = sorted(list(form_def.parent_of))

            form_dict['max_nesting_depth'] = form_def.max_depth
            form_dict['referenced_forms'] = sorted(list(form_def.referenced_forms))

            form_dict['statistics'] = {
                'total_fields': len(form_def.all_fields),
                'total_grids': len(form_def.all_grids),
                'total_sections': len(form_def.sections),
                'total_tabs': len(form_def.tabs)
            }

            # For parent multi-tab forms: only show tab references
            if form_def.is_parent_form and form_def.is_multi_tab:
                form_dict['tabs'] = []
                for tab in form_def.tabs:
                    tab_dict = {
                        'tab_label': tab.tab_label,
                        'form_def_id': tab.form_def_id,
                    }
                    if tab.parent_field_id:
                        tab_dict['parent_field_id'] = tab.parent_field_id
                    if tab.subform_parent_id:
                        tab_dict['subform_parent_id'] = tab.subform_parent_id

                    form_dict['tabs'].append(tab_dict)

            # For non-parent forms: show full content
            elif not form_def.is_parent_form:
                if form_def.sections:
                    form_dict['sections'] = []
                    for section in form_def.sections:
                        section_dict = self._section_to_dict(section)
                        form_dict['sections'].append(section_dict)

                form_dict['all_fields'] = self._fields_to_list(form_def.all_fields)

                if form_def.all_grids:
                    form_dict['grids'] = self._grids_to_list(form_def.all_grids)

            report['forms'][form_id] = form_dict

        with open(output_file, 'w') as f:
            yaml.safe_dump(
                report,
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
                indent=2,
                width=120
            )

        print(f"✓ Generated YAML report: {output_file}")

    def _section_to_dict(self, section: FormSection) -> Dict:
        """Convert section to dictionary for YAML output."""
        section_dict = {
            'section_id': section.section_id,
            'label': section.label,
            'depth': section.depth,
            'fields': []
        }

        for field in section.fields:
            field_dict = {
                'field_id': field.field_id,
                'label': field.label,
                'type': field.field_type,
                'column': field.table_column,
                'required': field.required
            }

            if field.options:
                field_dict['options_count'] = len(field.options)

            if field.options_binder:
                field_dict['lookup_form'] = field.options_binder['form_def_id']

            if field.transform_hint:
                field_dict['transform_hint'] = field.transform_hint

            section_dict['fields'].append(field_dict)

        if section.grids:
            section_dict['grids'] = []
            for grid in section.grids:
                grid_dict = {
                    'grid_id': grid.grid_id,
                    'label': grid.label,
                    'sub_form_id': grid.sub_form_id,
                    'foreign_key': grid.foreign_key,
                    'parent_form_id': grid.parent_form_id,
                    'parent_section_id': grid.parent_section_id
                }

                if grid.control_field:
                    grid_dict['control_field'] = grid.control_field
                    grid_dict['control_value'] = grid.control_value

                section_dict['grids'].append(grid_dict)

        if section.subsections:
            section_dict['subsections'] = []
            for subsection in section.subsections:
                section_dict['subsections'].append(self._section_to_dict(subsection))

        return section_dict

    def _fields_to_list(self, fields: List[FormField]) -> List[Dict]:
        """Convert fields list to dict list."""
        result = []
        for field in fields:
            field_dict = {
                'field_id': field.field_id,
                'label': field.label,
                'type': field.field_type,
                'column': field.table_column,
                'required': field.required,
                'depth': field.depth
            }

            if field.options:
                field_dict['options_count'] = len(field.options)

            if field.options_binder:
                field_dict['lookup_form'] = field.options_binder['form_def_id']

            if field.transform_hint:
                field_dict['transform_hint'] = field.transform_hint

            if field.control_field:
                field_dict['conditional'] = {
                    'field': field.control_field,
                    'value': field.control_value
                }

            result.append(field_dict)
        return result

    def _grids_to_list(self, grids: List[GridField]) -> List[Dict]:
        """Convert grids list to dict list with enhanced metadata."""
        result = []
        for grid in grids:
            grid_dict = {
                'grid_id': grid.grid_id,
                'label': grid.label,
                'sub_form_id': grid.sub_form_id,
                'foreign_key': grid.foreign_key,
                'parent_form_id': grid.parent_form_id,
                'parent_field_id': grid.parent_field_id,
                'parent_section_id': grid.parent_section_id,
                'min_rows': grid.min_rows,
                'max_rows': grid.max_rows,
                'depth': grid.depth
            }

            if grid.control_field:
                grid_dict['conditional_display'] = {
                    'control_field': grid.control_field,
                    'required_value': grid.control_value
                }

            if grid.columns:
                grid_dict['columns'] = [
                    {'label': col['label'], 'value': col['value']}
                    for col in grid.columns
                ]

            if grid.fields:
                grid_dict['sub_form_fields'] = [
                    {
                        'field_id': f.field_id,
                        'label': f.label,
                        'type': f.field_type,
                        'column': f.table_column,
                        'required': f.required
                    }
                    for f in grid.fields
                ]

            result.append(grid_dict)
        return result

    def generate_json_report(self, output_file: str = "form_structure.json"):
        """Generate JSON report."""
        report = {
            'metadata': {
                'total_forms': len(self.forms),
                'forms_directory': str(self.forms_dir),
                'forms_parsed': list(self.forms.keys())
            },
            'forms': {}
        }

        for form_id, form_def in self.forms.items():
            form_dict = self._form_to_dict(form_def)
            report['forms'][form_id] = form_dict

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"✓ Generated JSON report: {output_file}")

    def _form_to_dict(self, form_def: FormDefinition) -> Dict:
        """Convert form definition to dictionary."""
        result = {
            'form_id': form_def.form_id,
            'form_name': form_def.form_name,
            'table_name': form_def.table_name,
            'primary_key': form_def.primary_key,
            'is_parent_form': form_def.is_parent_form,
            'is_multi_tab': form_def.is_multi_tab,
            'max_depth': form_def.max_depth,
            'referenced_forms': sorted(list(form_def.referenced_forms)),
        }

        if form_def.child_of:
            result['child_of'] = form_def.child_of

        if form_def.parent_of:
            result['parent_of'] = sorted(list(form_def.parent_of))

        if form_def.multi_tab_plugin:
            result['multi_tab_plugin'] = form_def.multi_tab_plugin

        # Include tabs for parent forms
        if form_def.is_parent_form:
            result['tabs'] = [asdict(tab) for tab in form_def.tabs]
        else:
            result['sections'] = [asdict(section) for section in form_def.sections]
            result['all_fields'] = [asdict(field) for field in form_def.all_fields]
            result['all_grids'] = [asdict(grid) for grid in form_def.all_grids]

        result['metadata'] = form_def.metadata

        return result


def main():
    parser = argparse.ArgumentParser(
        description='Parse Joget form definitions with proper hierarchy tracking',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python form_parser.py --forms-dir forms/ --entry-point farmers-01.json
  python form_parser.py --forms-dir forms/ --entry-point farmers-01.json --format yaml
  python form_parser.py --forms-dir forms/ --entry-point farmers-01.json --output reports/
        """
    )

    parser.add_argument(
        '--forms-dir',
        required=True,
        help='Directory containing all Joget form JSON files'
    )

    parser.add_argument(
        '--entry-point',
        required=True,
        help='Entry point form file (e.g., farmers-01.json for multi-tab forms)'
    )

    parser.add_argument(
        '--format',
        choices=['yaml', 'json', 'both'],
        default='yaml',
        help='Output format (default: yaml)'
    )

    parser.add_argument(
        '--output',
        default='.',
        help='Output directory for reports (default: current directory)'
    )

    args = parser.parse_args()

    forms_path = Path(args.forms_dir)
    if not forms_path.exists():
        print(f"✗ Forms directory not found: {args.forms_dir}")
        sys.exit(1)

    entry_point_path = forms_path / args.entry_point
    if not entry_point_path.exists():
        print(f"✗ Entry point file not found: {entry_point_path}")
        sys.exit(1)

    print("=" * 80)
    print("JOGET FORM PARSER - ENHANCED")
    print("=" * 80)
    print(f"Forms Directory: {args.forms_dir}")
    print(f"Entry Point:     {args.entry_point}")
    print(f"Output Format:   {args.format}")
    print("=" * 80 + "\n")

    form_parser = JogetFormParser(args.forms_dir)

    print("Parsing forms...")
    print("-" * 80)

    # Parse entry point
    form_def = form_parser.parse_form_file(entry_point_path, entry_point=True)

    if not form_def:
        print("\n✗ Failed to parse entry point form")
        sys.exit(1)

    # Parse referenced forms
    to_parse = list(form_def.referenced_forms)
    while to_parse:
        ref_form_id = to_parse.pop(0)
        if ref_form_id not in form_parser.forms and ref_form_id in form_parser.form_files:
            print(f"\nParsing referenced form: {ref_form_id}")
            ref_form = form_parser.parse_form_file(form_parser.form_files[ref_form_id])
            if ref_form:
                to_parse.extend(ref_form.referenced_forms)

    # Finalize hierarchy
    form_parser.finalize_hierarchy()

    print("\n" + "=" * 80)
    print("PARSING COMPLETE")
    print("=" * 80)
    print(f"Total forms parsed: {len(form_parser.forms)}")

    print("\nForm Hierarchy:")
    for form_id, form_def in form_parser.forms.items():
        if form_def.child_of is None:  # Root forms only
            print(f"→ {form_def.form_name} ({form_id})")
            if form_def.is_parent_form:
                print(f"  [PARENT FORM]")
            if form_def.is_multi_tab:
                for tab in form_def.tabs:
                    print(f"  ├─ Tab: {tab.tab_label} → {tab.form_def_id}")
            if form_def.parent_of:
                for child_id in sorted(form_def.parent_of):
                    if child_id in form_parser.forms:
                        child_form = form_parser.forms[child_id]
                        print(f"  └─ Child: {child_form.form_name} ({child_id})")

    print("\n" + "=" * 80)
    print("GENERATING REPORTS")
    print("=" * 80 + "\n")

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.format in ['yaml', 'both']:
        form_parser.generate_yaml_report(str(output_dir / "form_structure.yaml"))

    if args.format in ['json', 'both']:
        form_parser.generate_json_report(str(output_dir / "form_structure.json"))

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print("\nGenerated files:")
    print("  • form_structure.yaml - Complete form breakdown with proper hierarchy")
    print(f"  • Entry point: {form_def.form_name}")
    print(f"  • Parent forms: {len([f for f in form_parser.forms.values() if f.is_parent_form])}")
    print(f"  • Child forms: {len([f for f in form_parser.forms.values() if f.child_of])}")
    print(f"  • Grid forms: {len([f for f in form_parser.forms.values() if not f.table_name or 'Form' in f.form_id])}")


if __name__ == '__main__':
    main()