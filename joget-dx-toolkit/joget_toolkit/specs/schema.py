"""
Canonical format schema for form specifications.

This module defines the Pydantic models that represent the canonical YAML format
used as the intermediate representation between input formats and platform outputs.

The canonical format is designed to be:
- Platform-agnostic (works for Joget, Django, Spring, etc.)
- Type-safe (validated by Pydantic)
- Human-readable (YAML-friendly)
- Extensible (can add new field types and properties)
"""

from enum import Enum
from typing import List, Optional, Union, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator, model_validator


class FieldType(str, Enum):
    """Supported field types in canonical format"""
    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    SELECT = "select"
    RADIO = "radio"
    CHECKBOX = "checkbox"
    DATE = "date"
    DATETIME = "datetime"
    TIME = "time"
    FILE = "file"
    FOREIGN_KEY = "foreign_key"
    HIDDEN = "hidden"

    def __str__(self):
        return self.value


class SelectOption(BaseModel):
    """Option for select/radio/checkbox fields"""
    value: str = Field(..., description="Internal value")
    label: Optional[str] = Field(None, description="Display label (defaults to value)")

    @model_validator(mode='after')
    def set_label_default(self):
        """Set label to value if not provided"""
        if self.label is None:
            self.label = self.value
        return self


class ForeignKeyRef(BaseModel):
    """Foreign key reference to another form"""
    form: str = Field(..., description="Referenced form ID")
    field: str = Field(..., description="Referenced field name (usually 'code' or 'id')")
    label_field: str = Field(..., description="Field to display in dropdown (usually 'name')")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters for query")


class ValidatorConfig(BaseModel):
    """Field validator configuration"""
    type: Literal["required", "email", "regex", "range", "unique"] = Field(
        ..., description="Validator type"
    )
    message: Optional[str] = Field(None, description="Custom error message")
    params: Optional[Dict[str, Any]] = Field(None, description="Validator-specific parameters")


class FieldSpec(BaseModel):
    """Field specification in canonical format"""
    id: str = Field(..., description="Field identifier (database column name)")
    type: FieldType = Field(..., description="Field type")
    label: str = Field(..., description="Human-readable label")

    # Constraints
    size: Optional[int] = Field(None, description="Maximum length for text fields")
    required: bool = Field(False, description="Whether field is required")
    readonly: bool = Field(False, description="Whether field is read-only")
    unique: bool = Field(False, description="Whether value must be unique")

    # Default values
    default: Optional[str] = Field(None, description="Default value or formula (e.g., 'uuid', 'currentDateTime')")

    # Field-type specific
    options: Optional[List[Union[str, SelectOption]]] = Field(
        None, description="Options for select/radio/checkbox fields"
    )
    references: Optional[ForeignKeyRef] = Field(None, description="Foreign key configuration")

    # Metadata
    description: Optional[str] = Field(None, description="Help text or description")
    placeholder: Optional[str] = Field(None, description="Placeholder text")
    primary_key: bool = Field(False, description="Whether this is the primary key")

    # Validation
    validators: Optional[List[ValidatorConfig]] = Field(None, description="Field validators")

    @field_validator('options')
    @classmethod
    def normalize_options(cls, v, info):
        """Convert string options to SelectOption objects"""
        if v is None:
            return None

        normalized = []
        for opt in v:
            if isinstance(opt, str):
                normalized.append(SelectOption(value=opt, label=opt))
            else:
                normalized.append(opt)
        return normalized

    @model_validator(mode='after')
    def validate_field_constraints(self):
        """Validate field-specific constraints"""
        # Select fields must have options or foreign key
        if self.type in (FieldType.SELECT, FieldType.RADIO, FieldType.CHECKBOX):
            if not self.options and not self.references:
                raise ValueError(
                    f"Field '{self.id}': {self.type} fields must have either 'options' or 'references'"
                )

        # Foreign key fields must have references
        if self.type == FieldType.FOREIGN_KEY:
            if not self.references:
                raise ValueError(f"Field '{self.id}': foreign_key fields must have 'references'")

        # Text fields with size > 255 should use textarea
        if self.type == FieldType.TEXT and self.size and self.size > 255:
            raise ValueError(
                f"Field '{self.id}': TEXT fields with size > 255 should use type 'textarea'"
            )

        return self


class IndexSpec(BaseModel):
    """Database index specification"""
    fields: List[str] = Field(..., min_length=1, description="Fields included in index")
    unique: bool = Field(False, description="Whether index enforces uniqueness")
    name: Optional[str] = Field(None, description="Index name (auto-generated if not provided)")


