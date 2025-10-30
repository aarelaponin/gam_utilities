# Archived Metadata Documentation

## metadata-overview.docx.backup-2025-10-27

**Original File:** `docs/metadata-overview.docx`
**Archived Date:** October 27, 2025
**File Size:** 48 KB
**Replaced By:** `docs/METADATA_MANUAL.md`

### Why Archived

The original `metadata-overview.docx` document was created before the implementation of the current metadata architecture and has become outdated.

**Key Issues:**
1. **Pre-dates Pattern 2 implementation** - Document was written before MD25/MD27 polymorphic table architecture
2. **Describes deprecated FK injection approach** - Referenced category-specific CSV files (md25tillageEquipment.csv, md27fertilizer.csv, etc.) that are no longer used
3. **Missing md19crops merge** - Does not reflect October 2025 architectural decision to merge crops data into md27input as SEEDS category
4. **Outdated form count** - References forms that have since been consolidated

### What Replaced It

**New comprehensive manual:** `docs/METADATA_MANUAL.md`

**Improvements in new manual:**
- ✅ Reflects current architecture (Pattern 2 with unified polymorphic CSVs)
- ✅ Documents all 37 MDM forms accurately
- ✅ Includes MD25 Equipment and MD27 Input hierarchies as implemented
- ✅ Clarifies deprecated CSV files
- ✅ Provides deployment guides, troubleshooting, and maintenance procedures
- ✅ 7,300+ lines of comprehensive documentation

### Current Implementation (October 2025)

**Pattern 1 - Simple Metadata:**
- 32 standalone lookup tables (md01-md37, excluding hierarchies)

**Pattern 2 - Traditional FK with Polymorphic Tables:**
- **MD25 Equipment:**
  - Parent: md25equipCategory (9 categories)
  - Child: md25equipment.csv (85 items, unified CSV with explicit equipment_category FK)
- **MD27 Input:**
  - Parent: md27inputCategory (8 categories)
  - Child: md27input.csv (61 items, unified CSV with explicit input_category FK)

**Deprecated (Not Deployed):**
- md25tillageEquipment.csv, md25plantingEquipment.csv, etc. → Replaced by unified md25equipment.csv
- md27fertilizer.csv, md27pesticide.csv, md27irrigation.csv, etc. → Replaced by unified md27input.csv
- md19crops.csv → Merged into md27input.csv as SEEDS category

### References

- **New Manual:** `docs/METADATA_MANUAL.md`
- **Architecture Decision:** `joget_utility/MD19_MERGE_NOTES.md`
- **Deployment Results:** `joget_utility/DEPLOYMENT_RESULTS.md`
- **relationships.json:** `joget_utility/data/relationships.json`
