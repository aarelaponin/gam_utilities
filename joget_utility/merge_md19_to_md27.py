#!/usr/bin/env python3
"""
Merge md19crops data into md27input.csv
Transforms 21 crop records to SEEDS category in md27input format
"""
import csv
from pathlib import Path

print("=" * 80)
print("MERGING md19crops INTO md27input")
print("=" * 80)
print()

# File paths
md19_csv = Path('data/metadata/md19crops.csv')
md27_csv = Path('data/metadata/md27input.csv')
backup_csv = Path('data/metadata/md27input.csv.backup')

# Backup existing md27input.csv
print(f"Backing up {md27_csv} → {backup_csv}")
with open(md27_csv, 'r') as src:
    with open(backup_csv, 'w') as dst:
        dst.write(src.read())
print(f"✓ Backup created")
print()

# Read existing md27input records
print(f"Reading existing md27input records...")
existing_records = []
with open(md27_csv, 'r') as f:
    reader = csv.DictReader(f)
    existing_records = list(reader)
print(f"✓ Found {len(existing_records)} existing records")

# Read md19crops records
print(f"Reading md19crops records...")
md19_records = []
with open(md19_csv, 'r') as f:
    reader = csv.DictReader(f)
    md19_records = list(reader)
print(f"✓ Found {len(md19_records)} crop records")
print()

# Transform md19crops to md27input format
print("Transforming md19crops records to md27input format...")
seeds_records = []
for crop in md19_records:
    transformed = {
        'code': crop['code'],
        'name': crop['name'],
        'input_category': 'SEEDS',
        'category': crop['crop_category'],
        'pesticide_type': '',
        'default_unit': 'kg',
        'typical_quantity': '',
        'typical_quantity_per_ha': '5-25 kg',
        'target': '',
        'estimated_cost_per_unit': ''
    }
    seeds_records.append(transformed)
    print(f"  {crop['code']}: {crop['name']} → SEEDS/{crop['crop_category']}")

print(f"✓ Transformed {len(seeds_records)} records")
print()

# Merge records
all_records = existing_records + seeds_records
print(f"Merging records:")
print(f"  Existing: {len(existing_records)}")
print(f"  SEEDS:    {len(seeds_records)}")
print(f"  Total:    {len(all_records)}")
print()

# Write merged CSV
print(f"Writing merged data to {md27_csv}...")
fieldnames = [
    'code', 'name', 'input_category', 'category', 'pesticide_type',
    'default_unit', 'typical_quantity', 'typical_quantity_per_ha',
    'target', 'estimated_cost_per_unit'
]
with open(md27_csv, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_records)

print(f"✓ Written {len(all_records)} records")
print()

# Verify by category
print("=" * 80)
print("VERIFICATION")
print("=" * 80)
category_counts = {}
for rec in all_records:
    cat = rec['input_category']
    category_counts[cat] = category_counts.get(cat, 0) + 1

for cat, count in sorted(category_counts.items()):
    print(f"{cat}: {count} records")

print()
print("Sample SEEDS records:")
seeds_sample = [r for r in all_records if r['input_category'] == 'SEEDS'][:3]
for rec in seeds_sample:
    print(f"  {rec['code']}: {rec['name']} ({rec['category']})")

print()
print("=" * 80)
print("✅ MERGE COMPLETE")
print("=" * 80)
print()
print("Next steps:")
print("1. Deploy md27 forms: python joget_utility.py --deploy-master-data --yes")
print("2. md27inputCategory will have 8 records")
print("3. md27input will have 61 records (40 + 21 SEEDS)")
print()