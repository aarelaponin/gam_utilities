# MD19 Crops Merge into MD27 Input

**Date:** October 27, 2025
**Type:** Architecture Decision / Data Migration
**Impact:** md19crops form removed, data merged into md27input

---

## Executive Summary

**Problem:** md19crops was incorrectly implemented as a standalone form, causing deployment failures and architectural inconsistency.

**Solution:** Merged 21 crop records from md19crops into md27input as SEEDS category.

**Result:**
- md19crops form **removed** from deployment
- md27input expanded from 40 → 61 records
- Architecture now matches original design in md27inputCategory

---

## Background

### Original Design (md27inputCategory)

The md27inputCategory form defines input categories for agricultural inputs:

```csv
code,name,has_subcategory,subcategory_source,default_unit,typical_subsidy_percent
SEEDS,Seeds,Yes,md19crops,kg,70
FERTILIZER,Fertilizer,Yes,md27fertilizer,50kg_bags,60
PESTICIDES,Pesticides,Yes,md27pesticide,litres,65
IRRIGATION,Irrigation,Yes,md27irrigation,metres,50
LIVESTOCK_VET,Livestock & Vet,Yes,md27livestockSupply,doses,60
```

**Key observation:** SEEDS category has `subcategory_source: md19crops`

This indicates that crop data should be **referenced** from md19crops, but crops themselves should still be **part of the md27input polymorphic table**.

---

### Incorrect Implementation

md19crops was created as a **standalone form**:

**File:** `data/metadata_forms/md19crops.json`
```json
{
  "properties": {
    "id": "md19crops",
    "tableName": "md19crops",
    "name": "MD.19 - Crops"
  },
  "elements": [
    {"id": "code", "label": "Code"},
    {"id": "name", "label": "Name"},
    {"id": "crop_category", "label": "Crop Category"},
    {"id": "input_category_code", "label": "Input Category", "className": "SelectBox"}
  ]
}
```

**File:** `data/metadata/md19crops.csv` (21 records)
```csv
id,code,name,crop_category
1,maize,Maize,cereals
2,sorghum,Sorghum,cereals
...
28,other,Other,other
```

---

### Why This Was Wrong

1. **SelectBox with input_category_code**
   - Form tried to reference md27inputCategory (parent)
   - But md19crops data was meant to be child of SEEDS category
   - Circular reference: md27inputCategory → md19crops → md27inputCategory

2. **Violated Polymorphic Table Design**
   - md27input should contain ALL input types (SEEDS, FERTILIZER, PESTICIDES, etc.)
   - Each category differentiated by `input_category` field
   - Having separate md19crops table breaks this pattern

3. **Deployment Failures**
   - md19crops.csv had no `input_category_code` column
   - Form validation expected it (SelectBox with mandatory validator)
   - Result: 0/21 records posted, all rejected

---

## Correct Architecture

### Polymorphic Table Pattern

md27input is a **single unified table** with all input types:

| input_category | category | Fields Used |
|---------------|----------|-------------|
| SEEDS | cereals, legumes, tubers, vegetables | code, name, category |
| FERTILIZER | Compound, Nitrogen, Phosphorus | code, name, category, default_unit, typical_quantity_per_ha, estimated_cost_per_unit |
| PESTICIDES | Insecticide, Herbicide, Fungicide | code, name, pesticide_type, default_unit, target |
| IRRIGATION | Pipes, Drip System, Sprinkler | code, name, category, default_unit |
| LIVESTOCK_VET | Vaccine, Medicine, Feed | code, name, category, default_unit |

**Sparse Columns:** Each row only uses relevant fields, others are empty.

**Parent-Child Relationship:**
- md27inputCategory (parent) defines categories
- md27input (child) contains all input items with `input_category` FK
- SelectBox in md27input filters options by parent category

---

## Data Transformation

### Mapping: md19crops → md27input

```
md19crops field      → md27input field         | Value/Logic
─────────────────────────────────────────────────────────────
code                 → code                    | Direct copy
name                 → name                    | Direct copy
-                    → input_category          | "SEEDS" (constant)
crop_category        → category                | Direct copy (cereals, legumes, etc.)
-                    → pesticide_type          | Empty (N/A for seeds)
-                    → default_unit            | "kg" (from md27inputCategory.SEEDS)
-                    → typical_quantity        | Empty
-                    → typical_quantity_per_ha | "5-25 kg" (default for seeds)
-                    → target                  | Empty
-                    → estimated_cost_per_unit | Empty
```

### Example Transformation

**Before (md19crops.csv):**
```csv
code,name,crop_category
maize,Maize,cereals
```

**After (md27input.csv):**
```csv
code,name,input_category,category,pesticide_type,default_unit,typical_quantity,typical_quantity_per_ha,target,estimated_cost_per_unit
maize,Maize,SEEDS,cereals,,kg,,5-25 kg,,
```

---

## Implementation

### Script: merge_md19_to_md27.py

```python
# Read md19crops records
md19_records = read_csv('data/metadata/md19crops.csv')

# Transform to md27input format
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
    md27_records.append(transformed)

# Write merged CSV
write_csv('data/metadata/md27input.csv', md27_records)
```

