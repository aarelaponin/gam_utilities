"""
Markdown parser for form specifications.

Parses markdown documents with form specifications in a specific format
and converts them to canonical YAML format.

Expected markdown structure:
- Level 1 heading: Application overview
- Level 2 headings: Form sections (## Form 1: Name)
- Level 3 headings: Subsections (### Fields, ### Select Box Options, etc.)
- Tables: Field specifications
- Bullet lists: Form details, select options, indexes
"""

import re
from pathlib import Path
from typing import Union, List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from joget_toolkit.parsers.base import BaseParser
from joget_toolkit.specs.schema import (
    AppSpec,
    AppMetadata,
    FormSpec,
    FieldSpec,
    FieldType,
    SelectOption,
    ForeignKeyRef,
    IndexSpec,
)


@dataclass
class FormSection:
    """Parsed form section from markdown"""
    title: str
    form_number: int
    form_name: str
    details: Dict[str, str]
    fields_table: List[List[str]]
    select_options: Dict[str, List[str]]
    indexes: List[Dict[str, Any]]
    content: str


class MarkdownParser(BaseParser):
    """Parser for markdown form specifications"""

    # Field type mapping from markdown descriptions to FieldType
    TYPE_MAPPING = {
        'text field': FieldType.TEXT,
        'text': FieldType.TEXT,
        'select box': FieldType.SELECT,
        'select': FieldType.SELECT,
        'text area': FieldType.TEXTAREA,
        'textarea': FieldType.TEXTAREA,
        'number': FieldType.NUMBER,
        'date picker': FieldType.DATE,
        'date': FieldType.DATE,
        'datetime': FieldType.DATETIME,
        'file upload': FieldType.FILE,
        'file': FieldType.FILE,
        'hidden': FieldType.HIDDEN,
    }

    def parse(self, input_path: Union[str, Path], **kwargs) -> AppSpec:
        """
        Parse markdown file and return canonical AppSpec.

        Args:
            input_path: Path to markdown file
            **kwargs: Additional options
                app_id: Override app ID from markdown
                app_name: Override app name from markdown

        Returns:
            AppSpec in canonical format
        """
        content = self._read_file(input_path)

        # Extract application metadata
        metadata = self._parse_metadata(content, **kwargs)

        # Extract form sections
        form_sections = self._extract_form_sections(content)

        # Convert form sections to FormSpec objects
        forms = []
        for section in form_sections:
            try:
                form_spec = self._parse_form_section(section)
                forms.append(form_spec)
            except Exception as e:
                raise ValueError(f"Error parsing form '{section.form_name}': {e}") from e

        # Build and validate AppSpec
        app_spec = AppSpec(
            version="1.0",
            metadata=metadata,
            forms=forms
        )

        return self._validate_result(app_spec)

    def _parse_metadata(self, content: str, **kwargs) -> AppMetadata:
        """Extract application metadata from markdown"""
        # Try to find application ID
        app_id = kwargs.get('app_id')
        if not app_id:
            # Look for **Application ID:** or similar
            match = re.search(r'\*\*Application ID:\*\*\s*`?(\w+)`?', content, re.IGNORECASE)
            if match:
                app_id = match.group(1)
            else:
                # Default: use filename
                app_id = "unknown_app"

        # Try to find application name
        app_name = kwargs.get('app_name')
        if not app_name:
            match = re.search(r'\*\*Application Name:\*\*\s*(.+)', content, re.IGNORECASE)
            if match:
                app_name = match.group(1).strip()
            else:
                # Try first level-1 heading
                match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                if match:
                    app_name = match.group(1).strip().replace(' - Form Specifications', '')
                else:
                    app_name = app_id.title()

        # Try to find description/purpose
        description = None
        match = re.search(r'\*\*Purpose:\*\*\s*(.+)', content, re.IGNORECASE)
        if match:
            description = match.group(1).strip()

        return AppMetadata(
            app_id=app_id,
            app_name=app_name,
            description=description
        )

    def _extract_form_sections(self, content: str) -> List[FormSection]:
        """Extract individual form sections from markdown"""
        # Find all form sections: ## Form N: Name
        form_pattern = r'^##\s+Form\s+(\d+):\s+(.+?)$'
        form_matches = list(re.finditer(form_pattern, content, re.MULTILINE))

        if not form_matches:
            raise ValueError("No form sections found (expected '## Form N: Name' headers)")

        sections = []
        for i, match in enumerate(form_matches):
            form_number = int(match.group(1))
            form_name = match.group(2).strip()

            # Extract content between this form and next form (or end of file)
            start_pos = match.start()
            end_pos = form_matches[i + 1].start() if i + 1 < len(form_matches) else len(content)
            section_content = content[start_pos:end_pos]

            # Parse subsections
            details = self._parse_form_details(section_content)
            fields_table = self._parse_fields_table(section_content)
            select_options = self._parse_select_options(section_content)
            indexes = self._parse_indexes(section_content)

            sections.append(FormSection(
                title=match.group(0),
                form_number=form_number,
                form_name=form_name,
                details=details,
                fields_table=fields_table,
                select_options=select_options,
                indexes=indexes,
                content=section_content
            ))

        return sections

    def _parse_form_details(self, section_content: str) -> Dict[str, str]:
        """Parse form details section (bullet list)"""
        details = {}

        # Look for "### Form Details" section
        match = re.search(r'###\s+Form Details(.+?)(?=###|\Z)', section_content, re.DOTALL)
        if not match:
            return details

        details_content = match.group(1)

        # Parse bullet points: - **Key:** value
        pattern = r'-\s+\*\*([^:]+):\*\*\s+`?([^`\n]+?)`?\s*(?:\n|$)'
        for match in re.finditer(pattern, details_content):
            key = match.group(1).strip()
            value = match.group(2).strip()
            details[key] = value

        return details

    def _parse_fields_table(self, section_content: str) -> List[List[str]]:
        """Parse fields table from markdown"""
        # Look for "### Fields" section
        match = re.search(r'###\s+Fields(.+?)(?=###|\Z)', section_content, re.DOTALL)
        if not match:
            return []

        table_content = match.group(1)

        # Extract table rows
        rows = []
        in_table = False

        for line in table_content.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Table header or separator line
            if '|' in line:
                if line.startswith('|--') or '---' in line:
                    in_table = True
                    continue

                # Parse table row
                cells = [cell.strip() for cell in line.split('|')]
                # Remove empty first/last cells from | ... |
                cells = [c for c in cells if c]

                if cells and in_table:
                    rows.append(cells)
                elif cells and not in_table:
                    # First row is header - skip it for now, we'll handle it
                    continue

        return rows

    def _parse_select_options(self, section_content: str) -> Dict[str, List[str]]:
        """Parse select box options section"""
        options_map = {}

        # Look for "### Select Box Options" section
        match = re.search(r'###\s+Select Box Options(.+?)(?=###|\Z)', section_content, re.DOTALL)
        if not match:
            return options_map

        options_content = match.group(1)

        # Parse structure like:
        # **field_name:**
        # - option1
        # - option2
        # OR
        # **field1 / field2 / field3:**
        # - option1
        current_fields = []
        for line in options_content.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Field name(s): **field_name:** or **field1 / field2:**
            if line.startswith('**') and line.endswith(':**'):
                field_names = line.strip('*:').strip()
                # Handle multiple fields separated by /
                if '/' in field_names:
                    current_fields = [f.strip() for f in field_names.split('/')]
                else:
                    current_fields = [field_names]

                # Initialize options for all fields
                for field in current_fields:
                    options_map[field] = []

            # Option: - value
            elif line.startswith('-') and current_fields:
                option = line.lstrip('- ').strip()
                if option:
                    # Add option to all current fields
                    for field in current_fields:
                        options_map[field].append(option)

        return options_map

    def _parse_indexes(self, section_content: str) -> List[Dict[str, Any]]:
        """Parse indexes section"""
        indexes = []

        # Look for "### Indexes" section
        match = re.search(r'###\s+Indexes(.+?)(?=###|\Z)', section_content, re.DOTALL)
        if not match:
            return indexes

        indexes_content = match.group(1)

        # Parse lines like:
        # - Primary: `field_name`
        # - Foreign Key: `field_name`
        # - Index: `field1`, `field2`, `field3`
        # - Unique Composite: `field1 + field2 + field3`

        for line in indexes_content.split('\n'):
            line = line.strip()
            if not line or not line.startswith('-'):
                continue

            # Extract index type and fields
            match = re.match(r'-\s+([^:]+):\s+(.+)', line)
            if not match:
                continue

            index_type = match.group(1).strip().lower()
            fields_str = match.group(2).strip()

            # Extract field names (remove backticks, split by comma or +)
            fields_str = re.sub(r'`', '', fields_str)
            if '+' in fields_str:
                fields = [f.strip() for f in fields_str.split('+')]
            else:
                fields = [f.strip() for f in fields_str.split(',')]

            # Determine if unique
            unique = 'unique' in index_type or 'primary' in index_type

            # Skip primary key (handled separately)
            if 'primary' in index_type:
                continue

            # Skip foreign key (handled separately)
            if 'foreign' in index_type:
                continue

            indexes.append({
                'fields': fields,
                'unique': unique
            })

        return indexes

    def _parse_form_section(self, section: FormSection) -> FormSpec:
        """Convert FormSection to FormSpec"""
        # Get form ID and table name from details
        form_id = section.details.get('Form ID', self._to_snake_case(section.form_name))
        table_name = section.details.get('Table Name', f"app_fd_{form_id}")

        # Parse fields
        fields = []
        for row in section.fields_table:
            if len(row) < 3:
                continue  # Skip invalid rows

            field_spec = self._parse_field_row(row, section)
            if field_spec:
                fields.append(field_spec)

        # Check if any field is marked as foreign key in details
        if 'Foreign Key' in section.details:
            fk_field_name = section.details['Foreign Key'].split('→')[0].strip()
            fk_target = section.details['Foreign Key'].split('→')[1].strip() if '→' in section.details['Foreign Key'] else None

            # Find and update the foreign key field
            for field in fields:
                if field.id == fk_field_name:
                    if fk_target:
                        # Parse target: formName.fieldName
                        if '.' in fk_target:
                            target_form, target_field = fk_target.split('.', 1)
                        else:
                            target_form = fk_target
                            target_field = 'id'  # Default

                        field.type = FieldType.FOREIGN_KEY
                        field.references = ForeignKeyRef(
                            form=target_form,
                            field=target_field,
                            label_field=target_field  # Could be improved
                        )

        # Parse indexes
        indexes = [IndexSpec(**idx) for idx in section.indexes]

        return FormSpec(
            id=form_id,
            name=section.form_name,
            table=table_name,
            description=section.details.get('Purpose'),
            fields=fields,
            indexes=indexes if indexes else None
        )

    def _parse_field_row(self, row: List[str], section: FormSection) -> Optional[FieldSpec]:
        """Parse a single field row from table"""
        if len(row) < 3:
            return None

        # Expected columns: Field Name | Label | Type | Size | Required | Default | Purpose
        field_name = row[0].strip('`').strip()
        label = row[1].strip() if len(row) > 1 else field_name.replace('_', ' ').title()
        type_str = row[2].lower().strip() if len(row) > 2 else 'text'
        size_str = row[3].strip() if len(row) > 3 else None
        required_str = row[4].lower().strip() if len(row) > 4 else 'no'
        default_str = row[5].strip() if len(row) > 5 else None
        description = row[6].strip() if len(row) > 6 else None

        # Map type
        field_type = self._map_field_type(type_str)

        # Parse size
        size = None
        if size_str and size_str != '-' and size_str.isdigit():
            size = int(size_str)

        # Parse required
        required = required_str in ('yes', 'true', 'required')

        # Parse default
        default = None
        if default_str and default_str != '-':
            # Handle special defaults
            default_lower = default_str.lower().strip('{}')
            if default_lower == 'currentuser':
                default = 'currentUser'
            elif default_lower == 'currentdatetime':
                default = 'currentDateTime'
            elif default_lower == 'uuid':
                default = 'uuid'
            else:
                default = default_str

        # Check if this is primary key
        primary_key = section.details.get('Primary Key', '') == field_name

        # Get select options if this is a select field
        options = None
        references = None
        if field_type in (FieldType.SELECT, FieldType.RADIO, FieldType.CHECKBOX):
            options = section.select_options.get(field_name)

        return FieldSpec(
            id=field_name,
            type=field_type,
            label=label,
            size=size,
            required=required,
            default=default,
            primary_key=primary_key,
            description=description,
            options=options,
            references=references
        )

    def _map_field_type(self, type_str: str) -> FieldType:
        """Map markdown type string to FieldType enum"""
        type_str = type_str.lower().strip()

        for key, field_type in self.TYPE_MAPPING.items():
            if key in type_str:
                return field_type

        # Default to text
        return FieldType.TEXT

    def _to_snake_case(self, text: str) -> str:
        """Convert text to snake_case"""
        # Remove special characters
        text = re.sub(r'[^\w\s]', '', text)
        # Replace spaces with underscores
        text = re.sub(r'\s+', '_', text)
        # Convert to lowercase
        return text.lower()
