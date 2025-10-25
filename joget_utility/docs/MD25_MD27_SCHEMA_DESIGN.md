# MD25 & MD27 Schema Design - Unified Tables

## MD25 Equipment - Unified Schema Design

### Current State (WRONG): 9 Separate Tables

1. **md25generalTools** (10 items)
   - Columns: code, name, tool_category, estimated_cost_lsl, typical_quantity

2. **md25irrigationEquipment** (10 items)
   - Columns: code, name, irrigation_type, estimated_cost_lsl, area_coverage_ha

3. **md25livestockEquipment** (13 items)
   - Columns: code, name, equipment_type, estimated_cost_lsl, purpose

4. **md25pestControlEquipment** (8 items)
   - Columns: code, name, sprayer_type, capacity_litres, estimated_cost_lsl, power_source

5. **md25plantingEquipment** (8 items)
   - Columns: code, name, planting_type, estimated_cost_lsl, capacity

6. **md25processingEquipment** (9 items)
   - Columns: code, name, processing_type, capacity, estimated_cost_lsl, power_source

7. **md25storageEquipment** (10 items)
   - Columns: code, name, storage_type, capacity, estimated_cost_lsl, material

8. **md25tillageEquipment** (10 items)
   - Columns: code, name, power_source, estimated_cost_lsl, typical_lifespan_years, maintenance_level

9. **md25transportEquipment** (7 items)
   - Columns: code, name, transport_type, capacity, estimated_cost_lsl

### Target State (CORRECT): Single Equipment Table

**Form: md25equipment**
**Table: md25equipment**
**Total Records: 93 items**

### Unified Schema - Column Analysis

#### Common Columns (All Equipment Types)
- `code` - Unique equipment code (PK)
- `name` - Equipment name
- `estimated_cost_lsl` - Cost in Lesotho Loti (appears in all)

#### Foreign Key
- `equipment_category` - FK to md25equipmentCategory.code
  - Values: GENERAL_TOOLS, IRRIGATION, LIVESTOCK_EQUIP, PEST_CONTROL, PLANTING, PROCESSING, STORAGE, TILLAGE, TRANSPORT

#### Type-Specific Columns (Sparse - NULL for non-applicable types)

**Subcategory Columns** (different name per type):
- `tool_category` - Used by: GENERAL_TOOLS (Weeding, Digging, Cutting, etc.)
- `irrigation_type` - Used by: IRRIGATION (Pumping, Drip, Sprinkler, Manual)
- `equipment_type` - Used by: LIVESTOCK_EQUIP (Milking, Storage, Feeding, etc.)
- `sprayer_type` - Used by: PEST_CONTROL (Knapsack, Backpack, Boom, etc.)
- `planting_type` - Used by: PLANTING (Manual, Animal, Tractor, etc.)
- `processing_type` - Used by: PROCESSING (Shelling, Threshing, etc.)
- `storage_type` - Used by: STORAGE (Grain storage types)
- `transport_type` - Used by: TRANSPORT (Manual, Animal, Tractor)

**Measurement Columns**:
- `typical_quantity` - Used by: GENERAL_TOOLS (e.g., "2-5", "1-2")
- `area_coverage_ha` - Used by: IRRIGATION (e.g., "1-5 ha", "2-10 ha")
- `purpose` - Used by: LIVESTOCK_EQUIP (e.g., "Dairy", "Watering")
- `capacity_litres` - Used by: PEST_CONTROL (Sprayer capacity)
- `capacity` - Used by: PLANTING, PROCESSING, STORAGE, TRANSPORT (Generic capacity)

**Technical Specifications**:
- `power_source` - Used by: PEST_CONTROL, PROCESSING, TILLAGE (Manual, Petrol, Diesel, Tractor, etc.)
- `material` - Used by: STORAGE (Galvanized steel, Plastic, etc.)
- `typical_lifespan_years` - Used by: TILLAGE (Equipment lifespan)
- `maintenance_level` - Used by: TILLAGE (Low, Medium, High)

### Final Unified Schema (Column Order)

```csv
code,name,equipment_category,estimated_cost_lsl,tool_category,typical_quantity,irrigation_type,area_coverage_ha,equipment_type,purpose,sprayer_type,capacity_litres,planting_type,processing_type,storage_type,transport_type,capacity,power_source,material,typical_lifespan_years,maintenance_level
```

**Total Columns**: 21

### Category Mapping