**Execution:**
```bash
$ python merge_md19_to_md27.py

Transforming md19crops records to md27input format...
  maize: Maize → SEEDS/cereals
  sorghum: Sorghum → SEEDS/cereals
  ...
  other: Other → SEEDS/other

✓ Transformed 21 records

Merging records:
  Existing: 40
  SEEDS:    21
  Total:    61
```

---

## Results

### Before Merge

**Forms:** 38
- md19crops (standalone)
- md27inputCategory
- md27input
- ... (35 others)

**md27input data:**
```
FERTILIZER: 10 records
IRRIGATION: 10 records
LIVESTOCK_VET: 10 records
PESTICIDES: 10 records
SEEDS: 0 records  ← MISSING!
Total: 40 records
```

**md19crops data:**
```
21 crop records (separate table)
```

---

### After Merge

**Forms:** 37
- ~~md19crops~~ (removed)
- md27inputCategory
- md27input
- ... (35 others)

**md27input data:**
```
FERTILIZER: 10 records
IRRIGATION: 10 records
LIVESTOCK_VET: 10 records
PESTICIDES: 10 records
SEEDS: 21 records  ← ADDED!
Total: 61 records
```

**md19crops data:**
```
Merged into md27input
```

---

## Database Verification

```sql
-- Check record distribution
SELECT c_input_category, COUNT(*) as count
FROM app_fd_md27input
GROUP BY c_input_category
ORDER BY c_input_category;

-- Result:
-- FERTILIZER    | 10
-- IRRIGATION    | 10
-- LIVESTOCK_VET | 10
-- PESTICIDES    | 10
-- SEEDS         | 21  ✓
-- Total: 61 records
```

```sql
-- Sample SEEDS records
SELECT c_code, c_name, c_category
FROM app_fd_md27input
WHERE c_input_category = 'SEEDS'
LIMIT 5;

-- Result:
-- maize     | Maize          | cereals
-- sorghum   | Sorghum        | cereals
-- groundnuts| Groundnuts     | legumes
-- potatoes  | Potatoes       | tubers
-- tomato    | Tomato         | vegetables
```

---

## Files Changed

### Deleted
- ❌ `data/metadata/md19crops.csv` → Backed up to `md19crops.csv.backup`
- ❌ `data/metadata_forms/md19crops.json` → Moved to `.backups/md19crops.json.backup`

### Modified
- ✏️ `data/metadata/md27input.csv` - Added 21 SEEDS records (40 → 61 total)
  - Backup: `md27input.csv.backup`

### Created
- ✨ `merge_md19_to_md27.py` - Transformation script
- ✨ `MD19_MERGE_NOTES.md` - This document

---

## Impact on Joget Forms

### md27input SelectBox Behavior

Before merge, SEEDS category had no data:

```
md27input form → SelectBox(input_category)
  Options from md27inputCategory:
    - SEEDS (0 items) ← Empty!
    - FERTILIZER (10 items)
    - PESTICIDES (10 items)
    - ...
```

After merge, SEEDS category is populated:

```
md27input form → SelectBox(input_category)
  Options from md27inputCategory:
    - SEEDS (21 items) ✓
    - FERTILIZER (10 items)
    - PESTICIDES (10 items)
    - ...
```

---

## Future Considerations

### What if we need crop-specific fields?

**Option 1:** Add columns to md27input (current approach)
- Sparse columns acceptable in polymorphic table
- Example: `seed_variety`, `maturity_days`, `yield_per_ha`

**Option 2:** Create md27seeds as proper child form
- Parent: md27inputCategory (category-level)
- Child: md27seeds (item-level details)
- Still maintain md27input entry for each seed

**Recommendation:** Option 1 for now, migrate to Option 2 if crop data becomes complex

---

### What about the subcategory_source field?

**Current state:**
```csv
md27inputCategory:
SEEDS,Seeds,Yes,md19crops,kg,70
```

**Question:** Should we update `subcategory_source` to `md27input`?

**Answer:** No, leave as is. Explanation:
- `subcategory_source: md19crops` is **documentation** of data origin
- Indicates "SEEDS data comes from crop list (md19crops)"
- Joget doesn't use this field programmatically
- Changing it might confuse future developers

**Alternative:** Add comment field explaining that md19crops is now in md27input.

---

## Lessons Learned

### 1. Understand Parent-Child Relationships

**Incorrect interpretation:**
- "subcategory_source: md19crops" → create separate md19crops form

**Correct interpretation:**
- "subcategory_source: md19crops" → SEEDS items come from crop list
- But items still belong in polymorphic md27input table

### 2. Polymorphic Tables are Powerful

Single table with sparse columns is cleaner than many related tables for hierarchical data.

### 3. Test Form Definitions Before Deployment

The `input_category_code` field in md19crops.json was a red flag that should have been caught earlier.

### 4. Document Architecture Decisions

This document explains WHY md19crops was merged, not just WHAT changed.

---

## References

- **DEPLOYMENT_RESULTS.md** - Deployment test results
- **merge_md19_to_md27.py** - Transformation script
- **test_md27_full_deploy.py** - Verification test
- **verify_md27_seeds.py** - Database verification

---

**Document Version:** 1.0
**Last Updated:** October 27, 2025
**Author:** Development Team
