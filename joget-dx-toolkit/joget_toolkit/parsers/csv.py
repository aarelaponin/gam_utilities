"""
CSV parser for simple metadata forms.

Parses CSV files and converts them to canonical YAML format.
Primarily for simple metadata (code + name) forms.
"""

import csv
from pathlib import Path
from typing import Union, Optional

from joget_toolkit.parsers.base import BaseParser
from joget_toolkit.specs.schema import (
    AppSpec,
    AppMetadata,
    FormSpec,
    FieldSpec,
    FieldType,
)


class CSVParser(BaseParser):
    """Parser for CSV metadata files"""

    def parse(self, input_path: Union[str, Path], **kwargs) -> AppSpec:
        """
        Parse CSV file and return canonical AppSpec.

        Args:
            input_path: Path to CSV file
            **kwargs: Additional options
                app_id: Application ID (required)
                form_id: Form ID (defaults to filename)
                form_name: Form name (defaults to formatted filename)

        Returns:
            AppSpec with single form

        Raises:
            ValueError: If app_id not provided or CSV is invalid
        """
        path = Path(input_path)
        content = self._read_file(path)

        # Parse CSV
        reader = csv.DictReader(content.splitlines())
        rows = list(reader)

        if not rows:
            raise ValueError(f"CSV file is empty: {path}")

        # Get column names
        columns = list(rows[0].keys())

        # Require app_id
        app_id = kwargs.get('app_id')
        if not app_id:
            raise ValueError("app_id is required for CSV parsing")

        # Get form details
        form_id = kwargs.get('form_id', path.stem)
        form_name = kwargs.get('form_name', self._format_name(path.stem))
        table_name = f"app_fd_{form_id}"

        # Create fields from columns
        fields = self._create_fields_from_columns(columns)

        # Create form
        form = FormSpec(
            id=form_id,
            name=form_name,
            table=table_name,
            fields=fields
        )

        # Create app metadata
        metadata = AppMetadata(
            app_id=app_id,
            app_name=kwargs.get('app_name', app_id.title())
        )

        # Build AppSpec
        app_spec = AppSpec(
            version="1.0",
            metadata=metadata,
            forms=[form]
        )

        return self._validate_result(app_spec)

    def _create_fields_from_columns(self, columns: list) -> list:
        """Create field specs from CSV columns"""
        fields = []

        for i, col in enumerate(columns):
            # Skip 'id' column if present
            if col.lower() == 'id':
                continue

            # Determine field properties
            is_primary = (col == 'code' or i == 0)
            required = is_primary

            field = FieldSpec(
                id=col,
                type=FieldType.TEXT,
                label=col.replace('_', ' ').title(),
                size=100 if col == 'code' else 255,
                required=required,
                primary_key=is_primary
            )
            fields.append(field)

        return fields

    def _format_name(self, filename: str) -> str:
        """Format filename as human-readable name"""
        # md01maritalStatus → MD.01 - Marital Status
        import re
        match = re.match(r'md(\d+)(.+)', filename, re.IGNORECASE)
        if match:
            number = match.group(1)
            name_part = match.group(2)
            # Convert camelCase to Title Case
            readable = re.sub(r'([A-Z])', r' \1', name_part).strip().title()
            return f"MD.{number} - {readable}"
        else:
            return filename.replace('_', ' ').title()