class FormSpec(BaseModel):
    """Form specification in canonical format"""
    id: str = Field(..., description="Form identifier (must be unique within app)")
    name: str = Field(..., description="Human-readable form name")
    table: str = Field(..., description="Database table name")

    # Fields
    fields: List[FieldSpec] = Field(..., min_length=1, description="Form fields")

    # Optional metadata
    description: Optional[str] = Field(None, description="Form description")
    category: Optional[str] = Field(None, description="Form category for organization")

    # Database configuration
    indexes: Optional[List[IndexSpec]] = Field(None, description="Database indexes")

    # Form behavior
    allow_create: bool = Field(True, description="Allow creating new records")
    allow_update: bool = Field(True, description="Allow updating records")
    allow_delete: bool = Field(True, description="Allow deleting records")

    @field_validator('id')
    @classmethod
    def validate_form_id(cls, v):
        """Validate form ID format"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError(f"Form ID '{v}' must contain only alphanumeric characters, underscores, and hyphens")
        return v

    @field_validator('table')
    @classmethod
    def validate_table_name(cls, v):
        """Validate table name (Joget has 20 char limit)"""
        if len(v) > 64:
            raise ValueError(f"Table name '{v}' exceeds 64 characters (database limit)")
        return v

    @model_validator(mode='after')
    def validate_form_constraints(self):
        """Validate form-level constraints"""
        # Must have at least one primary key
        primary_keys = [f for f in self.fields if f.primary_key]
        if not primary_keys:
            raise ValueError(f"Form '{self.id}' must have at least one primary key field")

        # Validate index field references
        if self.indexes:
            field_ids = {f.id for f in self.fields}
            for idx in self.indexes:
                for field_name in idx.fields:
                    if field_name not in field_ids:
                        raise ValueError(
                            f"Form '{self.id}': Index references non-existent field '{field_name}'"
                        )

        # Validate foreign key references (field must exist in this form)
        for field in self.fields:
            if field.references:
                # Note: We can't validate if referenced form exists at this level
                # That validation happens in AppSpec
                pass

        return self


class AppMetadata(BaseModel):
    """Application metadata"""
    app_id: str = Field(..., description="Application identifier")
    app_name: str = Field(..., description="Application display name")
    description: Optional[str] = Field(None, description="Application description")
    version: Optional[str] = Field("1.0", description="Application version")
    author: Optional[str] = Field(None, description="Application author")


class AppSpec(BaseModel):
    """Complete application specification in canonical format"""
    version: str = Field(default="1.0", description="Canonical format version")
    metadata: AppMetadata = Field(..., description="Application metadata")
    forms: List[FormSpec] = Field(..., min_length=1, description="Forms in this application")

    @field_validator('version')
    @classmethod
    def validate_version(cls, v):
        """Validate canonical format version"""
        if v != "1.0":
            raise ValueError(f"Unsupported canonical format version: {v}")
        return v

    @model_validator(mode='after')
    def validate_app_constraints(self):
        """Validate application-level constraints"""
        # Check for duplicate form IDs
        form_ids = [f.id for f in self.forms]
        duplicates = [fid for fid in form_ids if form_ids.count(fid) > 1]
        if duplicates:
            raise ValueError(f"Duplicate form IDs found: {', '.join(set(duplicates))}")

        # Validate foreign key references point to existing forms
        form_id_set = set(form_ids)
        for form in self.forms:
            for field in form.fields:
                if field.references and field.references.form not in form_id_set:
                    raise ValueError(
                        f"Form '{form.id}', field '{field.id}': "
                        f"References non-existent form '{field.references.form}'"
                    )

        return self

    def get_form(self, form_id: str) -> Optional[FormSpec]:
        """Get form by ID"""
        for form in self.forms:
            if form.id == form_id:
                return form
        return None

    def get_form_dependencies(self, form_id: str) -> List[str]:
        """Get list of form IDs that this form depends on (via foreign keys)"""
        form = self.get_form(form_id)
        if not form:
            return []

        dependencies = []
        for field in form.fields:
            if field.references and field.references.form != form_id:
                dependencies.append(field.references.form)

        return list(set(dependencies))

    def get_deployment_order(self) -> List[str]:
        """
        Get forms in deployment order (forms with no dependencies first).
        Uses topological sort to handle foreign key dependencies.
        """
        # Build dependency graph
        graph = {form.id: self.get_form_dependencies(form.id) for form in self.forms}

        # Topological sort (Kahn's algorithm)
        in_degree = {form_id: 0 for form_id in graph}
        for deps in graph.values():
            for dep in deps:
                in_degree[dep] = in_degree.get(dep, 0) + 1

        queue = [form_id for form_id, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            node = queue.pop(0)
            result.append(node)

            for dependent in graph.get(node, []):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(result) != len(graph):
            raise ValueError("Circular dependency detected in forms")

        return result
