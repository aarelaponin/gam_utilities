#!/usr/bin/env python3
"""
Relationship Detector
Detects parent-child relationships between metadata CSV files.

SINGLE RESPONSIBILITY: Analyze CSV files and detect relationships
Does NOT: Generate forms, deploy, or populate data

Supports two relationship patterns:
1. Traditional FK: Child CSV contains foreign key column referencing parent
2. Subcategory Source: Child CSV does NOT contain FK, relationship defined by config
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import logging

from .csv_processor import CSVProcessor


@dataclass
class RelationshipInfo:
    """Information about a parent-child relationship"""
    pattern_type: str  # 'traditional_fk' or 'subcategory_source'
    parent_form: str
    parent_csv: str
    parent_primary_key: str
    parent_code_value: Optional[str]  # For Pattern 2: specific category value
    child_form: str
    child_csv: str
    child_foreign_key: str  # Generated name if not in CSV
    relationship_type: str  # 'nested_lov'
    needs_fk_injection: bool  # True if FK not in child CSV
    fk_value_to_inject: Optional[str]  # For Pattern 2: value to inject
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class HierarchyLevel:
    """Single level in a hierarchy"""
    form: Optional[str] = None  # Single form at this level
    forms: Optional[List[str]] = None  # Multiple forms at this level
    level: int = 0
    parent: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = {'level': self.level}
        if self.form:
            result['form'] = self.form
        if self.forms:
            result['forms'] = self.forms
        if self.parent:
            result['parent'] = self.parent
        return result


@dataclass
class Hierarchy:
    """Complete hierarchy definition"""
    name: str
    pattern: str  # 'traditional_fk' or 'subcategory_source'
    levels: List[HierarchyLevel]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'pattern': self.pattern,
            'levels': [level.to_dict() for level in self.levels]
        }


class RelationshipDetector:
    """
    Detect parent-child relationships in metadata CSV files.

    Supports two patterns:
    1. Traditional FK: Detects FK columns in child CSV
    2. Subcategory Source: Uses config mappings to identify relationships
    """

    # Patterns to detect foreign key columns
    FK_PATTERNS = [
        r'^(.+)_code$',
        r'^(.+)_id$',
        r'^(.+)_type$',
        r'^(.+)_category$',
    ]

    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        Initialize relationship detector.

        Args:
            config: Configuration dictionary (from joget.yaml)
            logger: Logger instance
        """
        self.config = config
        self.logger = logger or logging.getLogger('joget_utility.relationship_detector')
        self.csv_processor = CSVProcessor()

        # Load subcategory mappings from config
        self.subcategory_mappings = config.get('subcategory_mappings', {})
        self.metadata_config = config.get('metadata', {})

    def detect_all_relationships(self, csv_dir: Path) -> Tuple[List[RelationshipInfo], List[Hierarchy]]:
        """
        Detect all relationships in metadata directory.

        Args:
            csv_dir: Directory containing CSV files

        Returns:
            Tuple of (relationships, hierarchies)
        """
        self.logger.info(f"Scanning for CSV files in: {csv_dir}")

        # Get all CSV files
        csv_files = sorted(csv_dir.glob('*.csv'))
        if not csv_files:
            self.logger.warning(f"No CSV files found in {csv_dir}")
            return [], []

        self.logger.info(f"Found {len(csv_files)} CSV files")

        # Build metadata about all CSVs
        csv_metadata = self._analyze_all_csvs(csv_files)

        # Detect relationships
        relationships = []

        # Pattern 1: Traditional FK detection
        pattern1_rels = self._detect_traditional_fk_relationships(csv_metadata)
        relationships.extend(pattern1_rels)
        self.logger.info(f"Detected {len(pattern1_rels)} traditional FK relationships")

        # Pattern 2: Subcategory source detection
        pattern2_rels = self._detect_subcategory_source_relationships(csv_metadata)
        relationships.extend(pattern2_rels)
        self.logger.info(f"Detected {len(pattern2_rels)} subcategory source relationships")

        # Build hierarchies
        hierarchies = self._build_hierarchies(relationships)
        self.logger.info(f"Built {len(hierarchies)} hierarchies")

        return relationships, hierarchies

    def _analyze_all_csvs(self, csv_files: List[Path]) -> Dict[str, Dict[str, Any]]:
        """
        Analyze structure of all CSV files.

        Returns:
            Dictionary mapping form_id to CSV metadata
        """
        csv_metadata = {}

        for csv_path in csv_files:
            form_id = csv_path.stem

            try:
                # Read CSV to get column information
                records = self.csv_processor.read_file(csv_path)

                if not records:
                    self.logger.warning(f"Empty CSV: {csv_path}")
                    continue

                columns = list(records[0].keys())

                # Detect primary key
                primary_key = self._detect_primary_key(columns, records)

                metadata = {
                    'form_id': form_id,
                    'csv_path': csv_path,
                    'csv_name': csv_path.name,
                    'columns': columns,
                    'primary_key': primary_key,
                    'record_count': len(records),
                    'records': records  # Keep for FK validation
                }

                csv_metadata[form_id] = metadata

            except Exception as e:
                self.logger.error(f"Error analyzing {csv_path}: {e}")
                continue

        return csv_metadata

    def _detect_primary_key(self, columns: List[str], records: List[Dict]) -> str:
        """
        Detect primary key column.

        Rules (in priority order):
        1. Column named 'id' or 'code'
        2. Column ending with '_id' or '_code'
        3. First column with unique values
        4. First column as fallback
        """
        # Rule 1: exact match
        for col in ['id', 'code']:
            if col in columns:
                return col

        # Rule 2: suffix match
        for col in columns:
            if col.endswith('_id') or col.endswith('_code'):
                return col

        # Rule 3: check uniqueness
        for col in columns:
            values = [r.get(col) for r in records]
            if len(values) == len(set(values)):
                return col

        # Rule 4: fallback
        return columns[0] if columns else 'id'

    def _detect_traditional_fk_relationships(self,
                                            csv_metadata: Dict[str, Dict[str, Any]]) -> List[RelationshipInfo]:
        """
        Detect Pattern 1: Traditional FK relationships.

        Child CSV contains a column that references parent CSV's primary key.
        """
        relationships = []

        for child_form_id, child_meta in csv_metadata.items():
            columns = child_meta['columns']

            # Check each column for FK pattern
            for column in columns:
                # Skip primary key
                if column == child_meta['primary_key']:
                    continue

                # Check FK patterns
                parent_form_candidate = None

                for pattern in self.FK_PATTERNS:
                    match = re.match(pattern, column)
                    if match:
                        parent_name = match.group(1)

                        # Look for parent CSV
                        # Try exact match first
                        if parent_name in csv_metadata:
                            parent_form_candidate = parent_name
                            break

                        # Try with md prefix
                        for form_id in csv_metadata.keys():
                            if form_id.endswith(parent_name) or parent_name in form_id:
                                parent_form_candidate = form_id
                                break

                if parent_form_candidate and parent_form_candidate in csv_metadata:
                    parent_meta = csv_metadata[parent_form_candidate]

                    # Create relationship
                    relationship = RelationshipInfo(
                        pattern_type='traditional_fk',
                        parent_form=parent_meta['form_id'],
                        parent_csv=parent_meta['csv_name'],
                        parent_primary_key=parent_meta['primary_key'],
                        parent_code_value=None,
                        child_form=child_meta['form_id'],
                        child_csv=child_meta['csv_name'],
                        child_foreign_key=column,
                        relationship_type='nested_lov',
                        needs_fk_injection=False,  # FK already in CSV
                        fk_value_to_inject=None,
                        notes="Traditional FK pattern - FK column exists in child CSV"
                    )

                    relationships.append(relationship)
                    self.logger.debug(f"Found traditional FK: {child_form_id}.{column} → {parent_form_candidate}")

        return relationships

    def _detect_subcategory_source_relationships(self,
                                                 csv_metadata: Dict[str, Dict[str, Any]]) -> List[RelationshipInfo]:
        """
        Detect Pattern 2: Subcategory source relationships.

        Uses subcategory_mappings from config to identify relationships
        where child CSV does NOT contain FK column.
        """
        relationships = []

        for parent_form, category_mappings in self.subcategory_mappings.items():
            if parent_form not in csv_metadata:
                self.logger.warning(f"Parent form {parent_form} not found in CSV files")
                continue

            parent_meta = csv_metadata[parent_form]

            # Generate FK field name from parent form
            # Example: md25equipmentCategory → equipment_category_code
            fk_field_name = self._derive_fk_field_name(parent_form)

            for category_code, child_form in category_mappings.items():
                if child_form not in csv_metadata:
                    self.logger.warning(f"Child form {child_form} not found in CSV files")
                    continue

                child_meta = csv_metadata[child_form]

                # Create relationship
                relationship = RelationshipInfo(
                    pattern_type='subcategory_source',
                    parent_form=parent_meta['form_id'],
                    parent_csv=parent_meta['csv_name'],
                    parent_primary_key=parent_meta['primary_key'],
                    parent_code_value=category_code,
                    child_form=child_meta['form_id'],
                    child_csv=child_meta['csv_name'],
                    child_foreign_key=fk_field_name,
                    relationship_type='nested_lov',
                    needs_fk_injection=True,  # FK NOT in CSV
                    fk_value_to_inject=category_code,
                    notes=f"Subcategory source pattern - FK will be injected with value '{category_code}'"
                )

                relationships.append(relationship)
                self.logger.debug(f"Found subcategory source: {parent_form}[{category_code}] → {child_form}")

        return relationships

    def _derive_fk_field_name(self, parent_form: str) -> str:
        """
        Derive FK field name from parent form name.

        Examples:
        - md25equipmentCategory → equipment_category_code
        - md27inputCategory → input_category_code
        - md03district → district_code
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

    def _build_hierarchies(self, relationships: List[RelationshipInfo]) -> List[Hierarchy]:
        """
        Build hierarchy trees from relationships.
        """
        hierarchies = []

        # Group by parent form
        parent_groups = defaultdict(list)
        for rel in relationships:
            parent_groups[rel.parent_form].append(rel)

        # Build hierarchy for each parent
        for parent_form, rels in parent_groups.items():
            # Determine hierarchy name and pattern
            pattern = rels[0].pattern_type

            if 'equipment' in parent_form.lower():
                name = 'equipment_hierarchy'
            elif 'input' in parent_form.lower():
                name = 'input_hierarchy'
            elif 'district' in parent_form.lower():
                name = 'geographic_hierarchy'
            else:
                name = f"{parent_form}_hierarchy"

            # Build levels
            levels = [
                HierarchyLevel(form=parent_form, level=0, parent=None)
            ]

            # Add child level
            child_forms = [rel.child_form for rel in rels]
            if len(child_forms) == 1:
                levels.append(HierarchyLevel(form=child_forms[0], level=1, parent=parent_form))
            else:
                levels.append(HierarchyLevel(forms=child_forms, level=1, parent=parent_form))

            hierarchy = Hierarchy(name=name, pattern=pattern, levels=levels)
            hierarchies.append(hierarchy)

        return hierarchies

    def save_relationships_metadata(self,
                                   relationships: List[RelationshipInfo],
                                   hierarchies: List[Hierarchy],
                                   output_path: Path) -> None:
        """
        Save relationships and hierarchies to JSON file.

        Args:
            relationships: List of detected relationships
            hierarchies: List of built hierarchies
            output_path: Path to output JSON file
        """
        from datetime import datetime

        metadata = {
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'total_relationships': len(relationships),
            'pattern1_count': len([r for r in relationships if r.pattern_type == 'traditional_fk']),
            'pattern2_count': len([r for r in relationships if r.pattern_type == 'subcategory_source']),
            'relationships': [rel.to_dict() for rel in relationships],
            'hierarchies': [h.to_dict() for h in hierarchies]
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        self.logger.info(f"Saved relationships metadata to: {output_path}")

    def load_relationships_metadata(self, metadata_path: Path) -> Tuple[List[RelationshipInfo], List[Hierarchy]]:
        """
        Load relationships from JSON file.

        Returns:
            Tuple of (relationships, hierarchies)
        """
        if not metadata_path.exists():
            raise FileNotFoundError(f"Relationships metadata not found: {metadata_path}")

        with open(metadata_path, 'r') as f:
            data = json.load(f)

        # Reconstruct relationships
        relationships = []
        for rel_dict in data.get('relationships', []):
            rel = RelationshipInfo(**rel_dict)
            relationships.append(rel)

        # Reconstruct hierarchies (simple reconstruction - just store as dict)
        hierarchies = data.get('hierarchies', [])

        return relationships, hierarchies
