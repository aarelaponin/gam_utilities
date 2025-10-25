#!/usr/bin/env python3
"""
Merge MD25 and MD27 subcategory CSVs into unified tables

MD25: 9 equipment subcategories → 1 md25equipment table (93 items)
MD27: 4 input subcategories → 1 md27input table (40 items)
"""

import pandas as pd
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent
METADATA_DIR = BASE_DIR / 'data' / 'metadata'

print("=" * 80)
print("MERGING MD25 EQUIPMENT SUBCATEGORIES")
print("=" * 80)
print()

# ============================================================================
# MD25 EQUIPMENT - Merge 9 subcategory tables
# ============================================================================

# Define unified schema (ALL columns from all 9 tables)
md25_columns = [
    'code',
    'name',
    'equipment_category',  # NEW: FK to md25equipmentCategory
    'estimated_cost_lsl',
    'tool_category',        # GENERAL_TOOLS
    'typical_quantity',     # GENERAL_TOOLS
    'irrigation_type',      # IRRIGATION
    'area_coverage_ha',     # IRRIGATION
    'equipment_type',       # LIVESTOCK_EQUIP
    'purpose',              # LIVESTOCK_EQUIP
    'sprayer_type',         # PEST_CONTROL
    'capacity_litres',      # PEST_CONTROL
    'planting_type',        # PLANTING
    'processing_type',      # PROCESSING
    'storage_type',         # STORAGE
    'transport_type',       # TRANSPORT
    'capacity',             # PLANTING, PROCESSING, STORAGE, TRANSPORT
    'power_source',         # PEST_CONTROL, PROCESSING, TILLAGE
    'material',             # STORAGE
    'typical_lifespan_years',  # TILLAGE
    'maintenance_level'     # TILLAGE
]

# Mapping: filename → equipment_category value
md25_file_category_map = {
    'md25generalTools.csv': 'GENERAL_TOOLS',
    'md25irrigationEquipment.csv': 'IRRIGATION',
    'md25livestockEquipment.csv': 'LIVESTOCK_EQUIP',
    'md25pestControlEquipment.csv': 'PEST_CONTROL',
    'md25plantingEquipment.csv': 'PLANTING',
    'md25processingEquipment.csv': 'PROCESSING',
    'md25storageEquipment.csv': 'STORAGE',
    'md25tillageEquipment.csv': 'TILLAGE',
    'md25transportEquipment.csv': 'TRANSPORT'
}

md25_merged = []
total_md25_records = 0

for filename, category in md25_file_category_map.items():
    file_path = METADATA_DIR / filename

    if not file_path.exists():
        print(f"⚠️  WARNING: {filename} not found, skipping...")
        continue

    df = pd.read_csv(file_path)
    record_count = len(df)
    total_md25_records += record_count

    # Add equipment_category column
    df['equipment_category'] = category

    # Reindex to include all columns (missing ones become NaN)
    df = df.reindex(columns=md25_columns)

    md25_merged.append(df)

    print(f"✓ {filename:40} → {category:20} ({record_count:2} records)")

# Concatenate all dataframes
md25_result = pd.concat(md25_merged, ignore_index=True)

# Save merged file
output_file = METADATA_DIR / 'md25equipment.csv'
md25_result.to_csv(output_file, index=False)

print()
print(f"✓ Created: {output_file}")
print(f"  Total records: {total_md25_records}")
print(f"  Columns: {len(md25_columns)}")
print()

# ============================================================================
# MD27 INPUT - Merge 4 subcategory tables
# ============================================================================

print("=" * 80)
print("MERGING MD27 INPUT SUBCATEGORIES")
print("=" * 80)
print()

# Define unified schema (ALL columns from all 4 tables)
md27_columns = [
    'code',
    'name',
    'input_category',          # NEW: FK to md27inputCategory
    'category',                # FERTILIZER, IRRIGATION, LIVESTOCK_VET (subcategory)
    'pesticide_type',          # PESTICIDES
    'default_unit',           # ALL
    'typical_quantity',        # IRRIGATION, LIVESTOCK_VET
    'typical_quantity_per_ha', # FERTILIZER, PESTICIDES
    'target',                  # PESTICIDES
    'estimated_cost_per_unit'  # ALL
]

# Mapping: filename → input_category value
md27_file_category_map = {
    'md27fertilizer.csv': 'FERTILIZER',
    'md27pesticide.csv': 'PESTICIDES',
    'md27irrigation.csv': 'IRRIGATION',
    'md27livestockSupply.csv': 'LIVESTOCK_VET'
}

md27_merged = []
total_md27_records = 0

for filename, category in md27_file_category_map.items():
    file_path = METADATA_DIR / filename

    if not file_path.exists():
        print(f"⚠️  WARNING: {filename} not found, skipping...")
        continue

    df = pd.read_csv(file_path)
    record_count = len(df)
    total_md27_records += record_count

    # Add input_category column
    df['input_category'] = category

    # Reindex to include all columns (missing ones become NaN)
    df = df.reindex(columns=md27_columns)

    md27_merged.append(df)

    print(f"✓ {filename:40} → {category:20} ({record_count:2} records)")

# Concatenate all dataframes
md27_result = pd.concat(md27_merged, ignore_index=True)

# Save merged file
output_file = METADATA_DIR / 'md27input.csv'
md27_result.to_csv(output_file, index=False)

print()
print(f"✓ Created: {output_file}")
print(f"  Total records: {total_md27_records}")
print(f"  Columns: {len(md27_columns)}")
print()

# ============================================================================
# SUMMARY
# ============================================================================

print("=" * 80)
print("MERGE SUMMARY")
print("=" * 80)
print()
print(f"MD25 Equipment:")
print(f"  - Input: 9 separate CSV files")
print(f"  - Output: md25equipment.csv ({total_md25_records} records, {len(md25_columns)} columns)")
print()
print(f"MD27 Input:")
print(f"  - Input: 4 separate CSV files")
print(f"  - Output: md27input.csv ({total_md27_records} records, {len(md27_columns)} columns)")
print()
print("✓ Merge complete!")
print()
print("Next steps:")
print("  1. Review merged CSV files for correctness")
print("  2. Backup original files to .archive/")
print("  3. Generate Joget forms from merged CSVs")
print("=" * 80)
