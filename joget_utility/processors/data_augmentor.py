#!/usr/bin/env python3
"""
Data Augmentor
Augments CSV data with foreign key values for Pattern 2 (subcategory source) relationships.

SINGLE RESPONSIBILITY: Add FK columns to CSV data
Does NOT: Deploy, validate relationships, or generate forms

Critical for Pattern 2: Child CSV does NOT contain FK column,
but Joget form requires it for nested LOV cascading to work.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging

from .csv_processor import CSVProcessor
from .relationship_detector import RelationshipInfo


@dataclass
class AugmentationResult:
    """Result of data augmentation operation"""
    original_columns: List[str]
    augmented_columns: List[str]
    injected_field: str
    injected_value: str
    record_count: int
    success: bool
    error: Optional[str] = None


class DataAugmentor:
    """
    Augment CSV data with FK values for Pattern 2 relationships.

    Example transformation:

    Input CSV (md25tillageEquipment.csv):
        code              | name                    | power_source
        ----------------------------------------------------------
        PLOUGH_ANIMAL     | Animal-Drawn Plough     | animal
        PLOUGH_TRACTOR    | Tractor Plough          | tractor

    Output (augmented):
        code              | equipment_category_code | name                    | power_source
        -------------------------------------------------------------------------------------
        PLOUGH_ANIMAL     | TILLAGE                 | Animal-Drawn Plough     | animal
        PLOUGH_TRACTOR    | TILLAGE                 | Tractor Plough          | tractor
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize data augmentor.

        Args:
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger('joget_utility.data_augmentor')
        self.csv_processor = CSVProcessor()

    def augment_csv_data(self,
                        csv_path: Path,
                        relationship: RelationshipInfo) -> Tuple[pd.DataFrame, AugmentationResult]:
        """
        Augment CSV data with FK column and value.

        Args:
            csv_path: Path to child CSV file
            relationship: RelationshipInfo for this form

        Returns:
            Tuple of (augmented DataFrame, AugmentationResult)

        Raises:
            ValueError: If augmentation cannot be performed
        """
        if not relationship.needs_fk_injection:
            raise ValueError(
                f"Relationship does not require FK injection: {relationship.child_form}"
            )

        if not relationship.fk_value_to_inject:
            raise ValueError(
                f"No FK value specified for injection: {relationship.child_form}"
            )

        try:
            # Read CSV data
            records = self.csv_processor.read_file(csv_path)

            if not records:
                raise ValueError(f"Empty CSV file: {csv_path}")

            # Convert to DataFrame for easier manipulation
            df = pd.DataFrame(records)
            original_columns = list(df.columns)

            self.logger.info(f"Augmenting {len(df)} records from {csv_path.name}")
            self.logger.debug(f"Original columns: {', '.join(original_columns)}")

            # Check if FK column already exists
            fk_field = relationship.child_foreign_key
            if fk_field in df.columns:
                self.logger.warning(
                    f"FK column '{fk_field}' already exists in CSV. "
                    f"This should not happen for Pattern 2 relationships."
                )
                # Return original data
                result = AugmentationResult(
                    original_columns=original_columns,
                    augmented_columns=list(df.columns),
                    injected_field=fk_field,
                    injected_value=relationship.fk_value_to_inject,
                    record_count=len(df),
                    success=True,
                    error="FK column already exists - no augmentation needed"
                )
                return df, result

            # Add FK column with constant value
            fk_value = relationship.fk_value_to_inject
            df[fk_field] = fk_value

            # Reorder columns: [primary_key, foreign_key, ...other_fields]
            primary_key = self._detect_primary_key(original_columns, records)

            # Build new column order
            new_column_order = [primary_key, fk_field]
            for col in original_columns:
                if col != primary_key:
                    new_column_order.append(col)

            df = df[new_column_order]

            augmented_columns = list(df.columns)

            self.logger.info(f"✓ Injected FK column: {fk_field} = '{fk_value}'")
            self.logger.debug(f"Augmented columns: {', '.join(augmented_columns)}")

            result = AugmentationResult(
                original_columns=original_columns,
                augmented_columns=augmented_columns,
                injected_field=fk_field,
                injected_value=fk_value,
                record_count=len(df),
                success=True
            )

            return df, result

        except Exception as e:
            self.logger.error(f"Error augmenting data from {csv_path}: {e}")

            result = AugmentationResult(
                original_columns=[],
                augmented_columns=[],
                injected_field=relationship.child_foreign_key,
                injected_value=relationship.fk_value_to_inject or '',
                record_count=0,
                success=False,
                error=str(e)
            )

            raise ValueError(f"Data augmentation failed: {e}")

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

    def validate_parent_existence(self,
                                  parent_csv_path: Path,
                                  parent_code_value: str,
                                  parent_primary_key: str = 'code') -> bool:
        """
        Validate that parent category code exists in parent CSV.

        Args:
            parent_csv_path: Path to parent CSV file
            parent_code_value: Code value to check (e.g., 'TILLAGE')
            parent_primary_key: Parent's primary key column name

        Returns:
            True if parent code exists, False otherwise
        """
        try:
            records = self.csv_processor.read_file(parent_csv_path)

            if not records:
                self.logger.warning(f"Parent CSV is empty: {parent_csv_path}")
                return False

            # Check if code exists
            parent_codes = [r.get(parent_primary_key) for r in records]

            if parent_code_value in parent_codes:
                self.logger.debug(
                    f"✓ Parent code '{parent_code_value}' found in {parent_csv_path.name}"
                )
                return True
            else:
                self.logger.error(
                    f"✗ Parent code '{parent_code_value}' NOT found in {parent_csv_path.name}"
                )
                self.logger.debug(f"Available codes: {', '.join(parent_codes)}")
                return False

        except Exception as e:
            self.logger.error(f"Error validating parent existence: {e}")
            return False

    def convert_dataframe_to_records(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Convert augmented DataFrame back to list of records for API posting.

        Args:
            df: Augmented pandas DataFrame

        Returns:
            List of dictionaries (records)
        """
        # Replace NaN with None for JSON serialization
        df = df.where(pd.notna(df), None)

        # Convert to list of dicts
        records = df.to_dict('records')

        return records

    def save_augmentation_report(self,
                                 augmentation_results: List[AugmentationResult],
                                 output_path: Path) -> None:
        """
        Save augmentation report to CSV file.

        Args:
            augmentation_results: List of augmentation results
            output_path: Path to output CSV file
        """
        report_data = []

        for result in augmentation_results:
            report_data.append({
                'injected_field': result.injected_field,
                'injected_value': result.injected_value,
                'record_count': result.record_count,
                'success': result.success,
                'error': result.error or '',
                'original_column_count': len(result.original_columns),
                'augmented_column_count': len(result.augmented_columns),
                'original_columns': ', '.join(result.original_columns),
                'augmented_columns': ', '.join(result.augmented_columns)
            })

        df = pd.DataFrame(report_data)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)

        self.logger.info(f"Saved augmentation report to: {output_path}")