| File | equipment_category Value | Record Count |
|------|-------------------------|--------------|
| md25generalTools.csv | GENERAL_TOOLS | 10 |
| md25irrigationEquipment.csv | IRRIGATION | 10 |
| md25livestockEquipment.csv | LIVESTOCK_EQUIP | 13 |
| md25pestControlEquipment.csv | PEST_CONTROL | 8 |
| md25plantingEquipment.csv | PLANTING | 8 |
| md25processingEquipment.csv | PROCESSING | 9 |
| md25storageEquipment.csv | STORAGE | 10 |
| md25tillageEquipment.csv | TILLAGE | 10 |
| md25transportEquipment.csv | TRANSPORT | 7 |
| **TOTAL** | | **93** |

---

## MD27 Input - Unified Schema Design

### Current State (WRONG): 4 Separate Tables

1. **md27fertilizer** (10 items)
   - Columns: code, name, category, default_unit, typical_quantity_per_ha, estimated_cost_per_unit

2. **md27pesticide** (10 items)
   - Columns: code, name, pesticide_type, default_unit, typical_quantity_per_ha, target, estimated_cost_per_unit

3. **md27irrigation** (10 items)
   - Columns: code, name, category, default_unit, typical_quantity, estimated_cost_per_unit

4. **md27livestockSupply** (10 items)
   - Columns: code, name, category, default_unit, typical_quantity, estimated_cost_per_unit

### Target State (CORRECT): Single Input Table

**Form: md27input**
**Table: md27input**
**Total Records: 40 items**

### Unified Schema - Column Analysis

#### Common Columns (All Input Types)
- `code` - Unique input code (PK)
- `name` - Input name
- `default_unit` - Unit of measurement (kg, litres, tonnes, doses, etc.)
- `estimated_cost_per_unit` - Cost per unit

#### Foreign Key
- `input_category` - FK to md27inputCategory.code
  - Values: FERTILIZER, PESTICIDES, IRRIGATION, LIVESTOCK_VET

#### Type-Specific Columns

**Subcategory Columns**:
- `category` - Used by: FERTILIZER, IRRIGATION, LIVESTOCK_VET (Generic subcategory)
- `pesticide_type` - Used by: PESTICIDES (Insecticide, Herbicide, Fungicide, Rodenticide)

**Measurement Columns**:
- `typical_quantity_per_ha` - Used by: FERTILIZER, PESTICIDES (e.g., "4-10 bags", "2-5 litres")
- `typical_quantity` - Used by: IRRIGATION, LIVESTOCK_VET (e.g., "50-500m", "10-50 doses")

**Additional Details**:
- `target` - Used by: PESTICIDES (Target pest/disease)

### Final Unified Schema (Column Order)

```csv
code,name,input_category,category,pesticide_type,default_unit,typical_quantity,typical_quantity_per_ha,target,estimated_cost_per_unit
```

**Total Columns**: 10

### Category Mapping

| File | input_category Value | Record Count |
|------|---------------------|--------------|
| md27fertilizer.csv | FERTILIZER | 10 |
| md27pesticide.csv | PESTICIDES | 10 |
| md27irrigation.csv | IRRIGATION | 10 |
| md27livestockSupply.csv | LIVESTOCK_VET | 10 |
| **TOTAL** | | **40** |

---

## Joget Form Implementation

### SelectBox with groupingColumn

**md25equipment Form:**
```json
{
  "className": "org.joget.apps.form.lib.SelectBox",
  "properties": {
    "id": "equipment_code",
    "label": "Equipment",
    "optionsBinder": {
      "className": "org.joget.apps.form.lib.FormOptionsBinder",
      "properties": {
        "formDefId": "md25equipment",
        "idColumn": "code",
        "labelColumn": "name",
        "groupingColumn": "equipment_category",
        "addEmptyOption": "true"
      }
    }
  }
}
```

**User Experience:**
1. User selects from md25equipmentCategory dropdown → "IRRIGATION"
2. Equipment dropdown auto-filters to show ONLY irrigation equipment (10 items)
3. User selects specific equipment → "WATER_PUMP_SOLAR"

### Table Name Validation

- md25equipment: 13 characters ✓ (under 20 limit)
- md27input: 9 characters ✓ (under 20 limit)

---

## Migration Notes

### Data Integrity Checks

**Before merge:**
- Verify no duplicate codes across child tables
- Check for NULL values in critical columns
- Validate category codes match parent table

**After merge:**
- Record count: 93 equipment items, 40 input items
- No orphaned category references
- All FK values exist in parent tables

### Rollback Plan

Original CSVs backed up to:
- `joget_utility/data/metadata/.archive/md25_original/`
- `joget_utility/data/metadata/.archive/md27_original/`

If merge fails, restore from archive and document issue.

---

**Generated**: 2025-10-25
**Status**: Schema Design Complete - Ready for Phase 2 (CSV Merge)
