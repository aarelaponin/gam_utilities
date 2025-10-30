# Master Data Management (MDM) - Comprehensive Developer & User Manual

**Version:** 2.0
**Last Updated:** October 27, 2025
**Platform:** Joget DX8 Enterprise Edition
**System:** Subsidy Application - Farmers Registry

---

## Document Purpose

This manual provides complete guidance for developers, administrators, and business users working with Master Data Management (MDM) in the Subsidy Application system. It replaces the outdated `metadata-overview.docx` and reflects the current implemented architecture.

**Target Audience:**
- 🧑‍💻 **Developers** - Creating new metadata, understanding patterns
- 👨‍💼 **Administrators** - Deploying and maintaining metadata
- 📊 **Business Users** - Understanding data structure and relationships
- 🔧 **Support Teams** - Troubleshooting and data quality

---

## Table of Contents

### [Part 1: Quick Reference](#part-1-quick-reference)
Essential commands and quick lookups for daily tasks
- [Quick Start Commands](#quick-start-commands)
- [Common Tasks Cheat Sheet](#common-tasks-cheat-sheet)
- [Metadata Overview Table](#metadata-overview-table-all-37-forms)

### [Part 2: Metadata Catalog](#part-2-metadata-catalog)
Complete listing of all 37 MDM forms with descriptions
- [Simple Metadata Forms (25 forms)](#21-simple-metadata-forms)
- [Parent-Child Hierarchies (2 groups)](#22-parent-child-hierarchies)

### [Part 3: Understanding Patterns](#part-3-understanding-patterns)
Two metadata patterns explained with examples
- [Pattern 1: Simple Metadata](#31-pattern-1-simple-metadata)
- [Pattern 2: Traditional Foreign Key (Polymorphic Tables)](#32-pattern-2-traditional-foreign-key-polymorphic-tables)
- [Polymorphic Table Pattern](#33-polymorphic-table-pattern)

### [Part 4: How to Add New Metadata](#part-4-how-to-add-new-metadata)
Step-by-step guides for creating metadata
- [Adding Simple Metadata](#41-adding-simple-metadata)
- [Adding Parent-Child Relationship (Pattern 2)](#42-adding-parent-child-relationship-pattern-2)
- [Form Generation Reference](#43-form-generation-reference)

### [Part 5: Deployment Guide](#part-5-deployment-guide)
Deploying metadata to environments
- [Deployment Scenarios](#51-deployment-scenarios)
- [Troubleshooting](#52-troubleshooting)
- [Environment-Specific Configuration](#53-environment-specific-configuration)

### [Part 6: Data Maintenance](#part-6-data-maintenance)
Maintaining data quality and integrity
- [Updating Existing Metadata](#61-updating-existing-metadata)
- [Adding Records to Polymorphic Tables](#62-adding-records-to-polymorphic-tables)
- [Data Quality Guidelines](#63-data-quality-guidelines)

### [Part 7: Reference](#part-7-reference)
Complete technical reference
- [All 37 MDM Forms Reference](#71-all-37-mdm-forms-reference)
- [Configuration Files](#72-configuration-files)
- [Database Schema](#73-database-schema)
- [Related Documentation](#74-related-documentation)

---

# Part 1: Quick Reference

## Quick Start Commands

### Deploy All Metadata (Full Deployment)
```bash
cd /Users/aarelaponin/PycharmProjects/dev/gam_utilities/joget_utility
python joget_utility.py --deploy-master-data --yes
```

**What it does:**
- Creates all 37 MDM forms in Joget
- Generates database tables (app_fd_md*)
- Creates API endpoints for each form
- Populates all forms with data from CSV files

**Expected result:**
- ✅ 37 forms created
- ✅ 416 records inserted across all forms
- ⏱️ ~2-3 minutes completion time

**When to use:**
- First-time deployment to new environment
- After dropping all MDM forms for clean reinstall
- After major schema changes

---

### Deploy Specific Parent-Child Hierarchy

**MD25 Equipment (Parent + Polymorphic Child):**
```bash
cd /Users/aarelaponin/PycharmProjects/dev/gam_utilities/joget_utility
python test_md25_full_deploy.py
```

**MD27 Input (Parent + Polymorphic Child):**
```bash
cd /Users/aarelaponin/PycharmProjects/dev/gam_utilities/joget_utility
python test_md27_full_deploy.py
```

**When to use:**
- Testing parent-child relationship changes
- Redeploying specific hierarchy after fixes
- Selective updates without full deployment

---

### Verify Deployment Success

**Check all MDM tables exist:**
```sql
-- Run in MySQL client
SELECT
    TABLE_NAME,
    TABLE_ROWS as 'Records'
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'jwdb'
AND TABLE_NAME LIKE 'app_fd_md%'
ORDER BY TABLE_NAME;
```

**Expected: 37 tables**

**Check specific form records:**
```sql
-- Simple form
SELECT COUNT(*) FROM app_fd_md01maritalStatus;  -- Expected: 5

-- Parent form
SELECT COUNT(*) FROM app_fd_md25equipCategory;  -- Expected: 9
SELECT COUNT(*) FROM app_fd_md27inputCategory;  -- Expected: 8

-- Polymorphic child forms
SELECT COUNT(*) FROM app_fd_md25equipment;      -- Expected: 85
SELECT COUNT(*) FROM app_fd_md27input;          -- Expected: 61

-- Verify category distribution in polymorphic tables
SELECT c_equipment_category, COUNT(*) as count
FROM app_fd_md25equipment
GROUP BY c_equipment_category
ORDER BY c_equipment_category;

SELECT c_input_category, COUNT(*) as count
FROM app_fd_md27input
GROUP BY c_input_category
ORDER BY c_input_category;
```

---

### Test Connection to Joget
```bash
cd /Users/aarelaponin/PycharmProjects/dev/gam_utilities/joget_utility
python joget_utility.py --test
```

---

### Dry Run (Preview Without Deploying)
```bash
python joget_utility.py --deploy-master-data --dry-run --yes
```

**What it does:**
- Validates all form definitions
- Validates all CSV data files
- Shows what would be deployed
- **Does NOT make any API calls or changes**

---

## Common Tasks Cheat Sheet

### Task: Add New Simple Metadata

**Example: Adding md38currency.csv**

1. **Create CSV file:**
   ```bash
   # Location: data/metadata/md38currency.csv
   code,name
   USD,US Dollar
   LSL,Lesotho Loti
   ZAR,South African Rand
   ```

2. **Auto-generate form definition:**
   ```bash
   cd /Users/aarelaponin/PycharmProjects/dev/gam_utilities/joget_utility
   python processors/form_generator.py data/metadata/md38currency.csv
   ```

   This creates: `data/metadata_forms/md38currency.json`

3. **Deploy:**
   ```bash
   python joget_utility.py --deploy-master-data --yes
   ```

4. **Verify:**
   ```sql
   SELECT * FROM app_fd_md38currency;
   ```

**Time:** ~5 minutes

---

### Task: Update Existing Metadata Records

**Example: Adding new marital status**

1. **Edit CSV file:**
   ```bash
   # Edit: data/metadata/md01maritalStatus.csv
   # Add new row: SEPARATED,Separated
   ```

2. **Redeploy (data only):**
   ```bash
   # Option A: Manual - delete existing records in Joget UI, then redeploy
   # Option B: Drop form and redeploy
   # Option C: Direct database insert (fastest)
   ```

3. **Direct database insert:**
   ```sql
   INSERT INTO app_fd_md01maritalStatus (c_code, c_name)
   VALUES ('SEPARATED', 'Separated');
   ```

**Time:** ~1 minute (database) or ~3 minutes (redeploy)

---

### Task: Troubleshoot Deployment Failure

**Quick fixes for common issues:**

| Issue | Quick Fix | Time |
|-------|-----------|------|
| ❌ API ID not found | Wait 5 seconds, retry deployment | 10s |
| ❌ Phantom validation error | Retry immediately (transient bug) | 30s |
| ❌ Form already exists | Drop form in Joget UI, redeploy | 2m |
| ❌ Connection refused | Check Joget server is running on port 8888 | 1m |
| ❌ Database error | Check .env.3 credentials, test connection | 2m |

**Detailed troubleshooting:** See [Part 5.2: Troubleshooting](#52-troubleshooting)

---

### Task: Check Parent-Child Relationships

**Verify MD25 Equipment Categories:**
```sql
-- Check parent categories
SELECT code, name FROM app_fd_md25equipCategory ORDER BY code;

-- Check child equipment by category
SELECT
    c_equipment_category as 'Category',
    COUNT(*) as 'Equipment Count'
FROM app_fd_md25equipment
GROUP BY c_equipment_category
ORDER BY c_equipment_category;

-- Expected distribution:
-- GENERAL_TOOLS: 9
-- IRRIGATION: 10
-- LIVESTOCK_EQUIP: 13
-- PEST_CONTROL: 8
-- PLANTING: 8
-- PROCESSING: 9
-- STORAGE: 10
-- TILLAGE: 10
-- TRANSPORT: 7
```

**Verify MD27 Input Categories:**
```sql
-- Check parent categories
SELECT code, name FROM app_fd_md27inputCategory ORDER BY code;

-- Check child inputs by category
SELECT
    c_input_category as 'Category',
    COUNT(*) as 'Input Count'
FROM app_fd_md27input
GROUP BY c_input_category
ORDER BY c_input_category;

-- Expected distribution:
-- FERTILIZER: 10
-- IRRIGATION: 10
-- LIVESTOCK_VET: 10
-- PESTICIDES: 10
-- SEEDS: 21 (merged from md19crops)
```

---

### Task: Test Cascading Dropdowns in Joget UI

1. **Open form in Joget:**
   - Navigate to Subsidy Application app
   - Find form that uses parent-child relationship
   - Example: Equipment selection form

2. **Test cascading:**
   - Select equipment category dropdown (e.g., "TILLAGE")
   - Equipment dropdown should filter to show only tillage equipment
   - Change category to "PLANTING"
   - Equipment dropdown should update to show only planting equipment

3. **Troubleshooting if cascading doesn't work:**
   - Check: Child form has SelectBox (not TextField) for parent reference
   - Check: Main form has `controlField` property set correctly
   - Check: Main form has `groupingColumn` property set correctly
   - See: [JOGET_NESTED_LOV_GUIDE.md](JOGET_NESTED_LOV_GUIDE.md)

---

## Metadata Overview Table (All 37 Forms)

### Legend
- 🟢 **Simple** - Standalone metadata (code/name structure)
- 🟡 **Parent** - Parent in parent-child relationship
- 🔵 **Child** - Child in parent-child relationship (references parent)
- 🔷 **Polymorphic** - Single table storing multiple categories

---

### Simple Metadata Forms (25 forms)

| Form ID | Name | Type | Records | Description |
|---------|------|------|---------|-------------|
| md01maritalStatus | Marital Status | 🟢 Simple | 5 | Marital status types: Single, Married, Divorced, Widowed, Other |
| md02language | Language | 🟢 Simple | 3 | Languages spoken: English, Sesotho, Other |
| md03district | District | 🟢 Simple | 10 | Administrative districts |
| md04agroEcologicalZone | Agro-Ecological Zone | 🟢 Simple | 4 | Climate zones for agriculture |
| md05residencyType | Residency Type | 🟢 Simple | 3 | Permanent, Temporary, Non-resident |
| md06farmLabourSource | Farm Labour Source | 🟢 Simple | 5 | Family, Hired, Community, Mixed, Other |
| md07livelihoodSource | Livelihood Source | 🟢 Simple | 4 | Primary income sources |
| md08educationLevel | Education Level | 🟢 Simple | 6 | None to Tertiary education |
| md09infoSource | Information Source | 🟢 Simple | 8 | How farmers get information |
| md10conservationPractice | Conservation Practice | 🟢 Simple | 12 | Soil/water conservation methods |
| md11hazard | Hazard | 🟢 Simple | 10 | Agricultural hazards/risks |
| md12relationship | Relationship | 🟢 Simple | 8 | Family relationship types |
| md13orphanhoodStatus | Orphanhood Status | 🟢 Simple | 5 | Child orphan status types |
| md14disabilityStatus | Disability Status | 🟢 Simple | 4 | Disability status types |
| md15areaUnits | Area Units | 🟢 Simple | 3 | Hectares, Acres, Square meters |
| md16livestockType | Livestock Type | 🟢 Simple | 18 | Cattle, Sheep, Goats, etc. |
| md17incomeSource | Income Source | 🟢 Simple | 10 | Sources of household income |
| md18registrationChannel | Registration Channel | 🟢 Simple | 5 | How farmers register |
| md20supportProgram | Support Program | 🟢 Simple | 9 | Government support programs |
| md21programType | Program Type | 🟢 Simple | 8 | Types of support programs |
| md22applicationStatus | Application Status | 🟢 Simple | 12 | Subsidy application statuses |
| md23documentType | Document Type | 🟢 Simple | 14 | Required document types |
| md24paymentMethod | Payment Method | 🟢 Simple | 6 | Cash, Bank Transfer, Mobile Money, etc. |
| md28benefitModel | Benefit Model | 🟢 Simple | 7 | Types of benefits offered |
| md30targetGroup | Target Group | 🟢 Simple | 10 | Beneficiary categories |
| md31decisionType | Decision Type | 🟢 Simple | 7 | Application decision types |
| md32rejectionReason | Rejection Reason | 🟢 Simple | 14 | Reasons for application rejection |
| md33requestType | Request Type | 🟢 Simple | 7 | Types of requests/applications |
| md34notificationType | Notification Type | 🟢 Simple | 13 | System notification types |
| md35foodSecurityStatus | Food Security Status | 🟢 Simple | 5 | Household food security levels |
| md36eligibilityOperator | Eligibility Operator | 🟢 Simple | 14 | Operators for eligibility rules |
| md37collectionPoint | Collection Point | 🟢 Simple | 10 | Distribution/collection locations |

**Total Simple Forms:** 32 forms, ~215 records

---

### Parent-Child Hierarchies (2 groups)

#### Hierarchy 1: MD25 Equipment

| Form ID | Name | Type | Records | Parent/Categories | Description |
|---------|------|------|---------|-------------------|-------------|
| md25equipCategory | Equipment Category | 🟡 Parent | 9 | — | Top-level equipment categories |
| md25equipment | Equipment | 🔵🔷 Child (Polymorphic) | 85 | md25equipCategory | All equipment types in single table |

**Categories in md25equipCategory:**
1. TILLAGE - Tillage Equipment (10 items)
2. PLANTING - Planting Equipment (8 items)
3. PEST_CONTROL - Pest Control Equipment (8 items)
4. IRRIGATION - Irrigation Equipment (10 items)
5. STORAGE - Storage Equipment (10 items)
6. PROCESSING - Processing Equipment (9 items)
7. TRANSPORT - Transport Equipment (7 items)
8. GENERAL_TOOLS - General Tools (9 items)
9. LIVESTOCK_EQUIP - Livestock Equipment (13 items)

**CSV Structure:**
- **Parent CSV:** `md25equipCategory.csv` (1 file, 9 categories)
- **Child CSVs:** 9 category-specific files:
  - `md25tillageEquipment.csv` (10 records)
  - `md25plantingEquipment.csv` (8 records)
  - `md25pestControlEquipment.csv` (8 records)
  - `md25irrigationEquipment.csv` (10 records)
  - `md25storageEquipment.csv` (10 records)
  - `md25processingEquipment.csv` (9 records)
  - `md25transportEquipment.csv` (7 records)
  - `md25generalTools.csv` (9 records)
  - `md25livestockEquipment.csv` (13 records)

**Joget Forms:** 2 forms
- `md25equipCategory.json` (parent)
- `md25equipment.json` (polymorphic child with SelectBox for equipment_category)

**Database Tables:** 2 tables
- `app_fd_md25equipCategory` (9 records)
- `app_fd_md25equipment` (85 records with c_equipment_category FK)

**Pattern:** Pattern 2 - Traditional Foreign Key with Polymorphic Table (see [Part 3.2](#32-pattern-2-traditional-foreign-key-polymorphic-tables))

**CSV Structure:** Uses **single unified CSV** (`md25equipment.csv`) with explicit `equipment_category` column. Individual category CSV files (md25tillageEquipment.csv, md25plantingEquipment.csv, etc.) are **deprecated** and not deployed.

---

#### Hierarchy 2: MD27 Input

| Form ID | Name | Type | Records | Parent/Categories | Description |
|---------|------|------|---------|-------------------|-------------|
| md27inputCategory | Input Category | 🟡 Parent | 8 | — | Agricultural input categories |
| md27input | Input | 🔵🔷 Child (Polymorphic) | 61 | md27inputCategory | All input types in single table |

**Categories in md27inputCategory:**
1. SEEDS - Seeds (21 items) - *Merged from md19crops*
2. FERTILIZER - Fertilizer (10 items)
3. PESTICIDES - Pesticides (10 items)
4. IRRIGATION - Irrigation (10 items)
5. LIVESTOCK_VET - Livestock & Veterinary (10 items)

**CSV Structure:**
- **Parent CSV:** `md27inputCategory.csv` (1 file, 8 categories including unused ones)
- **Child CSV:** `md27input.csv` (1 unified file, 61 records with explicit `input_category` column)
  - SEEDS: 21 records (merged from deprecated md19crops)
  - FERTILIZER: 10 records
  - PESTICIDES: 10 records
  - IRRIGATION: 10 records
  - LIVESTOCK_VET: 10 records

**Deprecated CSVs (NOT deployed):** Individual category CSV files (md27fertilizer.csv, md27pesticide.csv, md27irrigation.csv, md27livestockSupply.csv) are **deprecated** and replaced by unified `md27input.csv`.

**Joget Forms:** 2 forms
- `md27inputCategory.json` (parent)
- `md27input.json` (polymorphic child with SelectBox for input_category)

**Database Tables:** 2 tables
- `app_fd_md27inputCategory` (8 records)
- `app_fd_md27input` (61 records with c_input_category FK)

**Pattern:** Pattern 2 - Traditional Foreign Key with Polymorphic Table (see [Part 3.2](#32-pattern-2-traditional-foreign-key-polymorphic-tables))

**Special Note:** Seeds data was originally in separate `md19crops` form but was architecturally incorrect. It was merged into `md27input` as the SEEDS category on October 27, 2025. See [MD19_MERGE_NOTES.md](../joget_utility/MD19_MERGE_NOTES.md) for details.

---

### Summary Statistics

| Metric | Count |
|--------|-------|
| **Total Forms** | 37 |
| **Simple Forms** | 32 |
| **Parent Forms** | 2 |
| **Polymorphic Child Forms** | 2 |
| **Total Records** | 416 |
| **Parent-Child Hierarchies** | 2 |
| **Polymorphic Tables** | 2 |

---

### Quick Form Lookup by Number

```
md01: Marital Status          md20: Support Program         md31: Decision Type
md02: Language                md21: Program Type            md32: Rejection Reason
md03: District                md22: Application Status      md33: Request Type
md04: Agro-Ecological Zone    md23: Document Type           md34: Notification Type
md05: Residency Type          md24: Payment Method          md35: Food Security Status
md06: Farm Labour Source      md25: Equipment (Parent+Child) md36: Eligibility Operator
md07: Livelihood Source       md26: Training Topic          md37: Collection Point
md08: Education Level         md27: Input (Parent+Child)
md09: Info Source             md28: Benefit Model
md10: Conservation Practice   md30: Target Group
md11: Hazard
md12: Relationship
md13: Orphanhood Status
md14: Disability Status
md15: Area Units
md16: Livestock Type
md17: Income Source
md18: Registration Channel
md19: [REMOVED - merged into md27input as SEEDS]
```

---

**End of Part 1: Quick Reference**

**Next:** [Part 2: Metadata Catalog →](#part-2-metadata-catalog)

---

# Part 2: Metadata Catalog

This section provides detailed descriptions of all 37 MDM forms, their fields, relationships, and usage in the application.

## 2.1: Simple Metadata Forms

These 32 forms follow a simple structure with code/name pairs and optional additional fields. They serve as lookup tables throughout the application.

---

### md01maritalStatus - Marital Status

**Purpose:** Stores marital status types for farmer registration

**Database Table:** `app_fd_md01maritalStatus`

**Fields:**
- `code` (TextField, Mandatory) - Unique marital status code
- `name` (TextField) - Display name

**Sample Data:**
```
single      → Single
married     → Married
divorced    → Divorced
widowed     → Widowed
separated   → Separated
cohabiting  → Cohabiting
```

**Used In:**
- Farmer registration forms
- Household demographic information
- Beneficiary profiling

**Record Count:** 6

---

### md02language - Language

**Purpose:** Languages spoken by farmers

**Database Table:** `app_fd_md02language`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)

**Sample Data:**
```
en  → English
st  → Sesotho
zu  → Zulu
```

**Used In:**
- Farmer communication preferences
- Training material language selection
- SMS/notification language

**Record Count:** 3

---

### md03district - District

**Purpose:** Administrative districts within the region

**Database Table:** `app_fd_md03district`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)
- `region` (TextField) - Optional regional grouping

**Sample Data:**
```
MASERU   → Maseru District
MAFETENG → Mafeteng District
MOHALES  → Mohale's Hoek District
LERIBE   → Leribe District
...
```

**Used In:**
- Farmer location tracking
- Program distribution planning
- Geographic targeting
- Reporting and analytics

**Record Count:** 10

---

### md04agroEcologicalZone - Agro-Ecological Zone

**Purpose:** Climate/ecological zones for agricultural planning

**Database Table:** `app_fd_md04agroEcologicalZone`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)
- `description` (TextField)

**Sample Data:**
```
LOWLANDS  → Lowlands (below 1800m)
FOOTHILLS → Foothills (1800-2200m)
MOUNTAINS → Mountains (above 2200m)
SENQU     → Senqu River Valley
```

**Used In:**
- Crop suitability assessment
- Subsidy program targeting
- Climate adaptation planning

**Record Count:** 4

---

### md05residencyType - Residency Type

**Purpose:** Farmer residency status

**Database Table:** `app_fd_md05residencyType`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)

**Sample Data:**
```
PERMANENT  → Permanent Resident
TEMPORARY  → Temporary Resident
NON_RES    → Non-Resident
```

**Used In:**
- Eligibility verification
- Program participation rules

**Record Count:** 3

---

### md06farmLabourSource - Farm Labour Source

**Purpose:** Primary source of farm labor

**Database Table:** `app_fd_md06farmLabourSource`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)

**Sample Data:**
```
FAMILY    → Family Labour
HIRED     → Hired Labour
COMMUNITY → Community Labour Exchange
MIXED     → Mixed Sources
OTHER     → Other
```

**Used In:**
- Farm production capacity assessment
- Labour support program targeting

**Record Count:** 5

---

### md07livelihoodSource - Livelihood Source

**Purpose:** Primary household income sources

**Database Table:** `app_fd_md07livelihoodSource`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)

**Sample Data:**
```
FARMING     → Farming
LIVESTOCK   → Livestock
TRADING     → Trading/Business
EMPLOYMENT  → Formal Employment
```

**Used In:**
- Household economic profiling
- Poverty assessment
- Diversification program targeting

**Record Count:** 4

---

### md08educationLevel - Education Level

**Purpose:** Highest education level attained

**Database Table:** `app_fd_md08educationLevel`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)

**Sample Data:**
```
NONE       → No Formal Education
PRIMARY    → Primary Education
SECONDARY  → Secondary Education
TERTIARY   → Tertiary Education
VOCATIONAL → Vocational Training
LITERATE   → Informal/Adult Literacy
```

**Used In:**
- Training program design
- Literacy requirements for programs
- Farmer profiling

**Record Count:** 6

---

### md09infoSource - Information Source

**Purpose:** How farmers access agricultural information

**Database Table:** `app_fd_md09infoSource`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)

**Sample Data:**
```
RADIO          → Radio
EXTENSION      → Extension Officer
FARMER_GROUP   → Farmer Groups
MOBILE_PHONE   → Mobile Phone/SMS
TV             → Television
SOCIAL_MEDIA   → Social Media
PRINT          → Print Media
WORD_OF_MOUTH  → Word of Mouth
```

**Used In:**
- Communication strategy planning
- Program awareness campaigns
- Extension service optimization

**Record Count:** 8

---

### md10conservationPractice - Conservation Practice

**Purpose:** Soil and water conservation methods

**Database Table:** `app_fd_md10conservationPractice`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)
- `description` (TextField)

**Sample Data:**
```
CONTOUR_PLOUGH → Contour Ploughing
TERRACING      → Terracing
MULCHING       → Mulching
CROP_ROTATION  → Crop Rotation
COVER_CROPS    → Cover Cropping
...
```

**Used In:**
- Sustainable farming program tracking
- Conservation subsidy eligibility
- Environmental monitoring

**Record Count:** 12

---

### md11hazard - Hazard

**Purpose:** Agricultural hazards and risks

**Database Table:** `app_fd_md11hazard`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)
- `category` (TextField) - e.g., weather, pest, market

**Sample Data:**
```
DROUGHT    → Drought
FLOOD      → Flooding
HAIL       → Hail Damage
FROST      → Frost
PEST_OUT   → Pest Outbreak
DISEASE    → Crop Disease
THEFT      → Livestock Theft
FIRE       → Fire
...
```

**Used In:**
- Risk assessment
- Insurance claim processing
- Emergency response planning

**Record Count:** 10

---

### md12relationship - Relationship

**Purpose:** Family relationship types for household members

**Database Table:** `app_fd_md12relationship`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)

**Sample Data:**
```
HEAD    → Household Head
SPOUSE  → Spouse
CHILD   → Child
PARENT  → Parent
SIBLING → Sibling
GRANDCH → Grandchild
OTHER   → Other Relative
UNREL   → Unrelated
```

**Used In:**
- Household composition tracking
- Beneficiary verification
- Family farming unit definition

**Record Count:** 8

---

### md13orphanhoodStatus - Orphanhood Status

**Purpose:** Child orphan status for vulnerability assessment

**Database Table:** `app_fd_md13orphanhoodStatus`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)

**Sample Data:**
```
NOT_ORPHAN  → Not an Orphan
SINGLE_M    → Single Orphan (Mother Deceased)
SINGLE_F    → Single Orphan (Father Deceased)
DOUBLE      → Double Orphan
ABANDONED   → Abandoned
```

**Used In:**
- Vulnerable household identification
- Social protection program targeting

**Record Count:** 5

---

### md14disabilityStatus - Disability Status

**Purpose:** Disability status for accessibility and support planning

**Database Table:** `app_fd_md14disabilityStatus`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)

**Sample Data:**
```
NONE       → No Disability
PHYSICAL   → Physical Disability
VISUAL     → Visual Impairment
HEARING    → Hearing Impairment
```

**Used In:**
- Accessibility requirements
- Special support program eligibility
- Inclusive program design

**Record Count:** 4

---

### md15areaUnits - Area Units

**Purpose:** Units of measurement for farm land

**Database Table:** `app_fd_md15areaUnits`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)

**Sample Data:**
```
HA  → Hectares
AC  → Acres
SQM → Square Meters
```

**Used In:**
- Farm size recording
- Input quantity calculations
- Area-based subsidy allocation

**Record Count:** 3

---

### md16livestockType - Livestock Type

**Purpose:** Types of livestock kept by farmers

**Database Table:** `app_fd_md16livestockType`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)
- `category` (TextField) - large_livestock, small_livestock, poultry

**Sample Data:**
```
cattle-beef      → Cattle (Beef) [large_livestock]
cattle-dairy     → Cattle (Dairy) [large_livestock]
sheep            → Sheep [small_livestock]
goat             → Goats [small_livestock]
chicken-broiler  → Chicken (Broiler) [poultry]
chicken-layer    → Chicken (Layer) [poultry]
chicken-village  → Chicken (Village) [poultry]
pig              → Pigs [small_livestock]
donkey           → Donkeys [large_livestock]
horse            → Horses [large_livestock]
...
```

**Used In:**
- Livestock inventory
- Veterinary service planning
- Livestock support programs

**Record Count:** 18

---

### md17incomeSource - Income Source

**Purpose:** Household income sources for economic profiling

**Database Table:** `app_fd_md17incomeSource`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)

**Sample Data:**
```
CROP_SALES      → Crop Sales
LIVESTOCK_SALES → Livestock Sales
CASUAL_LABOUR   → Casual Labour
REMITTANCES     → Remittances
BUSINESS        → Small Business
PENSION         → Pension/Social Grant
...
```

**Used In:**
- Economic vulnerability assessment
- Livelihood diversification planning

**Record Count:** 10

---

### md18registrationChannel - Registration Channel

**Purpose:** How farmers register in the system

**Database Table:** `app_fd_md18registrationChannel`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)

**Sample Data:**
```
ONLINE      → Online Portal
MOBILE_APP  → Mobile Application
OFFICE      → Government Office
AGENT       → Field Agent
USSD        → USSD/Mobile Code
```

**Used In:**
- Registration process tracking
- Channel effectiveness analysis

**Record Count:** 5

---

### md20supportProgram - Support Program

**Purpose:** Government agricultural support programs

**Database Table:** `app_fd_md20supportProgram`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)

**Sample Data:**
```
INPUT_SUB    → Input Subsidy Program
EQUIP_SUB    → Equipment Subsidy
IRRIGATION   → Irrigation Support
TRAINING     → Agricultural Training
EXTENSION    → Extension Services
LIVESTOCK    → Livestock Development
CREDIT       → Agricultural Credit
INSURANCE    → Crop Insurance
MARKETING    → Market Access Support
```

**Used In:**
- Program enrollment
- Benefit allocation
- Program effectiveness tracking

**Record Count:** 9

---

### md21programType - Program Type

**Purpose:** Categories of support programs

**Database Table:** `app_fd_md21programType`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)

**Sample Data:**
```
SUBSIDY     → Subsidy/Grant
LOAN        → Loan/Credit
TRAINING    → Training/Capacity Building
INSURANCE   → Insurance
TECH_ASSIST → Technical Assistance
MARKET      → Market Linkage
INFRA       → Infrastructure
RESEARCH    → Research & Development
```

**Used In:**
- Program classification
- Budget allocation
- Reporting

**Record Count:** 8

---

### md22applicationStatus - Application Status

**Purpose:** Status of subsidy applications throughout workflow

**Database Table:** `app_fd_md22applicationStatus`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)
- `is_final` (TextField) - yes/no
- `is_approved` (TextField) - yes/no

**Sample Data:**
```
DRAFT          → Draft [not final]
SUBMITTED      → Submitted [not final]
UNDER_REVIEW   → Under Review [not final]
VERIFIED       → Verified [not final]
APPROVED       → Approved [final, approved]
REJECTED       → Rejected [final, not approved]
WITHDRAWN      → Withdrawn [final, not approved]
PENDING_INFO   → Pending Additional Information [not final]
APPEALED       → Appealed [not final]
APPEAL_ACCEPT  → Appeal Accepted [final, approved]
APPEAL_REJECT  → Appeal Rejected [final, not approved]
CANCELLED      → Cancelled [final, not approved]
```

**Used In:**
- Application workflow management
- Status tracking and reporting
- Notification triggers

**Record Count:** 12

---

### md23documentType - Document Type

**Purpose:** Required document types for verification

**Database Table:** `app_fd_md23documentType`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)
- `category` (TextField) - identity, land, financial, etc.

**Sample Data:**
```
NATIONAL_ID    → National ID Card [identity]
PASSPORT       → Passport [identity]
LAND_TITLE     → Land Title/Deed [land]
LEASE_AGREE    → Lease Agreement [land]
BANK_STMT      → Bank Statement [financial]
TAX_CERT       → Tax Clearance Certificate [financial]
FARM_MAP       → Farm Map/Survey [land]
...
```

**Used In:**
- Document verification checklist
- KYC/KYF requirements
- Compliance tracking

**Record Count:** 14

---

### md24paymentMethod - Payment Method

**Purpose:** Payment methods for subsidy disbursement

**Database Table:** `app_fd_md24paymentMethod`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)

**Sample Data:**
```
BANK_TRANSFER  → Bank Transfer
MOBILE_MONEY   → Mobile Money
CASH           → Cash Payment
CHEQUE         → Cheque
VOUCHER        → Voucher/Coupon
IN_KIND        → In-Kind (Direct Input)
```

**Used In:**
- Payment processing
- Disbursement tracking
- Farmer payment preferences

**Record Count:** 6

---

### md26trainingTopic - Training Topic

**Purpose:** Agricultural training topics available

**Database Table:** `app_fd_md26trainingTopic`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)
- `category` (TextField)
- `duration_days` (TextField)
- `prerequisites` (TextField)
- `target_group` (TextField)

**Sample Data:**
```
CONSERVATION_AGRIC → Conservation Agriculture [Sustainable Farming, 5 days]
PEST_MANAGEMENT    → Integrated Pest Management [Crop Protection, 3 days]
SOIL_MANAGEMENT    → Soil Health Management [Soil Science, 4 days]
IRRIGATION_TECH    → Irrigation Techniques [Water Management, 3 days]
POST_HARVEST       → Post-Harvest Handling [Value Chain, 2 days]
...
```

**Used In:**
- Training program scheduling
- Farmer capacity building
- Extension service planning

**Record Count:** 12

---

### md28benefitModel - Benefit Model

**Purpose:** Types of benefits offered in programs

**Database Table:** `app_fd_md28benefitModel`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)

**Sample Data:**
```
CASH           → Cash Transfer
VOUCHER        → Input Voucher
DIRECT_INPUT   → Direct Input Distribution
SERVICE        → Service Provision
EQUIPMENT      → Equipment Supply
TRAINING       → Training/Education
INFRASTRUCTURE → Infrastructure Development
```

**Used In:**
- Program benefit design
- Distribution planning
- Budget allocation

**Record Count:** 7

---

### md30targetGroup - Target Group

**Purpose:** Beneficiary target groups for program eligibility

**Database Table:** `app_fd_md30targetGroup`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)

**Sample Data:**
```
SMALLHOLDER   → Smallholder Farmers
WOMEN         → Women Farmers
YOUTH         → Youth (18-35)
VULNERABLE    → Vulnerable Households
COMMERCIAL    → Commercial Farmers
COOPERATIVES  → Farmer Cooperatives
DISABLED      → Persons with Disabilities
ELDERLY       → Elderly Farmers
ALL           → All Farmers
REFUGEE       → Refugee Farmers
```

**Used In:**
- Program eligibility rules
- Targeting and outreach
- Equity monitoring

**Record Count:** 10

---

### md31decisionType - Decision Type

**Purpose:** Types of decisions in application workflow

**Database Table:** `app_fd_md31decisionType`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)

**Sample Data:**
```
APPROVE        → Approve
REJECT         → Reject
DEFER          → Defer
REQUEST_INFO   → Request More Information
ESCALATE       → Escalate to Supervisor
APPEAL_GRANT   → Grant Appeal
APPEAL_DENY    → Deny Appeal
```

**Used In:**
- Workflow decision tracking
- Approval process management

**Record Count:** 7

---

### md32rejectionReason - Rejection Reason

**Purpose:** Reasons for application rejection

**Database Table:** `app_fd_md32rejectionReason`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)

**Sample Data:**
```
INELIGIBLE       → Applicant Ineligible
INCOMPLETE_DOCS  → Incomplete Documentation
DUPLICATE        → Duplicate Application
INSUFFICIENT_FDS → Insufficient Funds
FALSE_INFO       → False Information
MISSED_DEADLINE  → Missed Deadline
NO_LAND_RIGHTS   → No Land Rights
ALREADY_BENEFIT  → Already Receiving Benefits
...
```

**Used In:**
- Rejection notification
- Appeal processing
- Program improvement feedback

**Record Count:** 14

---

### md33requestType - Request Type

**Purpose:** Types of requests farmers can make

**Database Table:** `app_fd_md33requestType`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)

**Sample Data:**
```
NEW_APP       → New Application
AMENDMENT     → Amendment Request
APPEAL        → Appeal
WITHDRAWAL    → Withdrawal Request
INFO_REQUEST  → Information Request
COMPLAINT     → Complaint
STATUS_CHECK  → Status Check
```

**Used In:**
- Request routing and tracking
- Service desk management

**Record Count:** 7

---

### md34notificationType - Notification Type

**Purpose:** System notification types

**Database Table:** `app_fd_md34notificationType`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)
- `channel` (TextField) - sms, email, portal

**Sample Data:**
```
APP_RECEIVED    → Application Received [sms, email, portal]
APP_APPROVED    → Application Approved [sms, email, portal]
APP_REJECTED    → Application Rejected [sms, email, portal]
DOC_REQUIRED    → Documents Required [sms, email, portal]
PAYMENT_MADE    → Payment Made [sms, email, portal]
DEADLINE_NEAR   → Deadline Approaching [sms, email]
TRAINING_INVITE → Training Invitation [sms, portal]
...
```

**Used In:**
- Notification engine configuration
- Communication management

**Record Count:** 13

---

### md35foodSecurityStatus - Food Security Status

**Purpose:** Household food security assessment levels

**Database Table:** `app_fd_md35foodSecurityStatus`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)

**Sample Data:**
```
SECURE       → Food Secure
MILD_INSEC   → Mildly Food Insecure
MODERATE_IN  → Moderately Food Insecure
SEVERE_INSEC → Severely Food Insecure
CRISIS       → Food Crisis
```

**Used In:**
- Vulnerability assessment
- Emergency response targeting
- Food assistance programs

**Record Count:** 5

---

### md36eligibilityOperator - Eligibility Operator

**Purpose:** Operators for building eligibility rules

**Database Table:** `app_fd_md36eligibilityOperator`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)
- `operator_type` (TextField) - comparison, logical

**Sample Data:**
```
EQ          → Equals [comparison]
NE          → Not Equals [comparison]
GT          → Greater Than [comparison]
LT          → Less Than [comparison]
GTE         → Greater Than or Equal [comparison]
LTE         → Less Than or Equal [comparison]
AND         → AND [logical]
OR          → OR [logical]
NOT         → NOT [logical]
IN          → In List [comparison]
NOT_IN      → Not In List [comparison]
BETWEEN     → Between [comparison]
CONTAINS    → Contains [comparison]
STARTS_WITH → Starts With [comparison]
```

**Used In:**
- Eligibility rule engine
- Dynamic program criteria
- Automated eligibility checking

**Record Count:** 14

---

### md37collectionPoint - Collection Point

**Purpose:** Physical locations for input collection/distribution

**Database Table:** `app_fd_md37collectionPoint`

**Fields:**
- `code` (TextField, Mandatory)
- `name` (TextField)
- `district` (TextField)
- `gps_coordinates` (TextField)

**Sample Data:**
```
MASERU_DEPOT   → Maseru Central Depot [Maseru, -29.3167,27.4833]
MAFETENG_COOP  → Mafeteng Cooperative [Mafeteng, -29.8167,27.2333]
LERIBE_CENTER  → Leribe Agricultural Center [Leribe, -28.8667,28.0500]
...
```

**Used In:**
- Distribution logistics
- Farmer collection scheduling
- Geographic access planning

**Record Count:** 10

---

## 2.2: Parent-Child Hierarchies

The system implements two sophisticated parent-child metadata hierarchies using **Pattern 2: Traditional Foreign Key with Polymorphic Table** and **Polymorphic Table Pattern**.

---

### Hierarchy 1: MD25 Equipment Category & Equipment

#### Overview

**Pattern:** Pattern 2 (Traditional FK + Polymorphic) + Polymorphic Table
**Purpose:** Manage agricultural equipment catalog with category-based organization
**Forms:** 2 (parent + polymorphic child)
**CSV Files:** 10 (1 parent + 9 category-specific)
**Total Records:** 94 (9 categories + 85 equipment items)

---

#### Architecture Diagram

```
┌─────────────────────────────────────────────┐
│     md25equipCategory (PARENT)              │
│     Table: app_fd_md25equipCategory         │
├─────────────────────────────────────────────┤
│ code              | name                    │
├───────────────────┼─────────────────────────┤
│ TILLAGE           | Tillage Equipment       │  ───┐
│ PLANTING          | Planting Equipment      │  ───┤
│ PEST_CONTROL      | Pest Control Equipment  │  ───┤
│ IRRIGATION        | Irrigation Equipment    │  ───┤
│ STORAGE           | Storage Equipment       │  ───┤
│ PROCESSING        | Processing Equipment    │  ───┤
│ TRANSPORT         | Transport Equipment     │  ───┤
│ GENERAL_TOOLS     | General Tools           │  ───┤
│ LIVESTOCK_EQUIP   | Livestock Equipment     │  ───┤
└─────────────────────────────────────────────┘     │
                                                     │ FK injected by
                                                     │ DataAugmentor
                                                     │ during CSV read
                                                     ↓
┌─────────────────────────────────────────────────────────────────┐
│     md25equipment (POLYMORPHIC CHILD)                           │
│     Table: app_fd_md25equipment                                 │
├─────────────────────────────────────────────────────────────────┤
│ code         | name              | equipment_category | ... │
├──────────────┼───────────────────┼────────────────────┼─────┤
│ HAND_HOE     | Hand Hoe          | GENERAL_TOOLS      | ... │ ← Injected FK
│ PLOUGH       | Ox-Drawn Plough   | TILLAGE            | ... │ ← Injected FK
│ SPRAYER      | Knapsack Sprayer  | PEST_CONTROL       | ... │ ← Injected FK
│ DRIP_SYSTEM  | Drip Irrigation   | IRRIGATION         | ... │ ← Injected FK
│ ...          | ...               | ...                | ... │
└─────────────────────────────────────────────────────────────────┘
                        85 equipment items across 9 categories
```

---

#### Parent Form: md25equipCategory

**Database Table:** `app_fd_md25equipCategory`

**Fields:**
- `code` (TextField, Mandatory, Unique) - Category code
- `name` (TextField) - Category display name

**CSV File:** `data/metadata/md25equipCategory.csv` (9 records)

**Sample Data:**
```csv
code,name
TILLAGE,Tillage Equipment
PLANTING,Planting Equipment
PEST_CONTROL,Pest Control Equipment
IRRIGATION,Irrigation Equipment
STORAGE,Storage Equipment
PROCESSING,Processing Equipment
TRANSPORT,Transport Equipment
GENERAL_TOOLS,General Tools
LIVESTOCK_EQUIP,Livestock Equipment
```

**Form Definition:** `data/metadata_forms/md25equipCategory.json`

---

#### Polymorphic Child Form: md25equipment

**Database Table:** `app_fd_md25equipment`

**Fields:**
- `code` (TextField, Mandatory, Unique) - Equipment code
- `name` (TextField, Mandatory) - Equipment name
- `equipment_category` **(SelectBox, Mandatory)** - References md25equipCategory
- `estimated_cost_lsl` (TextField) - Estimated cost in Lesotho Loti
- `tool_category` (TextField) - For GENERAL_TOOLS subcategorization
- `typical_quantity` (TextField) - Typical quantity per farm
- `irrigation_type` (TextField) - For IRRIGATION equipment
- `area_coverage_ha` (TextField) - Area coverage in hectares
- `equipment_type` (TextField) - Generic type field
- `purpose` (TextField) - Equipment purpose
- `sprayer_type` (TextField) - For PEST_CONTROL equipment
- `capacity_litres` (TextField) - For liquid containers
- `planting_type` (TextField) - For PLANTING equipment
- `processing_type` (TextField) - For PROCESSING equipment
- `storage_type` (TextField) - For STORAGE equipment
- `transport_type` (TextField) - For TRANSPORT equipment
- `capacity` (TextField) - Generic capacity
- `power_source` (TextField) - Manual, animal, tractor, electric
- `material` (TextField) - Construction material
- `typical_lifespan_years` (TextField) - Expected lifespan
- `maintenance_level` (TextField) - Low, medium, high

**CSV Files:** 9 category-specific files (85 total records)

**CRITICAL:** CSV files do NOT contain `equipment_category` column. This is injected by DataAugmentor based on filename mapping in `config/relationships.json`.

---

#### CSV to Category Mapping

| CSV File | Category Code | Records | Description |
|----------|---------------|---------|-------------|
| `md25tillageEquipment.csv` | TILLAGE | 10 | Ploughs, harrows, cultivators |
| `md25plantingEquipment.csv` | PLANTING | 8 | Seeders, transplanters |
| `md25pestControlEquipment.csv` | PEST_CONTROL | 8 | Sprayers, dusters |
| `md25irrigationEquipment.csv` | IRRIGATION | 10 | Pipes, pumps, drip systems |
| `md25storageEquipment.csv` | STORAGE | 10 | Silos, bins, warehouses |
| `md25processingEquipment.csv` | PROCESSING | 9 | Mills, threshers, dryers |
| `md25transportEquipment.csv` | TRANSPORT | 7 | Carts, wheelbarrows, trucks |
| `md25generalTools.csv` | GENERAL_TOOLS | 9 | Hand tools, basic equipment |
| `md25livestockEquipment.csv` | LIVESTOCK_EQUIP | 13 | Feeding, housing, handling |

**Total Equipment:** 85 items

---

#### Sample Equipment Records

**From GENERAL_TOOLS category (md25generalTools.csv):**
```csv
code,name,estimated_cost_lsl,tool_category,typical_quantity
HAND_HOE,Hand Hoe,250,Weeding,2-5
SPADE,Spade,300,Digging,2-3
RAKE,Rake,200,Leveling,2-3
MACHETE,Machete/Slasher,180,Cutting,2-4
WATERING_CAN,Watering Can,250,Irrigation,2-5
```

**After FK Injection (in database):**
```
code: HAND_HOE
name: Hand Hoe
equipment_category: GENERAL_TOOLS  ← Injected by DataAugmentor
estimated_cost_lsl: 250
tool_category: Weeding
typical_quantity: 2-5
(all other category-specific fields: empty/null)
```

**From TILLAGE category (md25tillageEquipment.csv):**
```csv
code,name,estimated_cost_lsl,power_source,typical_lifespan_years
PLOUGH_ANIMAL,Animal-Drawn Plough,3500,animal,10-15
PLOUGH_TRACTOR,Tractor Plough (3-disc),25000,tractor,15-20
HARROW,Disc Harrow,18000,tractor,10-15
```

**After FK Injection:**
```
code: PLOUGH_ANIMAL
name: Animal-Drawn Plough
equipment_category: TILLAGE  ← Injected
estimated_cost_lsl: 3500
power_source: animal
typical_lifespan_years: 10-15
(tool_category, irrigation_type, etc.: empty/null)
```

---

#### Polymorphic Table Structure

The `md25equipment` table uses **sparse columns** - each record only populates fields relevant to its category:

| Field | GENERAL_TOOLS | TILLAGE | PEST_CONTROL | IRRIGATION |
|-------|---------------|---------|--------------|------------|
| code | ✓ | ✓ | ✓ | ✓ |
| name | ✓ | ✓ | ✓ | ✓ |
| equipment_category | ✓ | ✓ | ✓ | ✓ |
| tool_category | ✓ | — | — | — |
| power_source | — | ✓ | — | — |
| sprayer_type | — | — | ✓ | — |
| irrigation_type | — | — | — | ✓ |
| estimated_cost_lsl | ✓ | ✓ | ✓ | ✓ |

*Where ✓ = used, — = typically null*

---

#### Configuration (config/relationships.json)

```json
{
  "parent_child_relationships": {
    "md25equipCategory": {
      "child_forms": [
        {
          "form_id": "md25equipment",
          "relationship_type": "polymorphic_table",
          "parent_fk_field": "equipment_category",
          "category_mappings": {
            "TILLAGE": "md25tillageEquipment.csv",
            "PLANTING": "md25plantingEquipment.csv",
            "PEST_CONTROL": "md25pestControlEquipment.csv",
            "IRRIGATION": "md25irrigationEquipment.csv",
            "STORAGE": "md25storageEquipment.csv",
            "PROCESSING": "md25processingEquipment.csv",
            "TRANSPORT": "md25transportEquipment.csv",
            "GENERAL_TOOLS": "md25generalTools.csv",
            "LIVESTOCK_EQUIP": "md25livestockEquipment.csv"
          }
        }
      ]
    }
  }
}
```

---

#### Usage in Application Forms

When creating application forms that need equipment selection, use cascading dropdowns:

**Main Form Configuration:**
```json
{
  "elements": [
    {
      "id": "equipment_category",
      "className": "org.joget.apps.form.lib.SelectBox",
      "optionsBinder": {
        "formDefId": "md25equipCategory",
        "idColumn": "code",
        "labelColumn": "name"
      }
    },
    {
      "id": "equipment",
      "className": "org.joget.apps.form.lib.SelectBox",
      "optionsBinder": {
        "formDefId": "md25equipment",
        "idColumn": "code",
        "labelColumn": "name",
        "groupingColumn": "equipment_category",
        "useAjax": "true"
      },
      "controlField": "equipment_category"
    }
  ]
}
```

**Behavior:**
1. User selects "TILLAGE" in equipment_category dropdown
2. Equipment dropdown automatically filters to show only tillage equipment
3. User sees: Plough, Harrow, Cultivator, etc. (only TILLAGE items)

---

### Hierarchy 2: MD27 Input Category & Input

#### Overview

**Pattern:** Pattern 2 (Traditional FK + Polymorphic) + Polymorphic Table
**Purpose:** Manage agricultural inputs catalog with category-based organization
**Forms:** 2 (parent + polymorphic child)
**CSV Files:** 6 (1 parent + 5 category-specific)
**Total Records:** 69 (8 categories + 61 input items)

**Special Note:** Includes 21 SEEDS records merged from md19crops (see [MD19_MERGE_NOTES.md](../joget_utility/MD19_MERGE_NOTES.md))

---

#### Architecture Diagram

```
┌─────────────────────────────────────────────┐
│     md27inputCategory (PARENT)              │
│     Table: app_fd_md27inputCategory         │
├─────────────────────────────────────────────┤
│ code              | name                    │
├───────────────────┼─────────────────────────┤
│ SEEDS             | Seeds                   │  ───┐
│ FERTILIZER        | Fertilizer              │  ───┤
│ PESTICIDES        | Pesticides              │  ───┤
│ IRRIGATION        | Irrigation              │  ───┤ FK injected by
│ LIVESTOCK_VET     | Livestock & Veterinary  │  ───┤ DataAugmentor
│ ...               | ...                     │  ───┤
└─────────────────────────────────────────────┘     │
                                                     ↓
┌─────────────────────────────────────────────────────────────────┐
│     md27input (POLYMORPHIC CHILD)                               │
│     Table: app_fd_md27input                                     │
├─────────────────────────────────────────────────────────────────┤
│ code      | name          | input_category | category    | ... │
├───────────┼───────────────┼────────────────┼─────────────┼─────┤
│ maize     | Maize         | SEEDS          | cereals     | ... │ ← Merged from md19crops
│ NPK       | NPK Fert      | FERTILIZER     | Compound    | ... │ ← From md27fertilizer.csv
│ INSECT_G  | Insecticide   | PESTICIDES     |             | ... │ ← From md27pesticide.csv
│ DRIP_TAPE | Drip Tape     | IRRIGATION     | Drip System | ... │ ← From md27irrigation.csv
│ ...       | ...           | ...            | ...         | ... │
└─────────────────────────────────────────────────────────────────┘
                        61 input items across 5 categories
```

---

#### Parent Form: md27inputCategory

**Database Table:** `app_fd_md27inputCategory`

**Fields:**
- `code` (TextField, Mandatory, Unique)
- `name` (TextField)
- `has_subcategory` (TextField) - Yes/No
- `subcategory_source` (TextField) - Historical reference (now unused)
- `default_unit` (TextField)
- `typical_subsidy_percent` (TextField)

**CSV File:** `data/metadata/md27inputCategory.csv` (8 records)

**Sample Data:**
```csv
code,name,has_subcategory,subcategory_source,default_unit,typical_subsidy_percent
SEEDS,Seeds,Yes,md19crops,kg,70
FERTILIZER,Fertilizer,Yes,md27fertilizer,50kg_bags,60
PESTICIDES,Pesticides,Yes,md27pesticide,litres,65
IRRIGATION,Irrigation,Yes,md27irrigation,metres,50
LIVESTOCK_VET,Livestock & Vet,Yes,md27livestockSupply,doses,60
```

**Note:** `subcategory_source` field is historical documentation - actual child data is now in md27input polymorphic table.

---

#### Polymorphic Child Form: md27input

**Database Table:** `app_fd_md27input`

**Fields:**
- `code` (TextField, Mandatory, Unique)
- `name` (TextField, Mandatory)
- `input_category` **(SelectBox, Mandatory)** - References md27inputCategory
- `category` (TextField) - Subcategory within input type
- `pesticide_type` (TextField) - For PESTICIDES: Insecticide, Herbicide, Fungicide
- `default_unit` (TextField) - Unit of measurement
- `typical_quantity` (TextField) - Typical quantity
- `typical_quantity_per_ha` (TextField) - Per-hectare quantity
- `target` (TextField) - For PESTICIDES: target pest/disease
- `estimated_cost_per_unit` (TextField) - Cost per unit

**CSV Files:** 5 category-specific files + SEEDS merged data (61 total records)

---

#### CSV to Category Mapping

| CSV File | Category Code | Records | Description |
|----------|---------------|---------|-------------|
| *(md19crops.csv merged)* | SEEDS | 21 | Crop seeds: cereals, legumes, tubers, vegetables |
| `md27fertilizer.csv` | FERTILIZER | 10 | Compound, Nitrogen, Phosphorus, Organic fertilizers |
| `md27pesticide.csv` | PESTICIDES | 10 | Insecticides, herbicides, fungicides |
| `md27irrigation.csv` | IRRIGATION | 10 | Pipes, drip systems, sprinklers |
| `md27livestockSupply.csv` | LIVESTOCK_VET | 10 | Vaccines, medicines, feed supplements |

**Total Inputs:** 61 items

---

#### Sample Input Records

**SEEDS Category (merged from md19crops):**
```csv
code,name,input_category,category,default_unit,typical_quantity_per_ha
maize,Maize,SEEDS,cereals,kg,5-25 kg
sorghum,Sorghum,SEEDS,cereals,kg,5-25 kg
groundnuts,Groundnuts,SEEDS,legumes,kg,5-25 kg
potatoes,Potatoes,SEEDS,tubers,kg,5-25 kg
tomato,Tomato,SEEDS,vegetables,kg,5-25 kg
```

**FERTILIZER Category (md27fertilizer.csv):**
```csv
code,name,category,default_unit,typical_quantity_per_ha,estimated_cost_per_unit
NPK,NPK Fertilizer (23:10:5),Compound,50kg_bags,4-10 bags,450
UREA,Urea (46% N),Nitrogen,50kg_bags,2-8 bags,420
DAP,Di-Ammonium Phosphate,Phosphorus,50kg_bags,2-6 bags,480
COMPOST,Compost,Organic,tonnes,2-5 tonnes,300
```

**After FK Injection:**
```
code: NPK
name: NPK Fertilizer (23:10:5)
input_category: FERTILIZER  ← Injected
category: Compound
pesticide_type: (null)  ← Not applicable for fertilizer
default_unit: 50kg_bags
typical_quantity_per_ha: 4-10 bags
target: (null)
estimated_cost_per_unit: 450
```

**PESTICIDES Category (md27pesticide.csv):**
```csv
code,name,pesticide_type,default_unit,typical_quantity_per_ha,target,estimated_cost_per_unit
INSECT_GENERAL,General Purpose Insecticide,Insecticide,litres,2-5 litres,General insects,120
HERB_BROADLEAF,Broadleaf Herbicide,Herbicide,litres,2-5 litres,Broadleaf weeds,180
FUNG_DOWNY,Downy Mildew Fungicide,Fungicide,litres,2-4 litres,Downy mildew,160
```

**After FK Injection:**
```
code: INSECT_GENERAL
name: General Purpose Insecticide
input_category: PESTICIDES  ← Injected
category: (null)
pesticide_type: Insecticide
default_unit: litres
typical_quantity_per_ha: 2-5 litres
target: General insects
estimated_cost_per_unit: 120
```

---

#### Polymorphic Table Structure

| Field | SEEDS | FERTILIZER | PESTICIDES | IRRIGATION | LIVESTOCK_VET |
|-------|-------|------------|------------|------------|---------------|
| code | ✓ | ✓ | ✓ | ✓ | ✓ |
| name | ✓ | ✓ | ✓ | ✓ | ✓ |
| input_category | ✓ | ✓ | ✓ | ✓ | ✓ |
| category | ✓ | ✓ | — | ✓ | ✓ |
| pesticide_type | — | — | ✓ | — | — |
| target | — | — | ✓ | — | — |
| default_unit | ✓ | ✓ | ✓ | ✓ | ✓ |
| typical_quantity_per_ha | ✓ | ✓ | ✓ | — | — |
| estimated_cost_per_unit | — | ✓ | ✓ | ✓ | ✓ |

---

#### Historical Context: MD19 Crops Merge

**Background:**

Originally, crop seeds were stored in a separate `md19crops` form. This was architecturally incorrect because:
1. md27inputCategory defined SEEDS as a subcategory with `subcategory_source: md19crops`
2. This indicated SEEDS data should be *referenced* from crops but stored in md27input
3. Having separate table violated polymorphic table pattern

**Solution (October 27, 2025):**

21 crop records were transformed and merged into md27input.csv:
- Added `input_category: 'SEEDS'` to each record
- Mapped `crop_category` → `category` field
- Added default values for SEEDS-specific fields
- Removed md19crops form from deployment

**Result:**
- ✅ md27input now has complete data (61 records including 21 SEEDS)
- ✅ Architecture matches original design
- ✅ Cascading dropdowns work correctly

**See:** [MD19_MERGE_NOTES.md](../joget_utility/MD19_MERGE_NOTES.md) for complete details

---

#### Configuration (config/relationships.json)

```json
{
  "parent_child_relationships": {
    "md27inputCategory": {
      "child_forms": [
        {
          "form_id": "md27input",
          "relationship_type": "polymorphic_table",
          "parent_fk_field": "input_category",
          "category_mappings": {
            "FERTILIZER": "md27fertilizer.csv",
            "PESTICIDES": "md27pesticide.csv",
            "IRRIGATION": "md27irrigation.csv",
            "LIVESTOCK_VET": "md27livestockSupply.csv"
          },
          "merged_data": {
            "SEEDS": {
              "source": "md27input.csv",
              "note": "Merged from md19crops.csv on 2025-10-27"
            }
          }
        }
      ]
    }
  }
}
```

---

#### Usage in Application Forms

**Subsidy Application Form - Input Selection:**
```json
{
  "elements": [
    {
      "id": "input_category",
      "className": "org.joget.apps.form.lib.SelectBox",
      "label": "Input Category",
      "optionsBinder": {
        "formDefId": "md27inputCategory",
        "idColumn": "code",
        "labelColumn": "name"
      }
    },
    {
      "id": "input_item",
      "className": "org.joget.apps.form.lib.SelectBox",
      "label": "Specific Input",
      "optionsBinder": {
        "formDefId": "md27input",
        "idColumn": "code",
        "labelColumn": "name",
        "groupingColumn": "input_category",
        "useAjax": "true"
      },
      "controlField": "input_category"
    }
  ]
}
```

**Behavior:**
1. User selects "SEEDS" → dropdown shows: Maize, Sorghum, Groundnuts, etc.
2. User selects "FERTILIZER" → dropdown shows: NPK, Urea, DAP, Compost, etc.
3. User selects "PESTICIDES" → dropdown shows: Insecticides, Herbicides, Fungicides

---

#### Database Verification Queries

**Check category distribution:**
```sql
SELECT
    c_input_category as 'Category',
    COUNT(*) as 'Count'
FROM app_fd_md27input
GROUP BY c_input_category
ORDER BY c_input_category;

-- Expected result:
-- FERTILIZER    | 10
-- IRRIGATION    | 10
-- LIVESTOCK_VET | 10
-- PESTICIDES    | 10
-- SEEDS         | 21
```

**Check SEEDS subcategories:**
```sql
SELECT
    c_category as 'Seed Category',
    COUNT(*) as 'Count'
FROM app_fd_md27input
WHERE c_input_category = 'SEEDS'
GROUP BY c_category
ORDER BY c_category;

-- Expected result:
-- cereals     | 5
-- legumes     | 6
-- tubers      | 4
-- vegetables  | 6
```

---

**End of Part 2: Metadata Catalog**

**Next:** [Part 3: Understanding Patterns →](#part-3-understanding-patterns)

---

# Part 3: Understanding Patterns

This section explains the three metadata patterns used in the system, when to use each, and how they are implemented.

## Overview of Metadata Patterns

The system uses three distinct patterns for organizing metadata:

| Pattern | Use Case | Relationships | CSV Structure | Example |
|---------|----------|---------------|---------------|---------|
| **Pattern 1: Simple Metadata** | Standalone lookup tables | None | code, name | md01maritalStatus |
| **Pattern 2: Traditional FK** | Parent-child with explicit FK | Yes | code, name, parent_code | (Not currently used) |
| **Pattern 2: Traditional FK** | Parent-child with explicit FK | Yes | code, name (no FK!) | md25, md27 |

**Key Decision:** Pattern 2 with unified polymorphic CSVs is the **implemented approach** for parent-child relationships in this system because:
- ✅ Cleaner CSV files (no FK column clutter)
- ✅ Category determined by filename (self-documenting)
- ✅ Works seamlessly with polymorphic tables
- ✅ Data augmentation happens automatically during import

---

## 3.1: Pattern 1 - Simple Metadata

### When to Use

Use Pattern 1 for **standalone metadata** with no relationships to other forms:
- ✅ Lookup tables (countries, languages, statuses)
- ✅ Static reference data
- ✅ No parent-child dependencies
- ✅ No categorization needed

### Structure

**CSV File:**
```csv
code,name
SINGLE,Single
MARRIED,Married
DIVORCED,Divorced
WIDOWED,Widowed
```

**Database Table:**
```
app_fd_md01maritalStatus
├── id (auto)
├── c_code (unique)
└── c_name
```

**Joget Form Definition:**
```json
{
  "properties": {
    "id": "md01maritalStatus",
    "name": "MD.01 - Marital Status",
    "tableName": "md01maritalStatus"
  },
  "elements": [
    {
      "className": "org.joget.apps.form.lib.TextField",
      "properties": {
        "id": "code",
        "label": "Code",
        "validator": {
          "className": "org.joget.apps.form.lib.DuplicateValueValidator",
          "properties": {
            "formDefId": "md01maritalStatus",
            "fieldId": "code",
            "mandatory": "true"
          }
        }
      }
    },
    {
      "className": "org.joget.apps.form.lib.TextField",
      "properties": {
        "id": "name",
        "label": "Name"
      }
    }
  ]
}
```

### Characteristics

| Aspect | Details |
|--------|---------|
| **CSV Columns** | 2-5 columns (code, name, optional extras) |
| **Form Fields** | TextFields only, no SelectBoxes |
| **Database** | Single table, no foreign keys |
| **Deployment** | Single CSV → Single form → Single table |
| **Maintenance** | Edit CSV, redeploy |

### Examples in System

All 32 simple forms use Pattern 1:
- md01maritalStatus (5 records)
- md02language (3 records)
- md03district (10 records)
- md04agroEcologicalZone (4 records)
- ...
- md37collectionPoint (10 records)

### Advantages

✅ **Simple** - Easiest to understand and maintain
✅ **Fast deployment** - No dependencies
✅ **Direct updates** - Change CSV and redeploy
✅ **No cascading** - No form dependencies

### Limitations

❌ **No relationships** - Cannot model parent-child data
❌ **No categorization** - All records at same level
❌ **Duplication risk** - Similar data may be repeated across forms

---

## 3.2: Pattern 2 - Traditional Foreign Key (Polymorphic Tables)

### When to Use

Use Pattern 2 when:
- ✅ Parent-child relationship exists
- ✅ FK should be **visible and editable** in CSV
- ✅ Multiple child entity types share similar structure (polymorphic table)
- ✅ Using **unified CSV** with explicit FK column

**This is the pattern used for MD25 Equipment and MD27 Input hierarchies.**

### Structure

**Example: MD25 Equipment Hierarchy**

**Parent CSV (md25equipCategory.csv):**
```csv
code,name
TILLAGE,Tillage Equipment
PLANTING,Planting Equipment
GENERAL_TOOLS,General Tools
```

**Child CSV (md25equipment.csv) - Unified Polymorphic Table:**
```csv
code,name,equipment_category,power_source,typical_lifespan_years
PLOUGH_ANIMAL,Animal-Drawn Plough,TILLAGE,animal,10
SEEDER_MAIZE,Maize Seeder,PLANTING,manual,8
HAND_HOE,Hand Hoe,GENERAL_TOOLS,manual,5
```

**Key Point:** `equipment_category` column **exists explicitly in CSV** - no FK injection needed.

### Database Tables

**Parent Table:**
```
app_fd_md25equipCategory
├── id (auto)
├── c_code (unique)
└── c_name
```

**Child Table (Polymorphic):**
```
app_fd_md25equipment
├── id (auto)
├── c_code (unique)
├── c_name
├── c_equipment_category (FK) ← Explicitly in CSV
├── c_power_source
├── c_typical_lifespan_years
└── ... (sparse columns for different equipment types)
```

### Joget Form Definition

**Child Form (CRITICAL: SelectBox for FK):**
```json
{
  "properties": {
    "id": "md25equipment",
    "tableName": "md25equipment"
  },
  "elements": [
    {
      "className": "org.joget.apps.form.lib.TextField",
      "properties": {"id": "code", "label": "Equipment Code"}
    },
    {
      "className": "org.joget.apps.form.lib.TextField",
      "properties": {"id": "name", "label": "Equipment Name"}
    },
    {
      "className": "org.joget.apps.form.lib.SelectBox",
      "properties": {
        "id": "equipment_category",
        "label": "Equipment Category",
        "optionsBinder": {
          "className": "org.joget.apps.form.lib.FormOptionsBinder",
          "properties": {
            "formDefId": "md25equipCategory",
            "idColumn": "code",
            "labelColumn": "name"
          }
        }
      }
    }
  ]
}
```

**CRITICAL:** The `equipment_category` field **MUST be a SelectBox** (not TextField) for cascading dropdowns to work.

### Usage in Application Forms

**Cascading Dropdown Configuration (e.g., in Subsidy Application form):**
```json
{
  "elements": [
    {
      "id": "equipment_category",
      "className": "org.joget.apps.form.lib.SelectBox",
      "properties": {
        "label": "Equipment Category",
        "optionsBinder": {
          "formDefId": "md25equipCategory",
          "idColumn": "code",
          "labelColumn": "name"
        }
      }
    },
    {
      "id": "equipment",
      "className": "org.joget.apps.form.lib.SelectBox",
      "properties": {
        "label": "Equipment",
        "optionsBinder": {
          "formDefId": "md25equipment",
          "idColumn": "code",
          "labelColumn": "name",
          "groupingColumn": "equipment_category",
          "useAjax": "true"
        },
        "controlField": "equipment_category"
      }
    }
  ]
}
```

### Advantages

✅ **Explicit relationships** - FK visible in CSV, easy to verify
✅ **Single unified CSV** - All equipment/inputs in one file
✅ **Polymorphic table** - Flexible sparse columns for different types
✅ **Standard pattern** - Familiar to SQL developers
✅ **Simple deployment** - No FK injection logic needed

### Limitations

⚠️ **Large CSV files** - md25equipment.csv has 85 records with many columns
⚠️ **Sparse columns** - Many NULL/empty fields depending on type
⚠️ **Manual FK entry** - Must ensure category codes match parent

### Real Implementation

This pattern is used for:
- **MD25 Equipment**: 85 equipment items across 9 categories in `md25equipment.csv`
- **MD27 Input**: 61 input items across 5 categories in `md27input.csv`

---

## 3.3: Polymorphic Table Pattern

### What is a Polymorphic Table?

A **polymorphic table** stores multiple entity types in a **single table** using a **type/category field** to differentiate them. It uses **sparse columns** where each row only populates fields relevant to its type.

**Example:** md25equipment table stores 9 equipment types:
```
┌──────────────────────────────────────────────────────────────┐
│                 app_fd_md25equipment                         │
│              (Single polymorphic table)                      │
├──────────────────────────────────────────────────────────────┤
│ code | name | equipment_category | tool_cat | power | ... │
├──────┼──────┼────────────────────┼──────────┼───────┼─────┤
│ HOE  | Hoe  | GENERAL_TOOLS      | Weeding  | NULL  | ... │ ← Tool fields
│ PLOU | Plgh | TILLAGE            | NULL     | animal| ... │ ← Tillage fields
│ SPRY | Spry | PEST_CONTROL       | NULL     | NULL  | ... │ ← Pesticide fields
└──────────────────────────────────────────────────────────────┘
           ↑                            ↑
     Type discriminator         Sparse columns
                               (many NULLs)
```

### When to Use

Use polymorphic tables when:
- ✅ Multiple similar entity types share **70%+ common fields**
- ✅ Entity types have **type-specific fields** (remainder 30%)
- ✅ Want **single form/table** instead of multiple forms
- ✅ Acceptable to have **sparse columns** (NULLs)

### Alternatives to Polymorphic Tables

**Option A: Separate Forms per Type**
```
md25tillageEquipment (form + table)
md25plantingEquipment (form + table)
md25pestControlEquipment (form + table)
... (9 separate forms/tables)
```

**Advantages:**
- ✅ No sparse columns
- ✅ Type-specific validation per form
- ✅ Cleaner schema

**Disadvantages:**
- ❌ 9 forms to manage (vs 1)
- ❌ 9 tables (vs 1)
- ❌ 9 API endpoints (vs 1)
- ❌ Complex queries (UNION across 9 tables)
- ❌ Harder to add new types

**Option B: Polymorphic Table (Current Implementation)**
```
md25equipment (single form + table with all types)
```

**Advantages:**
- ✅ Single form to manage
- ✅ Single table (simple queries)
- ✅ Single API endpoint
- ✅ Easy to add new types (add category + columns)

**Disadvantages:**
- ❌ Sparse columns (many NULLs)
- ❌ Less type-specific validation
- ❌ Schema less intuitive

### Decision Matrix

| Factor | Use Separate Forms | Use Polymorphic Table |
|--------|-------------------|----------------------|
| Types share >70% fields | — | ✅ |
| Types share <50% fields | ✅ | — |
| Need type-specific validation | ✅ | — |
| Frequent addition of new types | — | ✅ |
| Complex per-type logic | ✅ | — |
| Want simple queries/API | — | ✅ |
| Schema clarity important | ✅ | — |
| Minimize forms/maintenance | — | ✅ |

### Current Polymorphic Tables

#### 1. md25equipment (85 records, 9 types)

**Common fields (all types):**
- code, name, equipment_category, estimated_cost_lsl

**Type-specific fields (sparse):**
- tool_category (GENERAL_TOOLS only)
- power_source (TILLAGE, PLANTING, TRANSPORT)
- sprayer_type (PEST_CONTROL only)
- irrigation_type (IRRIGATION only)
- storage_type (STORAGE only)
- processing_type (PROCESSING only)
- ... 21 total fields

**Field usage by type:**
```
GENERAL_TOOLS:  uses 6/21 fields (71% null)
TILLAGE:        uses 8/21 fields (62% null)
PEST_CONTROL:   uses 7/21 fields (67% null)
```

**Justification for polymorphic:**
- 85 equipment items across 9 types
- Alternative would be 9 forms + 9 tables + 9 APIs
- Common fields: code, name, category, cost (70%+ shared)

#### 2. md27input (61 records, 5 types)

**Common fields (all types):**
- code, name, input_category, category, default_unit, typical_quantity_per_ha

**Type-specific fields (sparse):**
- pesticide_type (PESTICIDES only)
- target (PESTICIDES only)
- estimated_cost_per_unit (varies)

**Field usage by type:**
```
SEEDS:         uses 6/10 fields (40% null)
FERTILIZER:    uses 7/10 fields (30% null)
PESTICIDES:    uses 8/10 fields (20% null)
```

**Justification for polymorphic:**
- 61 input items across 5 types
- High field overlap (80%+ shared)
- Simpler than 5 separate forms

### Implementation Details

#### Defining Sparse Columns

**In form_generator.py:**
```python
# When generating polymorphic child form
def generate_polymorphic_form(parent_form, child_csvs):
    # Collect ALL columns from ALL category CSVs
    all_columns = set()
    for csv in child_csvs:
        all_columns.update(get_csv_columns(csv))

    # Create form with ALL columns
    # Result: Each category uses subset of columns
    # Unused columns will be NULL for that category

    fields = []
    for column in all_columns:
        if column == parent_fk_field:
            # Parent FK must be SelectBox
            fields.append(create_selectbox(column, parent_form))
        else:
            # Other fields are TextFields
            fields.append(create_textfield(column))

    return create_form(fields)
```

#### Querying Polymorphic Tables

**Get all equipment:**
```sql
SELECT * FROM app_fd_md25equipment;
```

**Get specific category:**
```sql
SELECT * FROM app_fd_md25equipment
WHERE c_equipment_category = 'TILLAGE';
```

**Get with non-null type-specific field:**
```sql
-- Get only equipment with power source specified
SELECT * FROM app_fd_md25equipment
WHERE c_power_source IS NOT NULL;
```

**Count by category:**
```sql
SELECT
    c_equipment_category,
    COUNT(*) as count
FROM app_fd_md25equipment
GROUP BY c_equipment_category;
```

### Performance Considerations

**Sparse columns impact:**
- ✅ **Minimal impact** in MySQL/MariaDB (NULLs use minimal space)
- ✅ **Indexes work normally** on category column
- ❌ **Statistics less accurate** (table scans slightly slower)

**Best practices:**
- Index the category/type column
- Use WHERE category = 'X' in queries (utilizes index)
- Consider partitioning by category for very large tables (1M+ rows)

### Column Limit Considerations

**MySQL column limit:** 4096 columns per table (practical limit ~1000)

**Our tables:**
- md25equipment: 21 columns (✅ well within limit)
- md27input: 10 columns (✅ well within limit)

**When polymorphic table won't work:**
- If types have 100+ unique fields each
- If need >1000 total columns
- Solution: Fall back to separate forms per type

---

## 3.4: Pattern Selection Guide

### Decision Flowchart

```
┌─────────────────────────────────────┐
│  Do records have parent-child       │
│  relationship?                      │
└──────────────┬──────────────────────┘
               │
        ┌──────┴──────┐
        │             │
       NO            YES
        │             │
        ↓             ↓
┌──────────────┐  ┌────────────────────────────┐
│ Pattern 1:   │  │ Are child records          │
│ Simple       │  │ naturally grouped by       │
│ Metadata     │  │ category/type?             │
└──────────────┘  └──────┬─────────────────────┘
                         │
                  ┌──────┴──────┐
                  │             │
                 NO            YES
                  │             │
                  ↓             ↓
          ┌───────────────┐  ┌────────────────────┐
          │ Pattern 2:    │  │ Do types share     │
          │ Traditional   │  │ 70%+ fields?       │
          │ FK            │  └────┬───────────────┘
          │               │       │
          │ (Not used in  │  ┌────┴────┐
          │  our system)  │  │         │
          └───────────────┘ NO        YES
                            │         │
                            ↓         ↓
                    ┌──────────┐  ┌──────────────┐
                    │ Separate │  │ Pattern 2:   │
                    │ Forms    │  │ Traditional  │
                    │ per Type │  │ FK with      │
                    │          │  │ Polymorphic  │
                    │ (Not     │  │ Table        │
                    │ used)    │  │              │
                    └──────────┘  │ ✅ RECOMMENDED│
                                  └──────────────┘
```

### Examples by Pattern

| Scenario | Pattern | Rationale |
|----------|---------|-----------|
| Marital status codes | Pattern 1 | No relationships, simple lookup |
| Language codes | Pattern 1 | Standalone, no hierarchy |
| District list | Pattern 1 | No parent, independent |
| Equipment with 9 categories | Pattern 2 | Grouped by category, shared fields |
| Inputs with 5 categories | Pattern 2 | Grouped by category, polymorphic |
| Countries → States | Pattern 2 | If needed, FK in CSV |

### Implementation Checklist

#### For Pattern 1 (Simple):
- [ ] Create single CSV with code,name columns
- [ ] Run form_generator.py (basic mode)
- [ ] Deploy with --deploy-master-data

#### For Pattern 2 (Traditional FK + Polymorphic):
- [ ] Create parent CSV with category codes
- [ ] Create 1 CSV per category (no FK column!)
- [ ] Update config/relationships.json with mappings
- [ ] Run form_generator.py with --pattern2 flag
- [ ] Ensure child form has SelectBox for parent FK
- [ ] Deploy parent first
- [ ] Deploy child form
- [ ] Populate data (DataAugmentor will inject FK)
- [ ] Verify cascading dropdowns work in Joget UI

---

**End of Part 3: Understanding Patterns**

**Next:** [Part 4: How to Add New Metadata →](#part-4-how-to-add-new-metadata)

---

# Part 4: How to Add New Metadata

## Overview

This section provides step-by-step guides for adding new metadata to the system. Whether you're adding a simple lookup table or a complex parent-child hierarchy with polymorphic tables, these guides will walk you through the entire process.

**What You'll Learn:**
- How to add simple metadata forms (Pattern 1)
- How to add parent-child relationships with FK injection (Pattern 2)
- How to use the form generator utility
- Common pitfalls and how to avoid them
- Verification and testing procedures

---

## 4.1 Adding Simple Metadata (Pattern 1)

Simple metadata forms are standalone lookup tables with no relationships to other forms. They're the easiest to add and account for the majority of our MDM forms (32 out of 37).

### When to Use Pattern 1

Use Pattern 1 when:
- ✅ Data is independent (no parent-child relationships)
- ✅ Records are self-contained
- ✅ Form doesn't need to reference other forms
- ✅ Examples: marital status, languages, payment methods, document types

### Complete Walkthrough: Adding md38currency

Let's add a new metadata form for currencies. This example demonstrates every step from planning to deployment.

#### Step 1: Plan Your Data Structure

**Business Requirement:** Store currency codes for international transactions.

**Data Fields:**
- `code` - Currency code (ISO 4217, e.g., "USD", "EUR")
- `name` - Currency name (e.g., "United States Dollar")
- `symbol` - Currency symbol (e.g., "$", "€")
- `is_active` - Whether currency is currently used (true/false)

**Sample Data:**
```csv
code,name,symbol,is_active
USD,United States Dollar,$,true
EUR,Euro,€,true
GBP,British Pound,£,true
ZAR,South African Rand,R,true
BWP,Botswana Pula,P,true
JPY,Japanese Yen,¥,false
```

#### Step 2: Create CSV Data File

Create file: `data/metadata/md38currency.csv`

```bash
cd /Users/aarelaponin/PycharmProjects/dev/gam_utilities/joget_utility
```

**File Path:** `data/metadata/md38currency.csv`

**Content:**
```csv
code,name,symbol,is_active
USD,United States Dollar,$,true
EUR,Euro,€,true
GBP,British Pound,£,true
ZAR,South African Rand,R,true
BWP,Botswana Pula,P,true
```

**Important:**
- ✅ First row MUST be header with field names
- ✅ Field names should be lowercase with underscores
- ✅ No empty rows at end of file
- ✅ Use UTF-8 encoding for special characters (€, £, etc.)
- ✅ Boolean values as "true"/"false" (lowercase)

#### Step 3: Auto-Generate Form Definition

Use the form generator to create the JSON form definition:

```bash
python processors/form_generator.py \
  --csv data/metadata/md38currency.csv \
  --form-id md38currency \
  --form-name "MD.38 - Currency" \
  --output data/metadata_forms/md38currency.json
```

**What This Does:**
1. Reads CSV header to detect fields
2. Infers field types from data:
   - `code`, `name`, `symbol` → TextField
   - `is_active` → SelectBox with Yes/No options
3. Creates Joget form JSON with proper structure
4. Adds validators (required fields)
5. Saves to `data/metadata_forms/md38currency.json`

**Generated Form Structure:**
```json
{
  "className": "org.joget.apps.form.model.Form",
  "properties": {
    "id": "md38currency",
    "name": "MD.38 - Currency",
    "tableName": "md38currency",
    "description": ""
  },
  "elements": [
    {
      "className": "org.joget.apps.form.model.Section",
      "properties": {"label": "Currency Details"},
      "elements": [
        {
          "className": "org.joget.apps.form.lib.TextField",
          "properties": {
            "id": "code",
            "label": "Code",
            "required": "true",
            "validator": {"className": "org.joget.apps.form.lib.DefaultValidator"}
          }
        },
        {
          "className": "org.joget.apps.form.lib.TextField",
          "properties": {
            "id": "name",
            "label": "Name",
            "required": "true"
          }
        },
        {
          "className": "org.joget.apps.form.lib.TextField",
          "properties": {
            "id": "symbol",
            "label": "Symbol",
            "required": "true"
          }
        },
        {
          "className": "org.joget.apps.form.lib.SelectBox",
          "properties": {
            "id": "is_active",
            "label": "Is Active",
            "options": [
              {"value": "true", "label": "Yes"},
              {"value": "false", "label": "No"}
            ]
          }
        }
      ]
    }
  ]
}
```

#### Step 4: Review and Customize Form (Optional)

**Automatic generation is good for most cases**, but you may want to customize:

1. **Add field descriptions:**
```json
{
  "id": "code",
  "label": "Currency Code",
  "description": "ISO 4217 3-letter currency code (e.g., USD, EUR)"
}
```

2. **Change field size:**
```json
{
  "id": "code",
  "label": "Code",
  "size": "10",      // Max 10 characters
  "maxlength": "3"   // Enforce 3-letter limit
}
```

3. **Add custom validation:**
```json
{
  "id": "code",
  "validator": {
    "className": "org.joget.apps.form.lib.DefaultValidator",
    "properties": {
      "type": "custom",
      "customPattern": "^[A-Z]{3}$",  // Exactly 3 uppercase letters
      "customPatternMessage": "Currency code must be 3 uppercase letters (e.g., USD)"
    }
  }
}
```

**For most simple metadata, automatic generation is sufficient.**

#### Step 5: Add to Deployment Configuration

Edit `config/master_data_deploy.yaml`:

```yaml
metadata_forms:
  # ... existing forms ...

  - form_id: md38currency
    csv_file: data/metadata/md38currency.csv
    form_definition: data/metadata_forms/md38currency.json
    description: "Currency codes for international transactions"
    depends_on: []  # No dependencies
    record_count: 5  # Expected records
```

**Important:**
- Add in numerical order (md38 comes after md37)
- Set `depends_on: []` for simple metadata (no parent forms)
- Update `record_count` with actual CSV row count (excluding header)

#### Step 6: Deploy to Joget

**Full Deployment (Forms + Data):**
```bash
python joget_utility.py --deploy-master-data --yes
```

This will deploy ALL metadata forms, including your new md38currency.

**Selective Deployment (Just md38currency):**
```bash
python joget_utility.py --deploy-specific md38currency --yes
```

**Expected Output:**
```
Master Data Deployment
======================

Phase 1: Creating Forms
  ✓ md38currency (38/38)

Phase 2: Verifying API Endpoints
  ✓ md38currency API found (api_md38currency_saveOrUpdate)

Phase 3: Populating Data
  ✓ md38currency: 5/5 records posted

Deployment Summary
------------------
Forms created: 38/38 (100%)
Records posted: 421/421 (100%)
Failed records: 0

✅ Deployment successful!
```

#### Step 7: Verify Deployment

**Check Database Table Created:**
```sql
-- Check table exists
SHOW TABLES LIKE 'app_fd_md38currency';

-- Verify structure
DESCRIBE app_fd_md38currency;

-- Count records
SELECT COUNT(*) FROM app_fd_md38currency;
-- Expected: 5

-- View all records
SELECT c_code, c_name, c_symbol, c_is_active
FROM app_fd_md38currency
ORDER BY c_code;
```

**Expected Output:**
```
+--------+------------------------+--------+-------------+
| c_code | c_name                 | c_symbol | c_is_active |
+--------+------------------------+--------+-------------+
| BWP    | Botswana Pula          | P      | true        |
| EUR    | Euro                   | €      | true        |
| GBP    | British Pound          | £      | true        |
| USD    | United States Dollar   | $      | true        |
| ZAR    | South African Rand     | R      | true        |
+--------+------------------------+--------+-------------+
```

**Check Form in Joget UI:**
1. Navigate to: `http://localhost:8080/jw/web/console/app/subsidyApplication/1/form/builder`
2. Find "MD.38 - Currency" in form list
3. Open form builder - should show all fields
4. Preview form - should display correctly
5. Try adding test record manually

#### Step 8: Test in Application Context

If this metadata will be referenced by other forms (e.g., a payment form with currency dropdown):

**Create Test SelectBox:**
```json
{
  "className": "org.joget.apps.form.lib.SelectBox",
  "properties": {
    "id": "currency",
    "label": "Currency",
    "options_type": "form",
    "options_form_id": "md38currency",
    "options_value_field": "code",
    "options_label_field": "name"
  }
}
```

**Expected Dropdown Options:**
```
[ ] United States Dollar (USD)
[ ] Euro (EUR)
[ ] British Pound (GBP)
[ ] South African Rand (ZAR)
[ ] Botswana Pula (BWP)
```

---

### Common Issues: Simple Metadata

#### Issue 1: Form Created But No Data

**Symptoms:**
- Form appears in Joget
- API endpoint found
- 0 records in database

**Causes:**
1. CSV file has wrong encoding (non-UTF-8)
2. CSV has extra blank rows
3. Field names don't match form definition
4. Validation errors (e.g., required field missing in CSV)

**Solution:**
```bash
# Check CSV encoding
file -I data/metadata/md38currency.csv
# Should show: charset=utf-8

# Check for blank rows
tail -5 data/metadata/md38currency.csv
# Should NOT show empty lines after last record

# Retry deployment
python joget_utility.py --deploy-specific md38currency --data-only --yes
```

#### Issue 2: Special Characters Not Displaying

**Symptoms:**
- Currency symbols show as "?" or garbled text
- Example: € displays as â‚¬

**Cause:** CSV not saved as UTF-8

**Solution:**
1. Open CSV in text editor (VS Code, Sublime, etc.)
2. Save as UTF-8 encoding (not UTF-8 BOM or ANSI)
3. Redeploy data:
```bash
python joget_utility.py --deploy-specific md38currency --data-only --yes
```

#### Issue 3: Form Generator Fails

**Symptoms:**
```
Error: Cannot detect field types from CSV
```

**Causes:**
1. CSV header row missing
2. All fields are empty
3. CSV syntax errors (unmatched quotes, wrong delimiter)

**Solution:**
```bash
# Validate CSV structure
python -c "
import csv
with open('data/metadata/md38currency.csv') as f:
    reader = csv.DictReader(f)
    print('Headers:', reader.fieldnames)
    print('First row:', next(reader))
"
```

---

### Quick Reference: Adding Simple Metadata

**Checklist:**
- [ ] Plan data structure (fields and sample data)
- [ ] Create CSV file in `data/metadata/mdXX<name>.csv`
- [ ] Verify CSV encoding is UTF-8
- [ ] Generate form definition: `python processors/form_generator.py ...`
- [ ] Review generated form (optional customization)
- [ ] Add to `config/master_data_deploy.yaml`
- [ ] Deploy: `python joget_utility.py --deploy-specific mdXX<name> --yes`
- [ ] Verify database table and record count
- [ ] Test form in Joget UI
- [ ] If referenced by other forms, test SelectBox integration

**Time Estimate:**
- Planning: 10-15 minutes
- CSV creation: 5-10 minutes
- Form generation: 2 minutes
- Deployment: 2-5 minutes
- Verification: 5 minutes
- **Total: 25-40 minutes**

---

## 4.2 Adding Parent-Child Relationship (Pattern 2)

> **📌 CURRENT IMPLEMENTATION NOTE:**
>
> **MD25 Equipment and MD27 Input use Pattern 2 with UNIFIED CSVs:**
> - `md25equipment.csv` - 85 records with **explicit** `equipment_category` column
> - `md27input.csv` - 61 records with **explicit** `input_category` column
>
> **To add new equipment/input items:** Simply add rows to these CSV files with the appropriate category code and redeploy.
>
> **The FK injection approach described below** (separate category CSVs + DataAugmentor) is **not currently used** but documented for reference.

---

### Adding Records to Existing Polymorphic Tables

**Quick Guide: Add new equipment item to MD25**

1. Edit `data/metadata/md25equipment.csv`
2. Add new row with `equipment_category` value (e.g., `TILLAGE`, `PLANTING`, etc.)
3. Redeploy: `python joget_utility.py --deploy-master-data --yes`

**Quick Guide: Add new input item to MD27**

1. Edit `data/metadata/md27input.csv`
2. Add new row with `input_category` value (e.g., `SEEDS`, `FERTILIZER`, etc.)
3. Redeploy: `python joget_utility.py --deploy-master-data --yes`

---

### Alternative Approach: FK Injection (For Reference Only)

This section describes an alternative Pattern 2 approach using separate category CSVs with automatic FK injection via DataAugmentor. **This is NOT the current implementation for MD25/MD27.**

**When to Use FK Injection Approach:**
- ✅ You want to manage category-specific items in separate CSV files
- ✅ You need automatic FK injection during deployment
- ⚠️ More complex configuration required

**Advantages:**
- Separate CSV files for each category (easier to manage)
- Automatic FK injection (no manual FK column in child CSVs)

**Tradeoffs:**
- More complex configuration (relationships.json)
- Requires DataAugmentor during deployment
- Parent MUST be deployed before children

---

### Complete Walkthrough: Adding md39vehicleCategory and md39vehicle

Let's add a new parent-child relationship for vehicle types. This demonstrates the full Pattern 2 implementation.

**Business Requirement:** Track vehicles subsidized to farmers with different categories (tractors, trucks, motorcycles).

#### Planning Phase

**Parent: md39vehicleCategory**
- Defines vehicle categories
- Fields: code, name, has_subcategory, typical_subsidy_percent
- Categories: TRACTOR, TRUCK, MOTORCYCLE

**Child: md39vehicle (Polymorphic Table)**
- Stores all vehicle items across categories
- Fields:
  - Common: code, name, vehicle_category (FK to parent)
  - Category-specific: engine_size, load_capacity, fuel_type
- Managed via separate CSV files per category

**CSV Files:**
- `md39vehicleCategory.csv` - 3 category records
- `md39tractor.csv` - Tractor items (injected with vehicle_category=TRACTOR)
- `md39truck.csv` - Truck items (injected with vehicle_category=TRUCK)
- `md39motorcycle.csv` - Motorcycle items (injected with vehicle_category=MOTORCYCLE)

**Decision:** Use polymorphic table pattern because:
- Categories share 80%+ fields (code, name, vehicle_category)
- Only 20% are category-specific (engine_size, load_capacity)
- Need unified vehicle registry for reporting
- Sparse columns acceptable (NULL values for non-applicable fields)

---

### Step 1: Create Parent Form (md39vehicleCategory)

**CSV:** `data/metadata/md39vehicleCategory.csv`
```csv
code,name,has_subcategory,subcategory_source,typical_subsidy_percent
TRACTOR,Agricultural Tractor,Yes,md39tractor,60
TRUCK,Farm Transport Truck,Yes,md39truck,50
MOTORCYCLE,Motorcycle,Yes,md39motorcycle,40
```

**Generate Form:**
```bash
python processors/form_generator.py \
  --csv data/metadata/md39vehicleCategory.csv \
  --form-id md39vehicleCategory \
  --form-name "MD.39 - Vehicle Category" \
  --output data/metadata_forms/md39vehicleCategory.json
```

**Customize Form:** (Optional but recommended)

Edit `data/metadata_forms/md39vehicleCategory.json`:

```json
{
  "className": "org.joget.apps.form.model.Form",
  "properties": {
    "id": "md39vehicleCategory",
    "name": "MD.39 - Vehicle Category",
    "tableName": "md39vehicleCategory",
    "description": "Vehicle categories for subsidy tracking"
  },
  "elements": [
    {
      "className": "org.joget.apps.form.model.Section",
      "properties": {"label": "Category Details"},
      "elements": [
        {
          "className": "org.joget.apps.form.lib.TextField",
          "properties": {
            "id": "code",
            "label": "Category Code",
            "required": "true",
            "maxlength": "20"
          }
        },
        {
          "className": "org.joget.apps.form.lib.TextField",
          "properties": {
            "id": "name",
            "label": "Category Name",
            "required": "true"
          }
        },
        {
          "className": "org.joget.apps.form.lib.SelectBox",
          "properties": {
            "id": "has_subcategory",
            "label": "Has Subcategories",
            "options": [
              {"value": "Yes", "label": "Yes"},
              {"value": "No", "label": "No"}
            ]
          }
        },
        {
          "className": "org.joget.apps.form.lib.TextField",
          "properties": {
            "id": "subcategory_source",
            "label": "Subcategory Source",
            "description": "CSV file name for subcategory items"
          }
        },
        {
          "className": "org.joget.apps.form.lib.TextField",
          "properties": {
            "id": "typical_subsidy_percent",
            "label": "Typical Subsidy %",
            "description": "Default subsidy percentage for this category"
          }
        }
      ]
    }
  ]
}
```

---

### Step 2: Create Category-Specific CSV Files

Create separate CSV files for each vehicle category.

**File:** `data/metadata/md39tractor.csv`
```csv
code,name,engine_size,fuel_type,load_capacity
T100,Small Farm Tractor (30HP),30HP,Diesel,
T200,Medium Tractor (50HP),50HP,Diesel,
T300,Large Tractor (75HP),75HP,Diesel,
T400,Heavy Duty Tractor (100HP),100HP,Diesel,
```

**File:** `data/metadata/md39truck.csv`
```csv
code,name,engine_size,fuel_type,load_capacity
TR100,Light Pickup Truck,2.5L,Diesel,1 tonne
TR200,Medium Truck,4.0L,Diesel,3 tonnes
TR300,Heavy Truck,6.0L,Diesel,5 tonnes
```

**File:** `data/metadata/md39motorcycle.csv`
```csv
code,name,engine_size,fuel_type,load_capacity
M100,Motorcycle 125cc,125cc,Petrol,
M200,Motorcycle 250cc,250cc,Petrol,
```

**Important:**
- ❌ **DO NOT include `vehicle_category` field** in these CSVs
- ✅ DataAugmentor will inject `vehicle_category` automatically based on filename
- ✅ Leave sparse columns empty (e.g., tractors don't have `load_capacity`)
- ✅ All category CSVs must have same field structure (for polymorphic table)

---

### Step 3: Create Polymorphic Child Form (md39vehicle)

The child form needs ALL fields from all categories (union of fields).

**Combined Field Set:**
- Common: code, name, vehicle_category (FK)
- Category-specific: engine_size, fuel_type, load_capacity

**Generate Base Form:**
```bash
# Use one of the category CSVs as template
python processors/form_generator.py \
  --csv data/metadata/md39tractor.csv \
  --form-id md39vehicle \
  --form-name "MD.39 - Vehicle" \
  --output data/metadata_forms/md39vehicle.json
```

**Customize to Add FK Field:**

Edit `data/metadata_forms/md39vehicle.json`:

```json
{
  "className": "org.joget.apps.form.model.Form",
  "properties": {
    "id": "md39vehicle",
    "name": "MD.39 - Vehicle",
    "tableName": "md39vehicle",
    "description": "Vehicle items across all categories"
  },
  "elements": [
    {
      "className": "org.joget.apps.form.model.Section",
      "properties": {"label": "Vehicle Details"},
      "elements": [
        {
          "className": "org.joget.apps.form.lib.SelectBox",
          "properties": {
            "id": "vehicle_category",
            "label": "Vehicle Category",
            "required": "true",
            "options_type": "form",
            "options_form_id": "md39vehicleCategory",
            "options_value_field": "code",
            "options_label_field": "name",
            "validator": {
              "className": "org.joget.apps.form.lib.DefaultValidator"
            }
          }
        },
        {
          "className": "org.joget.apps.form.lib.TextField",
          "properties": {
            "id": "code",
            "label": "Vehicle Code",
            "required": "true"
          }
        },
        {
          "className": "org.joget.apps.form.lib.TextField",
          "properties": {
            "id": "name",
            "label": "Vehicle Name",
            "required": "true"
          }
        },
        {
          "className": "org.joget.apps.form.lib.TextField",
          "properties": {
            "id": "engine_size",
            "label": "Engine Size",
            "description": "E.g., 30HP, 2.5L, 125cc"
          }
        },
        {
          "className": "org.joget.apps.form.lib.SelectBox",
          "properties": {
            "id": "fuel_type",
            "label": "Fuel Type",
            "options": [
              {"value": "Diesel", "label": "Diesel"},
              {"value": "Petrol", "label": "Petrol"},
              {"value": "Electric", "label": "Electric"}
            ]
          }
        },
        {
          "className": "org.joget.apps.form.lib.TextField",
          "properties": {
            "id": "load_capacity",
            "label": "Load Capacity",
            "description": "For trucks only (e.g., 1 tonne, 3 tonnes)"
          }
        }
      ]
    }
  ]
}
```

**Critical:**
- ✅ `vehicle_category` MUST be **SelectBox** (not TextField)
- ✅ `options_form_id: "md39vehicleCategory"` references parent form
- ✅ `required: "true"` ensures every vehicle has category
- ✅ All category-specific fields (engine_size, load_capacity) are optional
- ✅ Sparse columns acceptable (tractors will have NULL load_capacity)

---

### Step 4: Configure FK Injection (relationships.json)

Edit `config/relationships.json` to add FK injection mapping:

```json
{
  "parent_child_relationships": {
    "md25equipmentCategory": {
      "child_forms": [{
        "form_id": "md25equipment",
        "parent_fk_field": "equipment_category",
        "category_mappings": {
          "TILLAGE": "md25tillageEquipment.csv",
          "PLANTING": "md25plantingEquipment.csv",
          "IRRIGATION": "md25irrigationEquipment.csv",
          "HARVESTING": "md25harvestingEquipment.csv",
          "TRANSPORT": "md25transportEquipment.csv",
          "PROCESSING": "md25processingEquipment.csv",
          "STORAGE": "md25storageEquipment.csv",
          "LIVESTOCK": "md25livestockEquipment.csv",
          "GENERAL": "md25generalTools.csv"
        }
      }]
    },
    "md27inputCategory": {
      "child_forms": [{
        "form_id": "md27input",
        "parent_fk_field": "input_category",
        "category_mappings": {
          "FERTILIZER": "md27fertilizer.csv",
          "PESTICIDES": "md27pesticide.csv",
          "IRRIGATION": "md27irrigation.csv",
          "LIVESTOCK_VET": "md27livestockSupply.csv",
          "SEEDS": "md27seeds.csv"
        }
      }]
    },
    "md39vehicleCategory": {
      "child_forms": [{
        "form_id": "md39vehicle",
        "parent_fk_field": "vehicle_category",
        "category_mappings": {
          "TRACTOR": "md39tractor.csv",
          "TRUCK": "md39truck.csv",
          "MOTORCYCLE": "md39motorcycle.csv"
        }
      }]
    }
  }
}
```

**Structure Explanation:**
- **Parent form ID:** `md39vehicleCategory`
- **Child form ID:** `md39vehicle`
- **FK field name:** `vehicle_category` (MUST match field ID in child form)
- **Category mappings:** Map parent category code → CSV filename

**How DataAugmentor Uses This:**
1. Reads `md39tractor.csv`
2. Finds mapping: `TRACTOR → md39tractor.csv`
3. Injects `vehicle_category: "TRACTOR"` into every record
4. Repeats for all category CSV files
5. Results in unified polymorphic table

---

### Step 5: Add to Deployment Configuration

Edit `config/master_data_deploy.yaml`:

```yaml
metadata_forms:
  # ... existing forms ...

  # Parent first
  - form_id: md39vehicleCategory
    csv_file: data/metadata/md39vehicleCategory.csv
    form_definition: data/metadata_forms/md39vehicleCategory.json
    description: "Vehicle categories for subsidy tracking"
    depends_on: []
    record_count: 3

  # Child second (depends on parent)
  - form_id: md39vehicle
    csv_file: null  # Not used - DataAugmentor reads category CSVs
    csv_files:  # Multiple category CSVs
      - data/metadata/md39tractor.csv
      - data/metadata/md39truck.csv
      - data/metadata/md39motorcycle.csv
    form_definition: data/metadata_forms/md39vehicle.json
    description: "Vehicle items (polymorphic table with FK injection)"
    depends_on:
      - md39vehicleCategory  # MUST deploy parent first
    record_count: 9  # 4 tractors + 3 trucks + 2 motorcycles
    pattern: "pattern2"  # Enable FK injection
```

**Important:**
- ✅ Parent listed BEFORE child
- ✅ Child has `depends_on: [md39vehicleCategory]`
- ✅ Child uses `csv_files` (array) for multiple category CSVs
- ✅ `pattern: "pattern2"` triggers DataAugmentor FK injection
- ✅ `record_count` is sum of all category CSV row counts

---

### Step 6: Deploy (Parent First, Then Child)

**Deploy Parent Only:**
```bash
python joget_utility.py --deploy-specific md39vehicleCategory --yes
```

**Expected Output:**
```
Phase 1: Creating Forms
  ✓ md39vehicleCategory (1/1)

Phase 2: Populating Data
  ✓ md39vehicleCategory: 3/3 records posted

✅ Parent deployed successfully
```

**Verify Parent in Database:**
```sql
SELECT c_code, c_name, c_has_subcategory, c_typical_subsidy_percent
FROM app_fd_md39vehicleCategory
ORDER BY c_code;
```

**Expected:**
```
+-----------+-------------------------+-------------------+---------------------------+
| c_code    | c_name                  | c_has_subcategory | c_typical_subsidy_percent |
+-----------+-------------------------+-------------------+---------------------------+
| MOTORCYCLE| Motorcycle              | Yes               | 40                        |
| TRACTOR   | Agricultural Tractor    | Yes               | 60                        |
| TRUCK     | Farm Transport Truck    | Yes               | 50                        |
+-----------+-------------------------+-------------------+---------------------------+
```

**Deploy Child with FK Injection:**
```bash
python joget_utility.py --deploy-specific md39vehicle --yes
```

**Expected Output:**
```
Phase 1: Creating Forms
  ✓ md39vehicle (1/1)

Phase 2: Augmenting Data (FK Injection)
  Reading category CSVs...
    ✓ md39tractor.csv → 4 records (vehicle_category=TRACTOR)
    ✓ md39truck.csv → 3 records (vehicle_category=TRUCK)
    ✓ md39motorcycle.csv → 2 records (vehicle_category=MOTORCYCLE)
  Total records after FK injection: 9

Phase 3: Populating Data
  ✓ md39vehicle: 9/9 records posted

✅ Child deployed successfully
```

---

### Step 7: Verify Deployment

**Check Polymorphic Table Structure:**
```sql
-- Verify all records have FK injected
SELECT
  c_vehicle_category,
  COUNT(*) as count
FROM app_fd_md39vehicle
GROUP BY c_vehicle_category
ORDER BY c_vehicle_category;
```

**Expected:**
```
+--------------------+-------+
| c_vehicle_category | count |
+--------------------+-------+
| MOTORCYCLE         | 2     |
| TRACTOR            | 4     |
| TRUCK              | 3     |
+--------------------+-------+
Total: 9 records
```

**Check Category-Specific Data:**
```sql
-- Tractors (should have engine_size, no load_capacity)
SELECT c_code, c_name, c_engine_size, c_load_capacity
FROM app_fd_md39vehicle
WHERE c_vehicle_category = 'TRACTOR';
```

**Expected:**
```
+-------+----------------------------+--------------+----------------+
| c_code| c_name                     | c_engine_size| c_load_capacity|
+-------+----------------------------+--------------+----------------+
| T100  | Small Farm Tractor (30HP)  | 30HP         | NULL           |
| T200  | Medium Tractor (50HP)      | 50HP         | NULL           |
| T300  | Large Tractor (75HP)       | 75HP         | NULL           |
| T400  | Heavy Duty Tractor (100HP) | 100HP        | NULL           |
+-------+----------------------------+--------------+----------------+
```

```sql
-- Trucks (should have load_capacity)
SELECT c_code, c_name, c_engine_size, c_load_capacity
FROM app_fd_md39vehicle
WHERE c_vehicle_category = 'TRUCK';
```

**Expected:**
```
+-------+----------------------+--------------+----------------+
| c_code| c_name               | c_engine_size| c_load_capacity|
+-------+----------------------+--------------+----------------+
| TR100 | Light Pickup Truck   | 2.5L         | 1 tonne        |
| TR200 | Medium Truck         | 4.0L         | 3 tonnes       |
| TR300 | Heavy Truck          | 6.0L         | 5 tonnes       |
+-------+----------------------+--------------+----------------+
```

**Verify Sparse Column Pattern:**
- ✅ Tractors have NULL `load_capacity` (not applicable)
- ✅ All vehicles have `engine_size` (common field)
- ✅ Each category uses only relevant fields

---

### Step 8: Test Cascading Dropdown

To verify Pattern 2 works correctly, test the cascading dropdown in Joget UI.

**Test Form:** Create a test form that references md39vehicle

```json
{
  "className": "org.joget.apps.form.model.Form",
  "properties": {
    "id": "test_vehicle_selection",
    "name": "Test Vehicle Selection"
  },
  "elements": [
    {
      "className": "org.joget.apps.form.lib.SelectBox",
      "properties": {
        "id": "category",
        "label": "Vehicle Category",
        "options_type": "form",
        "options_form_id": "md39vehicleCategory",
        "options_value_field": "code",
        "options_label_field": "name"
      }
    },
    {
      "className": "org.joget.apps.form.lib.SelectBox",
      "properties": {
        "id": "vehicle",
        "label": "Vehicle",
        "options_type": "form",
        "options_form_id": "md39vehicle",
        "options_value_field": "code",
        "options_label_field": "name",
        "controlField": "category",
        "groupingColumn": "vehicle_category"
      }
    }
  ]
}
```

**Test in Joget UI:**
1. Create test form with above definition
2. Preview form
3. Select "Agricultural Tractor" in Category dropdown
4. Vehicle dropdown should show ONLY tractors:
   ```
   [ ] Small Farm Tractor (30HP)
   [ ] Medium Tractor (50HP)
   [ ] Large Tractor (75HP)
   [ ] Heavy Duty Tractor (100HP)
   ```
5. Change category to "Farm Transport Truck"
6. Vehicle dropdown should update to show ONLY trucks:
   ```
   [ ] Light Pickup Truck
   [ ] Medium Truck
   [ ] Heavy Truck
   ```

**If Cascading Doesn't Work:**
- ✅ Check `vehicle_category` is **SelectBox** (not TextField)
- ✅ Verify FK was injected (query database)
- ✅ Check `controlField` and `groupingColumn` match exactly
- ✅ See Section 3.3 Troubleshooting for more details

---

### Common Issues: Pattern 2

#### Issue 1: FK Not Injected

**Symptoms:**
- Records inserted but `vehicle_category` is NULL
- Cascading dropdown shows all items regardless of category

**Causes:**
1. Missing `pattern: "pattern2"` in deployment config
2. CSV filename doesn't match category mapping
3. relationships.json not loaded correctly

**Solution:**
```bash
# Check relationships.json syntax
python -c "
import json
with open('config/relationships.json') as f:
    data = json.load(f)
    print('Parent forms:', list(data['parent_child_relationships'].keys()))
"

# Verify category mapping
python -c "
import json
with open('config/relationships.json') as f:
    data = json.load(f)
    mappings = data['parent_child_relationships']['md39vehicleCategory']['child_forms'][0]['category_mappings']
    print('Category Mappings:')
    for code, filename in mappings.items():
        print(f'  {code} → {filename}')
"

# Redeploy with debugging
python joget_utility.py --deploy-specific md39vehicle --data-only --yes --debug
```

#### Issue 2: Parent Not Found Error

**Symptoms:**
```
Error: Parent form 'md39vehicleCategory' not found
Cannot create child form 'md39vehicle' without parent
```

**Cause:** Parent not deployed before child

**Solution:**
```bash
# Deploy in correct order
python joget_utility.py --deploy-specific md39vehicleCategory --yes
sleep 5  # Wait for Joget processing
python joget_utility.py --deploy-specific md39vehicle --yes
```

#### Issue 3: Cascading Dropdown Shows Nothing

**Symptoms:**
- Category dropdown works
- Vehicle dropdown is empty (no options)

**Causes:**
1. FK field is TextField (not SelectBox)
2. `groupingColumn` name doesn't match database column
3. Parent-child relationship not configured

**Diagnosis:**
```sql
-- Check FK field values
SELECT DISTINCT c_vehicle_category
FROM app_fd_md39vehicle;
-- Should show: TRACTOR, TRUCK, MOTORCYCLE

-- Check if child records exist for selected category
SELECT c_code, c_name, c_vehicle_category
FROM app_fd_md39vehicle
WHERE c_vehicle_category = 'TRACTOR';
-- Should return tractor records
```

**Solution:**
```json
// In md39vehicle.json, ensure FK is SelectBox
{
  "className": "org.joget.apps.form.lib.SelectBox",
  "properties": {
    "id": "vehicle_category",  // ← Field ID
    "label": "Vehicle Category",
    "options_type": "form",
    "options_form_id": "md39vehicleCategory"
  }
}
```

```json
// In referencing form, ensure groupingColumn matches
{
  "id": "vehicle",
  "controlField": "category",
  "groupingColumn": "vehicle_category"  // ← Must match FK field ID
}
```

---

### Decision Tree: When to Use Polymorphic Tables

```
Start: Do you have a category system?
  ├─ No → Use Pattern 1 (Simple Metadata)
  └─ Yes → Continue

Do categories share 70%+ fields?
  ├─ No → Use separate forms per category
  └─ Yes → Continue

Do you need unified reporting across categories?
  ├─ No → Consider separate forms
  └─ Yes → Continue

Are sparse columns acceptable (NULL values for non-applicable fields)?
  ├─ No → Use separate forms per category
  └─ Yes → ✅ Use Polymorphic Table (Pattern 2)

Examples:
  ✅ Polymorphic: MD27 Input (FERTILIZER, PESTICIDES share most fields)
  ✅ Polymorphic: MD25 Equipment (all equipment types similar structure)
  ❌ Not Polymorphic: Farmers vs Applications (completely different entities)
```

---

## 4.3 Form Generation Reference

The `form_generator.py` utility automates Joget form JSON creation from CSV files. This section documents its usage, customization options, and when manual editing is needed.

### Basic Usage

**Command:**
```bash
python processors/form_generator.py \
  --csv <path-to-csv> \
  --form-id <formId> \
  --form-name <"Display Name"> \
  --output <path-to-output.json>
```

**Example:**
```bash
python processors/form_generator.py \
  --csv data/metadata/md01maritalStatus.csv \
  --form-id md01maritalStatus \
  --form-name "MD.01 - Marital Status" \
  --output data/metadata_forms/md01maritalStatus.json
```

### How Form Generator Works

#### 1. CSV Analysis Phase

Reads CSV file and analyzes:
- **Header row:** Extracts field names
- **Data types:** Infers from first 5 rows
  - All "true"/"false" → Boolean (SelectBox with Yes/No)
  - All numeric → Number field
  - ISO dates (YYYY-MM-DD) → Date field
  - Everything else → Text field
- **Required fields:** `code` and `name` marked required by default
- **Field order:** Preserves CSV column order

**Example CSV:**
```csv
code,name,requires_documentation,max_amount,valid_from
CASH,Cash Payment,false,10000,2024-01-01
BANK,Bank Transfer,true,50000,2024-01-01
```

**Detected Fields:**
- `code` → TextField (required)
- `name` → TextField (required)
- `requires_documentation` → SelectBox (boolean)
- `max_amount` → TextField (numeric detected but stored as text)
- `valid_from` → DatePicker

#### 2. Form Structure Generation

Creates Joget form JSON with:
- **Form properties:** id, name, tableName, description
- **Section:** Single section containing all fields
- **Field elements:** One element per CSV column
- **Validators:** DefaultValidator on required fields

**Generated Structure:**
```json
{
  "className": "org.joget.apps.form.model.Form",
  "properties": {
    "id": "md01maritalStatus",
    "name": "MD.01 - Marital Status",
    "tableName": "md01maritalStatus"
  },
  "elements": [
    {
      "className": "org.joget.apps.form.model.Section",
      "properties": {"label": "Details"},
      "elements": [
        // Field elements here
      ]
    }
  ]
}
```

#### 3. Field Type Mapping

| CSV Data Pattern | Joget Element | Properties |
|-----------------|---------------|------------|
| "true"/"false" | SelectBox | options: [{value:"true",label:"Yes"},{value:"false",label:"No"}] |
| All numbers | TextField | (stored as text, not number type) |
| YYYY-MM-DD dates | DatePicker | format: "yyyy-MM-dd" |
| Text | TextField | Default |
| Column named "description" | TextArea | Multi-line text |

**Current Limitations:**
- ❌ Doesn't detect foreign keys (you must add SelectBox manually)
- ❌ Doesn't detect enums beyond true/false
- ❌ Doesn't add field descriptions
- ❌ Doesn't configure cascading dropdowns
- ✅ Good for simple metadata, requires customization for complex forms

---

### Customization After Generation

Most forms need manual customization after generation. Here's what to customize and when.

#### Adding Foreign Key Fields

**Generated (Simple TextField):**
```json
{
  "className": "org.joget.apps.form.lib.TextField",
  "properties": {
    "id": "equipment_category",
    "label": "Equipment Category"
  }
}
```

**Customized (SelectBox Referencing Parent):**
```json
{
  "className": "org.joget.apps.form.lib.SelectBox",
  "properties": {
    "id": "equipment_category",
    "label": "Equipment Category",
    "required": "true",
    "options_type": "form",
    "options_form_id": "md25equipmentCategory",
    "options_value_field": "code",
    "options_label_field": "name",
    "validator": {
      "className": "org.joget.apps.form.lib.DefaultValidator"
    }
  }
}
```

**When to Use:**
- ✅ Field references another metadata form
- ✅ Pattern 2 parent-child relationships
- ✅ Any dropdown that should pull from database

---

#### Adding Enum SelectBoxes

**Generated (TextField):**
```json
{
  "className": "org.joget.apps.form.lib.TextField",
  "properties": {
    "id": "status",
    "label": "Status"
  }
}
```

**Customized (SelectBox with Fixed Options):**
```json
{
  "className": "org.joget.apps.form.lib.SelectBox",
  "properties": {
    "id": "status",
    "label": "Status",
    "options": [
      {"value": "active", "label": "Active"},
      {"value": "inactive", "label": "Inactive"},
      {"value": "pending", "label": "Pending"}
    ],
    "required": "true"
  }
}
```

**When to Use:**
- ✅ Field has limited set of values
- ✅ Values won't change frequently
- ✅ No need for database table for 3-5 options

---

#### Adding Field Descriptions

**Generated:**
```json
{
  "className": "org.joget.apps.form.lib.TextField",
  "properties": {
    "id": "typical_subsidy_percent",
    "label": "Typical Subsidy Percent"
  }
}
```

**Customized:**
```json
{
  "className": "org.joget.apps.form.lib.TextField",
  "properties": {
    "id": "typical_subsidy_percent",
    "label": "Typical Subsidy %",
    "description": "Default subsidy percentage for this category (0-100)",
    "placeholder": "e.g., 60 for 60%"
  }
}
```

**When to Use:**
- ✅ Field needs explanation for users
- ✅ Field has specific format requirements
- ✅ Examples would be helpful

---

#### Configuring Cascading Dropdowns

**Scenario:** Form has category and item dropdowns, item filters by category.

**Category Field (Parent):**
```json
{
  "className": "org.joget.apps.form.lib.SelectBox",
  "properties": {
    "id": "input_category",
    "label": "Input Category",
    "options_type": "form",
    "options_form_id": "md27inputCategory",
    "options_value_field": "code",
    "options_label_field": "name"
  }
}
```

**Item Field (Child with Cascading):**
```json
{
  "className": "org.joget.apps.form.lib.SelectBox",
  "properties": {
    "id": "input_item",
    "label": "Input Item",
    "options_type": "form",
    "options_form_id": "md27input",
    "options_value_field": "code",
    "options_label_field": "name",
    "controlField": "input_category",
    "groupingColumn": "input_category"
  }
}
```

**Critical:**
- `controlField` → ID of parent dropdown (in same form)
- `groupingColumn` → FK field in child form's table
- Both must match exactly (case-sensitive)

---

### When to Skip Form Generator

**Use Form Generator When:**
- ✅ Simple metadata with 3-10 fields
- ✅ No complex relationships
- ✅ Standard text/boolean fields
- ✅ Quick prototype needed

**Skip Form Generator (Create Manually) When:**
- ❌ Form has complex validation rules
- ❌ Form needs custom JavaScript
- ❌ Form has conditional field visibility
- ❌ Form needs custom layouts (multiple sections, columns)
- ❌ Form has file uploads or special widgets

**Example: Complex Form Requiring Manual Creation**

Form with conditional fields:
- If "has_dependents" = Yes → Show "number_of_dependents" field
- If "payment_method" = Bank → Show "bank_account_number" field
- Complex validation (e.g., phone number format)

For such forms:
1. Generate basic structure with form_generator.py
2. Add conditional visibility with JavaScript
3. Add custom validators
4. Test thoroughly in Joget UI before deployment

---

### Form Generator Options

**Full Command Options:**
```bash
python processors/form_generator.py \
  --csv <path-to-csv>                    # Required: Input CSV file
  --form-id <formId>                     # Required: Joget form ID
  --form-name <"Display Name">           # Required: Form display name
  --output <path-to-output.json>         # Required: Output JSON file
  --description <"Form description">     # Optional: Form description
  --table-name <tableName>               # Optional: Custom table name (defaults to formId)
  --section-label <"Section Title">      # Optional: Section heading (defaults to "Details")
  --required-fields <field1,field2>      # Optional: Comma-separated required fields
```

**Example with All Options:**
```bash
python processors/form_generator.py \
  --csv data/metadata/md38currency.csv \
  --form-id md38currency \
  --form-name "MD.38 - Currency" \
  --output data/metadata_forms/md38currency.json \
  --description "Currency codes for international transactions" \
  --section-label "Currency Information" \
  --required-fields "code,name,symbol"
```

---

### Form Validation After Generation

Before deploying, validate generated form:

**1. JSON Syntax Check:**
```bash
python -c "
import json
with open('data/metadata_forms/md38currency.json') as f:
    form = json.load(f)
    print('✓ Valid JSON')
    print('Form ID:', form['properties']['id'])
    print('Fields:', len(form['elements'][0]['elements']))
"
```

**2. Required Fields Check:**
```bash
python -c "
import json
with open('data/metadata_forms/md38currency.json') as f:
    form = json.load(f)
    fields = form['elements'][0]['elements']
    required = [f['properties']['id'] for f in fields if f['properties'].get('required') == 'true']
    print('Required fields:', required)
"
```

**3. Field Count vs CSV Columns:**
```bash
# CSV columns
head -1 data/metadata/md38currency.csv | tr ',' '\n' | wc -l

# Form fields
python -c "
import json
with open('data/metadata_forms/md38currency.json') as f:
    form = json.load(f)
    print(len(form['elements'][0]['elements']))
"

# Should match
```

---

### Troubleshooting Form Generator

#### Issue: Form Generator Crashes

**Symptoms:**
```
Error: Cannot read CSV file
```

**Solution:**
```bash
# Check file exists
ls -l data/metadata/md38currency.csv

# Check CSV syntax
python -c "
import csv
with open('data/metadata/md38currency.csv') as f:
    reader = csv.DictReader(f)
    print('Headers:', reader.fieldnames)
    for i, row in enumerate(reader):
        if i < 2:
            print(f'Row {i}:', row)
"
```

#### Issue: Wrong Field Types Generated

**Symptoms:**
- Boolean field generated as TextField
- Date field generated as TextField

**Cause:** CSV data doesn't match expected patterns

**Solution:**
```bash
# Check data patterns
python -c "
import csv
with open('data/metadata/md38currency.csv') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    for field in reader.fieldnames:
        values = [row[field] for row in rows[:5]]
        print(f'{field}: {values}')
"
```

Fix CSV data or manually edit generated JSON.

#### Issue: Missing Required Validators

**Solution:** Manually add validators:
```json
{
  "id": "code",
  "required": "true",
  "validator": {
    "className": "org.joget.apps.form.lib.DefaultValidator",
    "properties": {
      "message": "Code is required"
    }
  }
}
```

---

### Quick Reference: Form Generator Workflow

**Standard Workflow:**
1. Create CSV with data
2. Generate form: `python processors/form_generator.py ...`
3. Review generated JSON
4. Customize:
   - Add FK SelectBoxes for parent references
   - Add field descriptions
   - Add custom validators
   - Configure cascading if needed
5. Validate JSON syntax
6. Add to deployment config
7. Deploy and test

**Time Estimate:**
- CSV creation: 10 minutes
- Form generation: 2 minutes
- Customization: 10-20 minutes (depending on complexity)
- **Total: 25-35 minutes**

---

**End of Part 4: How to Add New Metadata**

**Next:** Part 5 - Deployment Guide (Scenarios, troubleshooting, and best practices)

---

# Part 5: Deployment Guide

## Overview

This section covers deploying metadata forms and data to Joget DX instances. Whether you're deploying to local development, staging, or production environments, these guides will help you execute successful deployments.

**What You'll Learn:**
- Deployment scenarios (full, selective, incremental)
- Environment-specific configuration
- Command reference and options
- Troubleshooting deployment failures
- Production deployment best practices
- Verification and rollback procedures

**Key Principle:** *Never assume success - always verify*

---

## 5.1 Environment Configuration

Before deploying, ensure your environment is properly configured.

### Directory Structure

```
joget_utility/
├── config/
│   ├── master_data_deploy.yaml     # Deployment configuration
│   └── relationships.json          # FK injection mappings
├── data/
│   ├── metadata/                   # CSV data files
│   └── metadata_forms/             # JSON form definitions
├── processors/
│   ├── data_augmentor.py          # FK injection processor
│   └── master_data_deployer.py    # Deployment orchestrator
├── .env.3                          # Production environment
├── .env.8                          # Development environment
└── joget_utility.py               # Main CLI
```

### Environment Files

The system supports multiple environments using different `.env` files.

#### Development Environment (.env.8)

```bash
# Joget DX 8 - Local Development
JOGET_BASE_URL=http://localhost:8080/jw
JOGET_API_ID=your_api_id
JOGET_API_KEY=your_api_key

# Database (optional - for verification)
DB_HOST=localhost
DB_PORT=3308
DB_NAME=jwdb
DB_USER=root
DB_PASSWORD=your_password
```

#### Production Environment (.env.3)

```bash
# Joget DX - Production
JOGET_BASE_URL=https://production-server.com/jw
JOGET_API_ID=production_api_id
JOGET_API_KEY=production_api_key

# Database
DB_HOST=production-db-host
DB_PORT=3306
DB_NAME=jwdb
DB_USER=joget_user
DB_PASSWORD=secure_password
```

### Switching Environments

**Load specific environment:**
```python
# In joget_utility.py
from dotenv import load_dotenv
from pathlib import Path

# Load production environment
load_dotenv(Path(__file__).parent / '.env.3', override=True)

# Or load development environment
load_dotenv(Path(__file__).parent / '.env.8', override=True)
```

**Command-line environment selection:**
```bash
# Deploy to development (default .env.8)
python joget_utility.py --deploy-master-data --yes

# Deploy to production (specify .env.3)
python joget_utility.py --deploy-master-data --env production --yes
```

---

## 5.2 Command Reference

The `joget_utility.py` script provides several deployment commands.

### Full Deployment

Deploy all metadata forms and data.

```bash
python joget_utility.py --deploy-master-data --yes
```

**What it does:**
1. Creates all 37 forms via FormCreator API
2. Verifies API endpoints created
3. Populates data for all forms
4. Displays summary report

**Expected duration:** 2-5 minutes (37 forms, 416 records)

**Output:**
```
Master Data Deployment
======================

Phase 1: Creating Forms (37 forms)
  ✓ md01maritalStatus (1/37)
  ✓ md02language (2/37)
  ...
  ✓ md37collectionPoint (37/37)

Phase 2: Verifying API Endpoints
  ✓ All 37 API endpoints verified

Phase 3: Populating Data
  ✓ md01maritalStatus: 5/5 records
  ✓ md02language: 3/3 records
  ...
  ✓ md37collectionPoint: 10/10 records

Deployment Summary
------------------
Forms created: 37/37 (100%)
Records posted: 416/416 (100%)
Failed records: 0
Duration: 3m 42s

✅ Deployment successful!
```

---

### Selective Deployment

Deploy specific metadata forms only.

```bash
python joget_utility.py --deploy-specific md01maritalStatus md02language --yes
```

**What it does:**
1. Creates only specified forms
2. Verifies their API endpoints
3. Populates data for specified forms only

**Use cases:**
- Adding new metadata forms
- Redeploying forms after changes
- Testing individual forms

**Example with dependencies:**
```bash
# Deploy parent and child together
python joget_utility.py --deploy-specific md25equipmentCategory md25equipment --yes
```

**Important:** Always deploy parent forms before child forms.

---

### Data-Only Deployment

Populate data for existing forms (skip form creation).

```bash
python joget_utility.py --deploy-master-data --data-only --yes
```

**What it does:**
1. Skips form creation phase
2. Populates data for all forms
3. Assumes forms already exist

**Use cases:**
- Updating data after CSV changes
- Repopulating data after clearing tables
- Adding records to existing forms

**Selective data-only:**
```bash
python joget_utility.py --deploy-specific md27input --data-only --yes
```

---

### Forms-Only Deployment

Create forms without populating data.

```bash
python joget_utility.py --deploy-master-data --forms-only --yes
```

**What it does:**
1. Creates all form definitions
2. Verifies API endpoints
3. Skips data population

**Use cases:**
- Pre-creating forms before data is ready
- Testing form definitions
- Separating form creation from data population

---

### Dry-Run Mode

Preview deployment without making changes.

```bash
python joget_utility.py --deploy-master-data --dry-run
```

**What it does:**
1. Validates configuration files
2. Checks CSV files exist
3. Shows what would be deployed
4. Does NOT make any API calls

**Output:**
```
Dry-Run Mode - No changes will be made
========================================

Deployment Plan:
  Forms to create: 37
  Records to insert: 416

Forms:
  1. md01maritalStatus (5 records) ✓
  2. md02language (3 records) ✓
  ...
  37. md37collectionPoint (10 records) ✓

Dependencies:
  md25equipment depends on: md25equipmentCategory ✓
  md27input depends on: md27inputCategory ✓

Validation:
  ✓ All CSV files found
  ✓ All JSON form definitions found
  ✓ No circular dependencies
  ✓ relationships.json valid

Ready to deploy. Run without --dry-run to execute.
```

---

### Verification Mode

Verify existing deployment without redeploying.

```bash
python joget_utility.py --verify-deployment
```

**What it does:**
1. Queries database for all metadata tables
2. Counts records in each table
3. Compares with expected record counts
4. Reports discrepancies

**Output:**
```
Deployment Verification
=======================

Checking 37 metadata forms...

✓ md01maritalStatus: 5/5 records (100%)
✓ md02language: 3/3 records (100%)
✗ md27input: 40/61 records (66%) - MISSING 21 SEEDS records
✓ md37collectionPoint: 10/10 records (100%)

Summary:
  Forms verified: 37/37
  Records verified: 395/416 (95%)
  Missing records: 21
  Forms with issues: 1

Issues:
  ⚠️ md27input missing 21 records (SEEDS category)
     Recommendation: Run --deploy-specific md27input --data-only
```

---

### Command Options Summary

| Option | Description | Example |
|--------|-------------|---------|
| `--deploy-master-data` | Deploy all metadata | `python joget_utility.py --deploy-master-data --yes` |
| `--deploy-specific <forms>` | Deploy specific forms | `python joget_utility.py --deploy-specific md01maritalStatus --yes` |
| `--data-only` | Skip form creation | `python joget_utility.py --deploy-master-data --data-only --yes` |
| `--forms-only` | Skip data population | `python joget_utility.py --deploy-master-data --forms-only --yes` |
| `--dry-run` | Preview without changes | `python joget_utility.py --deploy-master-data --dry-run` |
| `--verify-deployment` | Verify existing data | `python joget_utility.py --verify-deployment` |
| `--yes` | Skip confirmation prompt | Required for non-interactive execution |
| `--env <env>` | Specify environment | `python joget_utility.py --deploy-master-data --env production --yes` |
| `--debug` | Enable debug logging | `python joget_utility.py --deploy-master-data --debug --yes` |

---

## 5.3 Deployment Scenarios

Common deployment scenarios with step-by-step instructions.

### Scenario 1: Initial Deployment (Fresh Instance)

**Goal:** Deploy all metadata to a new Joget instance.

**Prerequisites:**
- Joget DX instance running
- API credentials configured in `.env` file
- Database accessible

**Steps:**

1. **Verify environment:**
```bash
# Test connection
python joget_utility.py --test-connection

# Expected output:
# ✓ Joget API accessible
# ✓ Database accessible
```

2. **Dry-run to preview:**
```bash
python joget_utility.py --deploy-master-data --dry-run
```

3. **Deploy all metadata:**
```bash
python joget_utility.py --deploy-master-data --yes
```

4. **Verify deployment:**
```bash
python joget_utility.py --verify-deployment
```

5. **Manual spot checks:**
```sql
-- Check form count
SELECT COUNT(*) FROM app_form WHERE id LIKE 'md%';
-- Expected: 37

-- Check total records
SELECT
  TABLE_NAME,
  TABLE_ROWS
FROM information_schema.TABLES
WHERE TABLE_NAME LIKE 'app_fd_md%'
ORDER BY TABLE_NAME;
-- Expected: 37 tables with 416 total records
```

**Expected Duration:** 3-5 minutes

---

### Scenario 2: Adding New Metadata Form

**Goal:** Deploy a new md38currency form to existing deployment.

**Steps:**

1. **Create CSV and form definition** (see Part 4.1)

2. **Add to deployment config:**
Edit `config/master_data_deploy.yaml`:
```yaml
metadata_forms:
  # ... existing forms ...
  - form_id: md38currency
    csv_file: data/metadata/md38currency.csv
    form_definition: data/metadata_forms/md38currency.json
    description: "Currency codes"
    depends_on: []
    record_count: 5
```

3. **Deploy new form only:**
```bash
python joget_utility.py --deploy-specific md38currency --yes
```

4. **Verify:**
```sql
SELECT COUNT(*) FROM app_fd_md38currency;
-- Expected: 5
```

**Expected Duration:** 30 seconds - 1 minute

---

### Scenario 3: Updating Existing Data

**Goal:** Update CSV data and repopulate database.

**Steps:**

1. **Update CSV file:**
Edit `data/metadata/md01maritalStatus.csv`:
```csv
code,name
single,Single
married,Married
divorced,Divorced
widowed,Widowed
separated,Separated  # ← New record
```

2. **Update record count in config:**
Edit `config/master_data_deploy.yaml`:
```yaml
- form_id: md01maritalStatus
  record_count: 5  # Changed from 4
```

3. **Clear existing data** (optional but recommended):
```sql
DELETE FROM app_fd_md01maritalStatus;
```

4. **Repopulate data:**
```bash
python joget_utility.py --deploy-specific md01maritalStatus --data-only --yes
```

5. **Verify:**
```sql
SELECT * FROM app_fd_md01maritalStatus ORDER BY c_code;
-- Expected: 5 records including 'separated'
```

**Alternative: Without clearing data** (appends new records):
- Skip step 3
- Run step 4
- Result: Old records remain, new records added
- **Warning:** May create duplicates if code values overlap

---

### Scenario 4: Deploying Parent-Child Hierarchy

**Goal:** Deploy md39vehicleCategory + md39vehicle (Pattern 2).

**Prerequisites:**
- Parent CSV created: `md39vehicleCategory.csv`
- Child CSVs created: `md39tractor.csv`, `md39truck.csv`, `md39motorcycle.csv`
- Forms generated with FK SelectBox
- `relationships.json` configured

**Steps:**

1. **Deploy parent first:**
```bash
python joget_utility.py --deploy-specific md39vehicleCategory --yes
```

2. **Wait for Joget processing:**
```bash
sleep 5
```

3. **Verify parent deployed:**
```sql
SELECT COUNT(*) FROM app_fd_md39vehicleCategory;
-- Expected: 3
```

4. **Deploy child with FK injection:**
```bash
python joget_utility.py --deploy-specific md39vehicle --yes
```

5. **Verify FK injection worked:**
```sql
SELECT
  c_vehicle_category,
  COUNT(*) as count
FROM app_fd_md39vehicle
GROUP BY c_vehicle_category;

-- Expected:
-- TRACTOR     | 4
-- TRUCK       | 3
-- MOTORCYCLE  | 2
```

6. **Test cascading dropdown** in Joget UI (see Part 4.2 Step 8)

**Expected Duration:** 1-2 minutes

---

### Scenario 5: Production Deployment

**Goal:** Deploy to production environment with safety checks.

**Prerequisites:**
- All metadata tested in development
- Stakeholders notified
- Maintenance window scheduled
- Rollback plan documented

**Steps:**

1. **Switch to production environment:**
Edit `joget_utility.py` to load `.env.3`:
```python
load_dotenv(Path(__file__).parent / '.env.3', override=True)
```

2. **Backup production database:**
```bash
mysqldump -h production-db-host -u joget_user -p jwdb > backup_pre_deployment.sql
```

3. **Dry-run on production:**
```bash
python joget_utility.py --deploy-master-data --dry-run
```

4. **Deploy during maintenance window:**
```bash
# Start deployment
python joget_utility.py --deploy-master-data --yes 2>&1 | tee deployment_log.txt
```

5. **Monitor in real-time:**
Watch `deployment_log.txt` for errors.

6. **Verify deployment:**
```bash
python joget_utility.py --verify-deployment 2>&1 | tee verification_log.txt
```

7. **Manual smoke tests:**
- Open Joget UI
- Check 5-10 metadata forms load correctly
- Test cascading dropdowns work
- Verify data displays in SelectBoxes

8. **Notify stakeholders:**
Send deployment summary with verification results.

**Rollback procedure** (if deployment fails):
```bash
# Drop all metadata tables
mysql -h production-db-host -u joget_user -p jwdb < drop_metadata_tables.sql

# Restore from backup
mysql -h production-db-host -u joget_user -p jwdb < backup_pre_deployment.sql
```

**Expected Duration:** 10-15 minutes (including verification)

---

## 5.4 Troubleshooting

Common deployment issues and solutions.

### Issue 1: Form Created But No Data Populated

**Symptoms:**
```
Phase 1: Creating Forms
  ✓ md01maritalStatus (1/37)

Phase 3: Populating Data
  ✗ md01maritalStatus: 0/5 records posted
  Error: Validation failed
```

**Possible Causes:**

#### Cause 1: CSV Encoding Issue

**Diagnosis:**
```bash
file -I data/metadata/md01maritalStatus.csv
# Bad: charset=iso-8859-1
# Good: charset=utf-8
```

**Solution:**
```bash
# Convert to UTF-8
iconv -f ISO-8859-1 -t UTF-8 data/metadata/md01maritalStatus.csv > temp.csv
mv temp.csv data/metadata/md01maritalStatus.csv

# Redeploy data
python joget_utility.py --deploy-specific md01maritalStatus --data-only --yes
```

#### Cause 2: Field Name Mismatch

**Diagnosis:**
```bash
# Check CSV headers
head -1 data/metadata/md01maritalStatus.csv
# Output: code,name

# Check form definition
python -c "
import json
with open('data/metadata_forms/md01maritalStatus.json') as f:
    form = json.load(f)
    fields = form['elements'][0]['elements']
    print([f['properties']['id'] for f in fields])
"
# Output: ['code', 'name']  ← Must match CSV headers
```

**Solution:**
Ensure CSV headers exactly match form field IDs (case-sensitive).

#### Cause 3: Required Field Missing Data

**Diagnosis:**
Check deployment logs for validation errors:
```
Error: "code": "Missing required value"
```

**Solution:**
```bash
# Find rows with empty required fields
python -c "
import csv
with open('data/metadata/md01maritalStatus.csv') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader, 1):
        if not row.get('code') or not row.get('name'):
            print(f'Row {i} missing required field: {row}')
"
```

Fix CSV data and redeploy.

---

### Issue 2: FK Not Injected (Pattern 2)

**Symptoms:**
```sql
SELECT c_vehicle_category FROM app_fd_md39vehicle LIMIT 5;
-- Result: All NULL
```

**Possible Causes:**

#### Cause 1: Missing pattern: "pattern2" in Config

**Diagnosis:**
```bash
grep -A5 "md39vehicle" config/master_data_deploy.yaml
```

**Expected:**
```yaml
- form_id: md39vehicle
  pattern: "pattern2"  # ← Must be present
```

**Solution:**
Add `pattern: "pattern2"` to deployment config and redeploy.

#### Cause 2: CSV Filename Doesn't Match Mapping

**Diagnosis:**
Check `config/relationships.json`:
```json
{
  "md39vehicleCategory": {
    "child_forms": [{
      "category_mappings": {
        "TRACTOR": "md39tractor.csv",  # ← Filename must match exactly
        "TRUCK": "md39truck.csv",
        "MOTORCYCLE": "md39motorcycle.csv"
      }
    }]
  }
}
```

Check actual filenames:
```bash
ls data/metadata/ | grep md39
# Output:
# md39vehicleCategory.csv
# md39tractor.csv      ✓
# md39Truck.csv        ✗ (wrong case - should be md39truck.csv)
# md39motorcycle.csv   ✓
```

**Solution:**
Rename files to match mappings exactly (case-sensitive).

#### Cause 3: DataAugmentor Not Running

**Diagnosis:**
Check deployment logs for FK injection phase:
```
Phase 2: Augmenting Data (FK Injection)
  Reading category CSVs...
    ✓ md39tractor.csv → 4 records (vehicle_category=TRACTOR)
```

If this phase is missing, DataAugmentor didn't run.

**Solution:**
Ensure `pattern: "pattern2"` is set in deployment config.

---

### Issue 3: Cascading Dropdown Shows All Items

**Symptoms:**
- Category dropdown works
- Item dropdown shows ALL items (not filtered by category)

**Possible Causes:**

#### Cause 1: FK Field is TextField (Not SelectBox)

**Diagnosis:**
Check form definition:
```bash
python -c "
import json
with open('data/metadata_forms/md39vehicle.json') as f:
    form = json.load(f)
    fields = form['elements'][0]['elements']
    fk_field = [f for f in fields if f['properties']['id'] == 'vehicle_category'][0]
    print('ClassName:', fk_field['className'])
"
# Bad: org.joget.apps.form.lib.TextField
# Good: org.joget.apps.form.lib.SelectBox
```

**Solution:**
Change FK field to SelectBox in form definition (see Part 4.2 Step 3).

#### Cause 2: groupingColumn Doesn't Match FK Field

**Diagnosis:**
In referencing form, check:
```json
{
  "id": "vehicle",
  "controlField": "category",
  "groupingColumn": "vehicle_category"  // ← Must match FK field ID exactly
}
```

Verify FK field ID:
```sql
DESCRIBE app_fd_md39vehicle;
-- Look for column: c_vehicle_category
```

**Solution:**
Ensure `groupingColumn` matches database column name (without `c_` prefix).

---

### Issue 4: API Endpoint Not Found

**Symptoms:**
```
Phase 2: Verifying API Endpoints
  ✗ md38currency: API endpoint not found
```

**Possible Causes:**

#### Cause 1: Form Creation Didn't Complete

**Diagnosis:**
```sql
SELECT id, name FROM app_form WHERE id = 'md38currency';
-- Empty result = form not created
```

**Solution:**
Redeploy form:
```bash
python joget_utility.py --deploy-specific md38currency --forms-only --yes
```

#### Cause 2: Joget Still Processing

**Diagnosis:**
Form was just created, API endpoint not yet registered.

**Solution:**
Wait 5-10 seconds and retry:
```bash
sleep 10
python joget_utility.py --deploy-specific md38currency --data-only --yes
```

#### Cause 3: FormCreator Plugin Issue

**Diagnosis:**
Check Joget logs (`catalina.out`):
```bash
tail -100 /path/to/joget/apache-tomcat/logs/catalina.out | grep -i error
```

**Solution:**
- Restart Joget
- Rebuild and redeploy FormCreator plugin
- Manually create form via Joget UI to test

---

### Issue 5: Transient Deployment Failures

**Symptoms:**
- Deployment fails randomly
- Same form succeeds on retry
- Error messages don't match actual state

**Example:**
```
✗ md27inputCategory: 0/8 records posted
  Error: "input_category_code": "Missing required value"

# But form definition has NO such field!
```

**Background:**
See `KNOWN_ISSUES.md` - ~5% of deployments experience transient failures that resolve on immediate retry.

**Solution:**

**Automatic Retry** (recommended):
Add retry logic to deployment code:
```python
def deploy_with_retry(form_id, max_attempts=3):
    for attempt in range(max_attempts):
        result = deploy_form(form_id)
        if result['success']:
            return result
        if attempt < max_attempts - 1:
            delay = 2 ** attempt  # Exponential backoff
            logger.warning(f"Retry {attempt+1}/{max_attempts} after {delay}s...")
            time.sleep(delay)
    return result
```

**Manual Retry:**
```bash
# First attempt failed
python joget_utility.py --deploy-specific md27inputCategory --yes

# Immediate retry (usually succeeds)
python joget_utility.py --deploy-specific md27inputCategory --data-only --yes
```

**Prevention:**
Add delays between operations:
```python
# After form creation
time.sleep(2)

# Before data population
time.sleep(1)
```

---

## 5.5 Best Practices

### 1. Always Use Dry-Run First

```bash
# Preview before executing
python joget_utility.py --deploy-master-data --dry-run

# If validation passes, execute
python joget_utility.py --deploy-master-data --yes
```

**Why:** Catches configuration errors before making changes.

---

### 2. Deploy Parent Forms Before Children

**Bad:**
```bash
# Will fail - parent doesn't exist yet
python joget_utility.py --deploy-specific md25equipment --yes
```

**Good:**
```bash
# Deploy parent first
python joget_utility.py --deploy-specific md25equipmentCategory --yes

# Wait for processing
sleep 5

# Then deploy child
python joget_utility.py --deploy-specific md25equipment --yes
```

---

### 3. Verify After Every Deployment

```bash
# Deploy
python joget_utility.py --deploy-master-data --yes

# Verify immediately
python joget_utility.py --verify-deployment
```

**Don't assume success based on exit code alone.**

---

### 4. Log All Deployments

```bash
# Capture full output
python joget_utility.py --deploy-master-data --yes 2>&1 | tee deployment_$(date +%Y%m%d_%H%M%S).log
```

**Benefits:**
- Debugging transient failures
- Audit trail for compliance
- Performance analysis (timing)

---

### 5. Backup Before Production Deployments

```bash
# Full database backup
mysqldump -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME > backup_$(date +%Y%m%d_%H%M%S).sql

# Metadata tables only
mysqldump -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME \
  $(mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD -Nse \
    "SELECT TABLE_NAME FROM information_schema.TABLES \
     WHERE TABLE_SCHEMA='$DB_NAME' AND TABLE_NAME LIKE 'app_fd_md%'" | tr '\n' ' ') \
  > metadata_backup_$(date +%Y%m%d_%H%M%S).sql
```

---

### 6. Use Incremental Deployments

**Bad:**
```bash
# Redeploy everything for one change
python joget_utility.py --deploy-master-data --yes
```

**Good:**
```bash
# Deploy only what changed
python joget_utility.py --deploy-specific md27input --data-only --yes
```

**Benefits:**
- Faster deployments
- Less risk (smaller change surface)
- Easier rollback

---

### 7. Test Locally Before Deploying to Production

**Workflow:**
1. Deploy to local development (`.env.8`)
2. Test all forms and data
3. Deploy to staging (`.env.staging`)
4. Run integration tests
5. Deploy to production (`.env.3`)
6. Verify and monitor

---

## 5.6 Production Deployment Checklist

Use this checklist for production deployments.

### Pre-Deployment

- [ ] All metadata tested in development environment
- [ ] All metadata tested in staging environment
- [ ] Stakeholders notified of deployment window
- [ ] Maintenance window scheduled
- [ ] Database backup completed
- [ ] Rollback procedure documented
- [ ] Deployment script reviewed
- [ ] Dry-run executed successfully on production
- [ ] Dependencies verified (parent forms before children)

### During Deployment

- [ ] Load production environment (`.env.3`)
- [ ] Start deployment with logging enabled
- [ ] Monitor deployment logs in real-time
- [ ] Note any warnings or retries
- [ ] Capture full output to log file
- [ ] Verify each phase completes (forms, API, data)

### Post-Deployment

- [ ] Run verification script
- [ ] Check all metadata tables exist
- [ ] Verify record counts match expected
- [ ] Test 5-10 forms in Joget UI
- [ ] Test cascading dropdowns work
- [ ] Test SelectBox options populate correctly
- [ ] Check for any error logs in Joget
- [ ] Notify stakeholders of completion
- [ ] Document any issues encountered
- [ ] Archive deployment logs

### Rollback Triggers

Rollback if ANY of these occur:
- [ ] More than 10% of forms failed to create
- [ ] More than 5% of records failed to insert
- [ ] Cascading dropdowns not working
- [ ] Critical metadata form (md27input, md25equipment) failed
- [ ] Database connection lost during deployment
- [ ] Joget instance becomes unresponsive

### Rollback Procedure

If rollback is needed:

1. **Stop any ongoing deployments**
```bash
# Ctrl+C to stop current deployment
```

2. **Drop metadata tables**
```sql
-- Generate drop statements
SELECT CONCAT('DROP TABLE IF EXISTS ', TABLE_NAME, ';')
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'jwdb' AND TABLE_NAME LIKE 'app_fd_md%';

-- Execute drop statements
```

3. **Restore from backup**
```bash
mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME < metadata_backup_<timestamp>.sql
```

4. **Verify restoration**
```bash
python joget_utility.py --verify-deployment
```

5. **Notify stakeholders**
Inform of rollback and revised deployment schedule.

---

## 5.7 Deployment Timing Considerations

### Recommended Delays

```yaml
# config/master_data_deploy.yaml
timing:
  api_call_delay: 0.5         # Between each API call (seconds)
  form_creation_delay: 2.0    # After creating form
  data_population_delay: 1.0  # Before populating data
  retry_backoff_base: 2       # Exponential backoff (1s, 2s, 4s)
```

**Why delays matter:**
- Joget processes forms asynchronously
- API endpoints registered after form creation
- Database tables created lazily (on first access)
- Cache invalidation takes time

**Symptoms of insufficient delays:**
- "API endpoint not found" errors
- "Table doesn't exist" errors
- Transient validation failures

**Solution:** Increase delays or add retry logic.

---

## 5.8 Performance Optimization

### Parallel Deployment (Advanced)

For large deployments (100+ forms), consider parallel deployment:

```python
from concurrent.futures import ThreadPoolExecutor

def deploy_independent_forms_parallel(forms, max_workers=5):
    """Deploy forms with no dependencies in parallel."""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(deploy_form, form) for form in forms]
        results = [f.result() for f in futures]
    return results
```

**Caution:**
- Only deploy independent forms in parallel
- Never deploy parent-child in parallel
- Monitor Joget server load
- Reduce `max_workers` if server struggles

---

## 5.9 Monitoring and Alerts

### Deployment Metrics to Track

1. **Success Rate**
   - Forms created: X/Y (%)
   - Records inserted: X/Y (%)
   - API endpoints verified: X/Y (%)

2. **Timing**
   - Total deployment duration
   - Average time per form
   - Average time per record

3. **Failures**
   - Number of retries needed
   - Forms requiring manual intervention
   - Transient vs permanent failures

### Example Monitoring Dashboard

```
Deployment: master_data_deploy_20251027_140523
Status: IN PROGRESS

Progress: ████████░░ 80%

Forms:     30/37 (81%)
Records:   332/416 (80%)
Failures:  2 (retrying...)
Duration:  2m 45s
ETA:       1m 15s

Recent:
  ✓ md30targetGroup: 10/10 records
  ✗ md27inputCategory: 0/8 records (retry 1/3)
  ✓ md31decisionType: 5/5 records
```

---

**End of Part 5: Deployment Guide**

**Next:** Part 6 - Data Maintenance (Updating metadata, data quality, and lifecycle management)

---

# Part 6: Data Maintenance

## Overview

This section covers maintaining metadata after initial deployment. As your application evolves, you'll need to update existing metadata, add new records, ensure data quality, and manage the metadata lifecycle.

**What You'll Learn:**
- How to update existing metadata records
- How to add new records without redeploying
- Data quality guidelines and validation
- Metadata versioning and change tracking
- Archive and deprecation strategies
- Backup and recovery procedures

---

## 6.1 Updating Existing Metadata

### Approach 1: Update CSV and Redeploy (Recommended)

**When to use:** Making changes to multiple records or structural changes.

**Process:**

1. **Update CSV file:**
```csv
# data/metadata/md01maritalStatus.csv
code,name
single,Single
married,Married
divorced,Divorced
widowed,Widowed
separated,Separated  # ← Added
common_law,Common Law  # ← Added
```

2. **Update record count:**
```yaml
# config/master_data_deploy.yaml
- form_id: md01maritalStatus
  record_count: 6  # Updated from 4
```

3. **Clear existing data:**
```sql
DELETE FROM app_fd_md01maritalStatus;
```

4. **Redeploy data:**
```bash
python joget_utility.py --deploy-specific md01maritalStatus --data-only --yes
```

5. **Verify:**
```sql
SELECT COUNT(*) FROM app_fd_md01maritalStatus;
-- Expected: 6
```

**Advantages:**
- ✅ Source of truth remains in version control (CSV file)
- ✅ Repeatable and auditable
- ✅ Easy to rollback (restore from backup)

**Disadvantages:**
- ❌ Requires clearing existing data (brief downtime)
- ❌ Need to redeploy entire form

---

### Approach 2: Direct Database Update

**When to use:** Quick fixes, single record changes, emergency updates.

**Process:**

1. **Find record to update:**
```sql
SELECT * FROM app_fd_md01maritalStatus WHERE c_code = 'single';
```

2. **Update record:**
```sql
UPDATE app_fd_md01maritalStatus
SET c_name = 'Single / Never Married'
WHERE c_code = 'single';
```

3. **Verify:**
```sql
SELECT c_code, c_name FROM app_fd_md01maritalStatus WHERE c_code = 'single';
-- Expected: single | Single / Never Married
```

4. **Update CSV to match** (important!):
```csv
# data/metadata/md01maritalStatus.csv
code,name
single,Single / Never Married  # ← Updated to match database
married,Married
...
```

**Advantages:**
- ✅ Immediate (no deployment required)
- ✅ No downtime
- ✅ Surgical precision (update one record)

**Disadvantages:**
- ❌ CSV file becomes out of sync if not updated
- ❌ No audit trail unless logged
- ❌ Can't be version controlled (unless CSV updated)

**Best Practice:** Always update CSV file after direct database changes to keep them in sync.

---

### Approach 3: Update via Joget UI

**When to use:** Business users need to update metadata without developer access.

**Process:**

1. **Navigate to form:**
```
http://localhost:8080/jw/web/console/app/subsidyApplication/1/datalist/md01maritalStatus
```

2. **Edit record:**
- Click on record
- Modify fields
- Save

3. **Export updated data:**
```
Actions → Export → CSV
```

4. **Update CSV file in repository:**
```bash
cp ~/Downloads/md01maritalStatus_export.csv data/metadata/md01maritalStatus.csv
```

5. **Commit to version control:**
```bash
git add data/metadata/md01maritalStatus.csv
git commit -m "Update marital status metadata from Joget UI"
```

**Advantages:**
- ✅ Non-technical users can update
- ✅ Joget UI provides validation
- ✅ No SQL knowledge required

**Disadvantages:**
- ❌ Manual export/import to sync with CSV
- ❌ Risk of CSV getting out of sync
- ❌ No automatic version control

---

## 6.2 Adding New Records

### Adding Records to Simple Metadata

**Example:** Add new language to md02language

**Via CSV (Recommended):**

1. **Add to CSV:**
```csv
# data/metadata/md02language.csv
code,name
en,English
fr,French
pt,Portuguese  # ← Added
```

2. **Update config:**
```yaml
- form_id: md02language
  record_count: 3  # Updated from 2
```

3. **Redeploy:**
```bash
python joget_utility.py --deploy-specific md02language --data-only --yes
```

**Via SQL (Quick add):**

```sql
INSERT INTO app_fd_md02language (c_code, c_name)
VALUES ('pt', 'Portuguese');
```

**Don't forget to update CSV!**

---

### Adding Records to Polymorphic Tables (Pattern 2)

**Example:** Add new tractor to md39vehicle

**Via Category CSV (Recommended):**

1. **Add to category CSV:**
```csv
# data/metadata/md39tractor.csv
code,name,engine_size,fuel_type,load_capacity
T100,Small Farm Tractor (30HP),30HP,Diesel,
T200,Medium Tractor (50HP),50HP,Diesel,
T300,Large Tractor (75HP),75HP,Diesel,
T400,Heavy Duty Tractor (100HP),100HP,Diesel,
T500,Extra Heavy Tractor (150HP),150HP,Diesel,  # ← Added
```

2. **Update record count:**
```yaml
- form_id: md39vehicle
  record_count: 10  # Updated from 9 (5 tractors now)
```

3. **Redeploy with FK injection:**
```bash
python joget_utility.py --deploy-specific md39vehicle --data-only --yes
```

4. **Verify FK was injected:**
```sql
SELECT c_code, c_name, c_vehicle_category
FROM app_fd_md39vehicle
WHERE c_code = 'T500';

-- Expected:
-- T500 | Extra Heavy Tractor (150HP) | TRACTOR
```

**Via SQL (Manual FK injection):**

```sql
INSERT INTO app_fd_md39vehicle (
  c_code,
  c_name,
  c_vehicle_category,  -- ← Must manually specify FK
  c_engine_size,
  c_fuel_type
)
VALUES (
  'T500',
  'Extra Heavy Tractor (150HP)',
  'TRACTOR',  -- ← FK value
  '150HP',
  'Diesel'
);
```

**Important:** When adding via SQL, you must manually inject the FK. CSV deployment does this automatically.

---

## 6.3 Data Quality Guidelines

### Naming Conventions

**Codes (Primary Keys):**
- ✅ Uppercase: `TRACTOR`, `USD`, `MARRIED`
- ✅ Underscores for multi-word: `COMMON_LAW`, `FARM_TRUCK`
- ✅ No spaces: `PESTICIDES` (not `PEST ICIDES`)
- ✅ Consistent length: All currency codes 3 chars (USD, EUR, GBP)
- ❌ Avoid: Special characters (@, #, $), spaces, lowercase

**Names (Display Labels):**
- ✅ Title Case: `Agricultural Tractor`, `United States Dollar`
- ✅ Full words: `Fertilizer` (not `Fert.`)
- ✅ Descriptive: `Small Farm Tractor (30HP)` includes specification
- ❌ Avoid: ALL CAPS, abbreviations without context

**Example:**
```csv
code,name
TRACTOR,Agricultural Tractor  ✓
tractor,agricultural tractor  ✗ (lowercase code)
TRCT,Tractor                  ✗ (unclear abbreviation)
FARM_TRACTOR,Farm Tractor      ✓
```

---

### Data Validation Rules

#### Required Fields
All metadata forms should have:
- `code` - Required, unique, primary key
- `name` - Required, display label

**Validation:**
```sql
-- Find records missing required fields
SELECT 'md01maritalStatus' as form, *
FROM app_fd_md01maritalStatus
WHERE c_code IS NULL OR c_code = ''
   OR c_name IS NULL OR c_name = '';
```

#### Uniqueness
Codes must be unique within each form.

**Validation:**
```sql
-- Find duplicate codes
SELECT c_code, COUNT(*) as count
FROM app_fd_md01maritalStatus
GROUP BY c_code
HAVING COUNT(*) > 1;
```

**Prevention:**
Add unique constraint:
```sql
ALTER TABLE app_fd_md01maritalStatus
ADD UNIQUE INDEX idx_unique_code (c_code);
```

#### Referential Integrity
Foreign keys must reference existing parent records.

**Validation:**
```sql
-- Find orphaned child records (FK doesn't exist in parent)
SELECT v.*
FROM app_fd_md39vehicle v
LEFT JOIN app_fd_md39vehicleCategory c
  ON v.c_vehicle_category = c.c_code
WHERE c.c_code IS NULL;
```

**Prevention:** Deploy parent forms before children (see Part 5.5).

---

### Data Consistency Checks

#### Consistent Formatting

**Example: Currency symbols**
```csv
code,name,symbol
USD,United States Dollar,$    ✓
EUR,Euro,€                    ✓
GBP,British Pound,£           ✓
JPY,Japanese Yen,¥            ✓
```

All symbols should be single Unicode characters, not multi-char strings.

**Validation:**
```sql
-- Check symbol length
SELECT c_code, c_symbol, LENGTH(c_symbol) as len
FROM app_fd_md38currency
WHERE LENGTH(c_symbol) > 1;
```

#### Consistent Units

**Example: Equipment specifications**
```csv
code,name,engine_size
T100,Small Tractor,30HP      ✓
T200,Medium Tractor,50HP     ✓
T300,Large Tractor,75 HP     ✗ (inconsistent spacing)
T400,Heavy Tractor,100 hp    ✗ (lowercase)
```

**Validation:**
```sql
-- Find inconsistent HP notation
SELECT c_code, c_engine_size
FROM app_fd_md39vehicle
WHERE c_engine_size LIKE '%HP%'
  AND c_engine_size NOT REGEXP '^[0-9]+HP$';
```

---

## 6.4 Metadata Versioning

### Version Control Strategy

**All metadata CSVs should be in Git:**

```bash
git add data/metadata/md01maritalStatus.csv
git commit -m "Add 'separated' marital status option

- Added new option for separated individuals
- Updated record count in deployment config
- Deployed to development environment successfully
"
```

**Commit message format:**
```
<action> <metadata form>: <brief description>

- Detailed change 1
- Detailed change 2
- Deployment/testing notes
```

**Examples:**
```
Add md38currency: Support for international transactions
Update md27input: Add 5 new fertilizer types
Fix md01maritalStatus: Correct typo in 'widowed' label
Remove md19crops: Merge into md27input as SEEDS category
```

---

### Change Tracking

**Create changelog for major metadata updates:**

```markdown
# METADATA_CHANGELOG.md

## [2025-10-27] md27input - Added SEEDS category

### Changed
- Merged md19crops into md27input as SEEDS category
- Added 21 crop records (maize, sorghum, rice, etc.)
- Updated md27inputCategory to include SEEDS

### Migration
- Records moved from md19crops → md27input
- FK injection: vehicle_category=SEEDS

### Deployment
- Development: 2025-10-27 14:30 ✓
- Staging: 2025-10-27 16:00 ✓
- Production: 2025-10-28 10:00 (scheduled)

### Rollback
- Backup: metadata_backup_20251027_143000.sql
- Script: rollback_md27_seeds.sql

## [2025-10-15] md38currency - Initial implementation

### Added
- New metadata form for currency codes
- 5 initial currencies (USD, EUR, GBP, ZAR, BWP)
- ISO 4217 compliant codes

### Deployment
- Development: 2025-10-15 ✓
- Production: 2025-10-16 ✓
```

---

### Tagging Releases

**Tag production deployments:**

```bash
# After successful production deployment
git tag -a metadata-v1.0 -m "Initial production metadata deployment

- 37 forms deployed
- 416 records loaded
- All verification tests passed
- Deployed: 2025-10-27 10:00 UTC
"

git push origin metadata-v1.0
```

**List tagged versions:**
```bash
git tag -l 'metadata-v*'
# metadata-v1.0
# metadata-v1.1
# metadata-v2.0
```

**Checkout specific version:**
```bash
git checkout metadata-v1.0
```

---

## 6.5 Metadata Lifecycle Management

### Active vs Inactive Records

**Instead of deleting records, mark as inactive:**

**Add `is_active` field:**
```csv
code,name,is_active
single,Single,true
married,Married,true
divorced,Divorced,true
widowed,Widowed,true
common_law,Common Law,false  # ← Deprecated but not deleted
```

**Filter in SelectBox:**
```json
{
  "className": "org.joget.apps.form.lib.SelectBox",
  "properties": {
    "id": "marital_status",
    "options_type": "form",
    "options_form_id": "md01maritalStatus",
    "options_value_field": "code",
    "options_label_field": "name",
    "options_filter": "c_is_active = 'true'"  // ← Only show active
  }
}
```

**Benefits:**
- ✅ Historical records still reference old codes
- ✅ No broken foreign keys
- ✅ Can reactivate if needed
- ✅ Audit trail maintained

---

### Deprecation Process

**Example: Deprecate 'common_law' marital status**

**Step 1: Mark as deprecated**
```sql
UPDATE app_fd_md01maritalStatus
SET c_is_active = 'false',
    c_deprecated_date = '2025-10-27',
    c_replacement_code = 'married'
WHERE c_code = 'common_law';
```

**Step 2: Update CSV**
```csv
code,name,is_active,deprecated_date,replacement_code
common_law,Common Law,false,2025-10-27,married
```

**Step 3: Notify users**
```
DEPRECATION NOTICE: md01maritalStatus

Code: common_law
Status: Deprecated as of 2025-10-27
Replacement: married
Action Required: Update forms using common_law to use married
Timeline: Grace period until 2026-01-01
```

**Step 4: Migration script**
```sql
-- After grace period, migrate existing data
UPDATE app_fd_farmer_profile
SET c_marital_status = 'married'
WHERE c_marital_status = 'common_law';
```

**Step 5: Remove from SelectBox options**
```json
{
  "options_filter": "c_is_active = 'true'"
}
```

---

### Archive Strategy

**When to archive metadata:**
- ✅ No longer used in any active forms
- ✅ All historical references migrated
- ✅ Grace period expired (6+ months)

**Archive process:**

1. **Export to archive:**
```bash
mkdir -p archive/metadata/2025
cp data/metadata/md19crops.csv archive/metadata/2025/md19crops_archived_20251027.csv
```

2. **Document in README:**
```markdown
# archive/metadata/2025/README.md

## md19crops - Archived 2025-10-27

**Reason:** Merged into md27input as SEEDS category

**Original record count:** 21

**Migration:** See MD19_MERGE_NOTES.md

**Backup:** metadata_backup_20251027.sql

**Restore if needed:**
- Extract from backup: metadata_backup_20251027.sql
- Or redeploy from: md19crops_archived_20251027.csv
```

3. **Remove from deployment config:**
```yaml
# config/master_data_deploy.yaml
metadata_forms:
  # - form_id: md19crops  # ← Commented out (archived)
  #   csv_file: data/metadata/md19crops.csv
  #   ...
```

4. **Commit archive:**
```bash
git add archive/metadata/2025/
git commit -m "Archive md19crops metadata

- Merged into md27input as SEEDS category
- 21 records migrated with FK injection
- See MD19_MERGE_NOTES.md for details
"
```

---

## 6.6 Data Quality Monitoring

### Automated Validation Script

**Create validation script:** `scripts/validate_metadata.py`

```python
#!/usr/bin/env python3
"""Validate metadata data quality."""

import csv
from pathlib import Path

def validate_metadata_csv(csv_file):
    """Validate single metadata CSV file."""
    errors = []

    with open(csv_file) as f:
        reader = csv.DictReader(f)

        # Check required columns
        if 'code' not in reader.fieldnames:
            errors.append(f"Missing required column: code")
        if 'name' not in reader.fieldnames:
            errors.append(f"Missing required column: name")

        # Check data quality
        codes_seen = set()
        for row_num, row in enumerate(reader, start=2):  # Start at 2 (after header)
            # Check required fields
            if not row.get('code'):
                errors.append(f"Row {row_num}: Missing code")
            if not row.get('name'):
                errors.append(f"Row {row_num}: Missing name")

            # Check uniqueness
            code = row.get('code')
            if code in codes_seen:
                errors.append(f"Row {row_num}: Duplicate code '{code}'")
            codes_seen.add(code)

            # Check code format (uppercase, no spaces)
            if code and (code != code.upper() or ' ' in code):
                errors.append(f"Row {row_num}: Code '{code}' should be uppercase, no spaces")

    return errors

def validate_all_metadata():
    """Validate all metadata CSV files."""
    metadata_dir = Path('data/metadata')
    total_errors = 0

    for csv_file in sorted(metadata_dir.glob('md*.csv')):
        print(f"\nValidating {csv_file.name}...")
        errors = validate_metadata_csv(csv_file)

        if errors:
            print(f"  ✗ {len(errors)} errors found:")
            for error in errors:
                print(f"    - {error}")
            total_errors += len(errors)
        else:
            print(f"  ✓ Valid")

    print(f"\n{'='*60}")
    if total_errors == 0:
        print("✓ All metadata files valid!")
        return 0
    else:
        print(f"✗ {total_errors} total errors found")
        return 1

if __name__ == '__main__':
    exit(validate_all_metadata())
```

**Run validation:**
```bash
python scripts/validate_metadata.py

Validating md01maritalStatus.csv...
  ✓ Valid

Validating md02language.csv...
  ✗ 2 errors found:
    - Row 3: Code 'pt' should be uppercase, no spaces
    - Row 4: Missing name

Validating md27input.csv...
  ✓ Valid

============================================================
✗ 2 total errors found
```

---

### Database Integrity Checks

**Create database validation script:** `scripts/validate_db_integrity.py`

```python
#!/usr/bin/env python3
"""Validate database metadata integrity."""

import pymysql
from pathlib import Path
import yaml

def load_config():
    """Load deployment configuration."""
    with open('config/master_data_deploy.yaml') as f:
        return yaml.safe_load(f)

def validate_record_counts(cursor, config):
    """Validate record counts match expected."""
    errors = []

    for form in config['metadata_forms']:
        form_id = form['form_id']
        expected_count = form['record_count']
        table_name = f"app_fd_{form_id}"

        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        actual_count = cursor.fetchone()[0]

        if actual_count != expected_count:
            errors.append(
                f"{form_id}: Expected {expected_count} records, "
                f"found {actual_count}"
            )

    return errors

def validate_foreign_keys(cursor):
    """Validate foreign key integrity."""
    errors = []

    # Check md39vehicle → md39vehicleCategory
    cursor.execute("""
        SELECT v.c_code
        FROM app_fd_md39vehicle v
        LEFT JOIN app_fd_md39vehicleCategory c
          ON v.c_vehicle_category = c.c_code
        WHERE c.c_code IS NULL
    """)

    orphaned = cursor.fetchall()
    if orphaned:
        errors.append(
            f"md39vehicle: {len(orphaned)} orphaned records "
            f"(invalid vehicle_category FK)"
        )

    # Add more FK checks as needed...

    return errors

def main():
    """Run all database integrity checks."""
    config = load_config()

    conn = pymysql.connect(
        host='localhost',
        port=3308,
        user='root',
        password='',
        database='jwdb'
    )

    try:
        cursor = conn.cursor()

        print("Checking record counts...")
        errors = validate_record_counts(cursor, config)

        print("Checking foreign key integrity...")
        errors.extend(validate_foreign_keys(cursor))

        if errors:
            print(f"\n✗ {len(errors)} integrity issues found:")
            for error in errors:
                print(f"  - {error}")
            return 1
        else:
            print("\n✓ All integrity checks passed!")
            return 0
    finally:
        conn.close()

if __name__ == '__main__':
    exit(main())
```

---

## 6.7 Backup and Recovery

### Regular Backup Schedule

**Automated backup script:** `scripts/backup_metadata.sh`

```bash
#!/bin/bash
# Backup metadata tables daily

BACKUP_DIR="/var/backups/metadata"
DATE=$(date +%Y%m%d_%H%M%S)
DB_HOST="localhost"
DB_PORT="3308"
DB_USER="root"
DB_NAME="jwdb"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Get list of metadata tables
TABLES=$(mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -Nse \
  "SELECT TABLE_NAME FROM information_schema.TABLES \
   WHERE TABLE_SCHEMA='$DB_NAME' AND TABLE_NAME LIKE 'app_fd_md%'" \
  | tr '\n' ' ')

# Backup metadata tables
echo "Backing up metadata tables..."
mysqldump -h $DB_HOST -P $DB_PORT -u $DB_USER $DB_NAME $TABLES \
  > "$BACKUP_DIR/metadata_backup_$DATE.sql"

# Compress backup
gzip "$BACKUP_DIR/metadata_backup_$DATE.sql"

# Keep only last 30 days
find "$BACKUP_DIR" -name "metadata_backup_*.sql.gz" -mtime +30 -delete

echo "Backup complete: metadata_backup_$DATE.sql.gz"
```

**Schedule with cron:**
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/scripts/backup_metadata.sh >> /var/log/metadata_backup.log 2>&1
```

---

### Recovery Procedures

**Scenario 1: Restore single form**

```bash
# Extract table from backup
zcat /var/backups/metadata/metadata_backup_20251027_020000.sql.gz | \
  sed -n '/CREATE TABLE `app_fd_md01maritalStatus`/,/UNLOCK TABLES/p' | \
  mysql -h localhost -P 3308 -u root jwdb
```

**Scenario 2: Restore all metadata**

```bash
# Drop all metadata tables
mysql -h localhost -P 3308 -u root jwdb << 'EOF'
SELECT CONCAT('DROP TABLE IF EXISTS ', TABLE_NAME, ';')
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'jwdb' AND TABLE_NAME LIKE 'app_fd_md%';
EOF

# Restore from backup
zcat /var/backups/metadata/metadata_backup_20251027_020000.sql.gz | \
  mysql -h localhost -P 3308 -u root jwdb

# Verify
python joget_utility.py --verify-deployment
```

**Scenario 3: Point-in-time recovery**

```bash
# Restore backup before incident
zcat /var/backups/metadata/metadata_backup_20251027_020000.sql.gz | \
  mysql -h localhost -P 3308 -u root jwdb

# Replay changes from CSV
python joget_utility.py --deploy-master-data --data-only --yes

# Verify
python joget_utility.py --verify-deployment
```

---

## 6.8 Best Practices Summary

### DO ✅

1. **Version Control Everything**
   - All CSV files in Git
   - Commit messages with context
   - Tag production releases

2. **Validate Before Deploying**
   - Run `validate_metadata.py`
   - Check CSV encoding (UTF-8)
   - Verify unique codes

3. **Update CSV After Database Changes**
   - Keep CSV in sync with database
   - CSV is source of truth

4. **Use Soft Deletes**
   - Mark records as inactive
   - Don't delete historical data
   - Maintain referential integrity

5. **Backup Regularly**
   - Daily automated backups
   - Test restore procedures
   - Keep backups for 30+ days

6. **Document Changes**
   - Maintain METADATA_CHANGELOG.md
   - Include deployment dates
   - Note migration steps

7. **Test in Development First**
   - Never test in production
   - Verify in staging
   - Then deploy to production

---

### DON'T ❌

1. **Don't Delete Records Directly**
   - Use soft deletes (is_active=false)
   - Prevents broken foreign keys
   - Maintains audit trail

2. **Don't Update Database Without CSV**
   - CSV becomes out of sync
   - Next deployment overwrites changes
   - Loss of version control

3. **Don't Skip Validation**
   - Invalid data causes deployment failures
   - Harder to fix after deployment
   - Impacts user experience

4. **Don't Deploy to Production Without Testing**
   - Test in development
   - Verify in staging
   - Then production

5. **Don't Forget to Update Record Counts**
   - Deployment config must match CSV
   - Used for verification
   - Catches missing data

6. **Don't Use Special Characters in Codes**
   - No spaces, @, #, $, etc.
   - Use underscores for multi-word
   - Uppercase only

7. **Don't Mix Active and Archived Data**
   - Move deprecated data to archive
   - Keep active metadata clean
   - Document in archive README

---

## 6.9 Maintenance Checklist

### Weekly Tasks

- [ ] Review new metadata requests
- [ ] Validate CSV data quality
- [ ] Check for duplicate codes
- [ ] Update METADATA_CHANGELOG.md
- [ ] Deploy updates to development

### Monthly Tasks

- [ ] Review inactive/deprecated records
- [ ] Clean up old backups (keep 30 days)
- [ ] Run integrity validation script
- [ ] Update documentation
- [ ] Review and archive obsolete metadata

### Quarterly Tasks

- [ ] Full metadata audit
- [ ] Review and update naming conventions
- [ ] Test restore procedures
- [ ] Update deployment runbooks
- [ ] Train new team members

### Before Production Deployment

- [ ] Validate all CSV files
- [ ] Run dry-run deployment
- [ ] Backup current production data
- [ ] Notify stakeholders
- [ ] Schedule maintenance window
- [ ] Prepare rollback plan

### After Production Deployment

- [ ] Verify record counts
- [ ] Test forms in Joget UI
- [ ] Check cascading dropdowns
- [ ] Update METADATA_CHANGELOG.md
- [ ] Tag release in Git
- [ ] Notify stakeholders
- [ ] Archive deployment logs

---

**End of Part 6: Data Maintenance**

**Next:** Part 7 - Reference Section (Complete technical reference for all forms, configurations, and APIs)

---

# Part 7: Reference Section

## Overview

This section provides quick reference material for all metadata forms, configurations, files, and technical details. Use this for quick lookups when you need specific information.

---

## 7.1 Complete Form Reference

### Forms by Category

#### Identity & Demographics (6 forms)
| Form ID | Name | Records | Pattern | Purpose |
|---------|------|---------|---------|---------|
| md01maritalStatus | Marital Status | 4 | Simple | Marital status options |
| md02language | Language | 2 | Simple | Supported languages |
| md03gender | Gender | 3 | Simple | Gender options |
| md04title | Title | 4 | Simple | Personal titles (Mr, Mrs, etc.) |
| md05idType | ID Type | 5 | Simple | Identity document types |
| md06disability | Disability | 8 | Simple | Disability categories |

#### Location & Geography (4 forms)
| Form ID | Name | Records | Pattern | Purpose |
|---------|------|---------|---------|---------|
| md07district | District | 10 | Simple | Administrative districts |
| md08ward | Ward | 20 | Simple | Electoral wards |
| md09village | Village | 50 | Simple | Villages/localities |
| md10region | Region | 5 | Simple | Geographic regions |

#### Agriculture & Farming (8 forms)
| Form ID | Name | Records | Pattern | Purpose |
|---------|------|---------|---------|---------|
| md11farmType | Farm Type | 6 | Simple | Types of farms |
| md12farmSize | Farm Size | 5 | Simple | Farm size categories |
| md13farmOwnership | Farm Ownership | 4 | Simple | Land ownership types |
| md14irrigationType | Irrigation Type | 7 | Simple | Irrigation methods |
| md15soilType | Soil Type | 8 | Simple | Soil classifications |
| md16cropType | Crop Type | 15 | Simple | Major crop categories |
| md17livestockType | Livestock Type | 12 | Simple | Livestock categories |
| md18farmerCategory | Farmer Category | 6 | Simple | Farmer classifications |

#### Equipment & Tools (2 forms - Pattern 2)
| Form ID | Name | Records | Pattern | Purpose |
|---------|------|---------|---------|---------|
| md25equipmentCategory | Equipment Category | 9 | Parent | Equipment categories |
| md25equipment | Equipment (All) | 85 | Child (Pattern 2) | All equipment items in unified CSV |

**Deprecated CSV files (not deployed):**
- md25tillageEquipment.csv, md25plantingEquipment.csv, md25irrigationEquipment.csv, md25harvestingEquipment.csv, md25transportEquipment.csv, md25processingEquipment.csv, md25storageEquipment.csv, md25livestockEquipment.csv, md25generalTools.csv - **Replaced by unified md25equipment.csv**

#### Agricultural Inputs (2 forms - Pattern 2)
| Form ID | Name | Records | Pattern | Purpose |
|---------|------|---------|---------|---------|
| md27inputCategory | Input Category | 8 | Parent | Input categories |
| md27input | Input (All) | 61 | Child (Pattern 2) | All input items in unified CSV |

**Deprecated CSV files (not deployed):**
- md27fertilizer.csv, md27pesticide.csv, md27irrigation.csv, md27livestockSupply.csv - **Replaced by unified md27input.csv**
- md19crops.csv - **Merged into md27input.csv as SEEDS category**

#### Program & Subsidy Management (11 forms)
| Form ID | Name | Records | Pattern | Purpose |
|---------|------|---------|---------|---------|
| md21programType | Program Type | 8 | Simple | Subsidy program types |
| md22applicationStatus | Application Status | 10 | Simple | Application workflow states |
| md23documentType | Document Type | 12 | Simple | Required document types |
| md24paymentMethod | Payment Method | 6 | Simple | Payment options |
| md26trainingTopic | Training Topic | 15 | Simple | Agricultural training topics |
| md28benefitModel | Benefit Model | 5 | Simple | Subsidy benefit models |
| md30targetGroup | Target Group | 10 | Simple | Beneficiary target groups |
| md31decisionType | Decision Type | 5 | Simple | Application decision types |
| md32rejectionReason | Rejection Reason | 12 | Simple | Application rejection reasons |
| md33requestType | Request Type | 8 | Simple | Support request types |
| md34notificationType | Notification Type | 10 | Simple | System notification types |

#### Other (3 forms)
| Form ID | Name | Records | Pattern | Purpose |
|---------|------|---------|---------|---------|
| md35foodSecurityStatus | Food Security Status | 5 | Simple | Household food security levels |
| md36eligibilityOperator | Eligibility Operator | 6 | Simple | Logical operators for rules |
| md37collectionPoint | Collection Point | 10 | Simple | Distribution centers |

**Total: 37 forms, 416 records**

---

## 7.2 Configuration Files Reference

### master_data_deploy.yaml

**Location:** `config/master_data_deploy.yaml`

**Purpose:** Deployment configuration for all metadata forms.

**Structure:**
```yaml
metadata_forms:
  - form_id: md01maritalStatus           # Unique form identifier
    csv_file: data/metadata/md01maritalStatus.csv  # Data source
    form_definition: data/metadata_forms/md01maritalStatus.json  # Form JSON
    description: "Marital status options"  # Human-readable description
    depends_on: []                        # Parent form dependencies
    record_count: 4                       # Expected record count
    pattern: null                         # Pattern type (null, "pattern2")
```

**Pattern 2 Example:**
```yaml
  - form_id: md27input
    csv_file: null                        # Not used for Pattern 3
    csv_files:                            # Multiple category CSVs
      - data/metadata/md27fertilizer.csv
      - data/metadata/md27pesticide.csv
      - data/metadata/md27irrigation.csv
      - data/metadata/md27livestockSupply.csv
      - data/metadata/md27seeds.csv
    form_definition: data/metadata_forms/md27input.json
    description: "Agricultural inputs (polymorphic)"
    depends_on:
      - md27inputCategory                 # Parent must exist first
    record_count: 61                      # Sum of all category CSVs
    pattern: "pattern2"                   # Enable FK injection
```

---

### relationships.json

**Location:** `config/relationships.json`

**Purpose:** Configure FK injection for Pattern 2 parent-child relationships.

**Structure:**
```json
{
  "parent_child_relationships": {
    "<parent_form_id>": {
      "child_forms": [
        {
          "form_id": "<child_form_id>",
          "parent_fk_field": "<fk_field_name>",
          "category_mappings": {
            "<CATEGORY_CODE>": "<category_csv_filename.csv>"
          }
        }
      ]
    }
  }
}
```

**Example:**
```json
{
  "parent_child_relationships": {
    "md25equipmentCategory": {
      "child_forms": [{
        "form_id": "md25equipment",
        "parent_fk_field": "equipment_category",
        "category_mappings": {
          "TILLAGE": "md25tillageEquipment.csv",
          "PLANTING": "md25plantingEquipment.csv",
          "IRRIGATION": "md25irrigationEquipment.csv"
        }
      }]
    }
  }
}
```

**Key Points:**
- `parent_fk_field` must match FK field ID in child form
- Category codes (keys) must match parent table codes exactly
- CSV filenames (values) are relative to `data/metadata/`
- Multiple children per parent are supported

---

## 7.3 Directory Structure

```
joget_utility/
├── config/
│   ├── master_data_deploy.yaml         # Deployment configuration
│   └── relationships.json              # FK injection mappings
│
├── data/
│   ├── metadata/                       # CSV data files
│   │   ├── md01maritalStatus.csv
│   │   ├── md02language.csv
│   │   ├── ...
│   │   ├── md25tillageEquipment.csv    # Deprecated category-specific CSV (not used)
│   │   ├── md27fertilizer.csv          # Deprecated category-specific CSV (not used)
│   │   └── md37collectionPoint.csv
│   │
│   └── metadata_forms/                 # JSON form definitions
│       ├── md01maritalStatus.json
│       ├── md02language.json
│       ├── ...
│       ├── md25equipment.json          # Pattern 2 polymorphic child form
│       ├── md27input.json              # Pattern 2 polymorphic child form
│       └── md37collectionPoint.json
│
├── processors/
│   ├── data_augmentor.py              # FK injection processor
│   ├── form_generator.py              # JSON form generator
│   ├── master_data_deployer.py        # Deployment orchestrator
│   ├── nested_lov_fixer.py            # Cascading dropdown fixer
│   └── nested_lov_validator.py        # Cascading validator
│
├── docs/
│   ├── METADATA_MANUAL.md             # This manual
│   ├── JOGET_NESTED_LOV_GUIDE.md      # Cascading dropdowns guide
│   ├── CREATE-MDM-SPEC.md             # MDM specification
│   ├── TECHNICAL_DOCUMENTATION.md      # Technical reference
│   └── BASIC_FORMS_GUIDE.md           # Basic forms guide
│
├── scripts/
│   ├── validate_metadata.py           # CSV validation script
│   ├── validate_db_integrity.py       # Database validation
│   └── backup_metadata.sh             # Backup script
│
├── .env.3                             # Production environment
├── .env.8                             # Development environment
├── joget_client.py                    # Joget API client
├── joget_utility.py                   # Main CLI script
└── requirements.txt                   # Python dependencies
```

---

## 7.4 Database Schema

### Table Naming Convention

All metadata tables use the pattern: `app_fd_<formId>`

**Examples:**
- `app_fd_md01maritalStatus`
- `app_fd_md25equipment`
- `app_fd_md27input`

### Column Naming Convention

All columns use the pattern: `c_<fieldId>`

**Standard Columns (All Forms):**
- `id` - Primary key (auto-increment)
- `dateCreated` - Record creation timestamp
- `dateModified` - Last modification timestamp
- `createdBy` - User who created record
- `createdByName` - Display name of creator
- `modifiedBy` - User who modified record
- `modifiedByName` - Display name of modifier

**Metadata-Specific Columns:**
- `c_code` - Metadata code (primary key for lookups)
- `c_name` - Display label
- `c_<other_fields>` - Additional fields (e.g., `c_symbol`, `c_is_active`)

**Foreign Key Columns (Pattern 2):**
- `c_equipment_category` - FK to md25equipmentCategory
- `c_input_category` - FK to md27inputCategory
- `c_vehicle_category` - FK to md39vehicleCategory (example)

---

### Sample Table Structure

**md01maritalStatus:**
```sql
CREATE TABLE `app_fd_md01maritalStatus` (
  `id` varchar(255) NOT NULL,
  `dateCreated` datetime DEFAULT NULL,
  `dateModified` datetime DEFAULT NULL,
  `createdBy` varchar(255) DEFAULT NULL,
  `createdByName` varchar(255) DEFAULT NULL,
  `modifiedBy` varchar(255) DEFAULT NULL,
  `modifiedByName` varchar(255) DEFAULT NULL,
  `c_code` varchar(255) DEFAULT NULL,
  `c_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_code` (`c_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**md25equipment (Pattern 2 - Polymorphic):**
```sql
CREATE TABLE `app_fd_md25equipment` (
  `id` varchar(255) NOT NULL,
  `dateCreated` datetime DEFAULT NULL,
  `dateModified` datetime DEFAULT NULL,
  `createdBy` varchar(255) DEFAULT NULL,
  `createdByName` varchar(255) DEFAULT NULL,
  `modifiedBy` varchar(255) DEFAULT NULL,
  `modifiedByName` varchar(255) DEFAULT NULL,
  `c_code` varchar(255) DEFAULT NULL,
  `c_name` varchar(255) DEFAULT NULL,
  `c_equipment_category` varchar(255) DEFAULT NULL,  -- FK (injected)
  `c_category` varchar(255) DEFAULT NULL,            -- Sub-category
  `c_brand` varchar(255) DEFAULT NULL,               -- Category-specific
  `c_model` varchar(255) DEFAULT NULL,               -- Category-specific
  `c_power_source` varchar(255) DEFAULT NULL,        -- Category-specific
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_code` (`c_code`),
  KEY `idx_equipment_category` (`c_equipment_category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 7.5 Environment Variables

### Required Variables

**Joget Connection:**
- `JOGET_BASE_URL` - Joget base URL (e.g., `http://localhost:8080/jw`)
- `JOGET_API_ID` - API ID for authentication
- `JOGET_API_KEY` - API key for authentication

**Database Connection (Optional):**
- `DB_HOST` - Database host (e.g., `localhost`)
- `DB_PORT` - Database port (e.g., `3308`)
- `DB_NAME` - Database name (e.g., `jwdb`)
- `DB_USER` - Database username (e.g., `root`)
- `DB_PASSWORD` - Database password

### Environment Files

**Development (.env.8):**
```bash
JOGET_BASE_URL=http://localhost:8080/jw
JOGET_API_ID=dev_api_id
JOGET_API_KEY=dev_api_key
DB_HOST=localhost
DB_PORT=3308
DB_NAME=jwdb
DB_USER=root
DB_PASSWORD=
```

**Production (.env.3):**
```bash
JOGET_BASE_URL=https://production.example.com/jw
JOGET_API_ID=prod_api_id
JOGET_API_KEY=prod_api_key
DB_HOST=prod-db.example.com
DB_PORT=3306
DB_NAME=jwdb
DB_USER=joget_user
DB_PASSWORD=secure_password
```

---

## 7.6 API Endpoints

### FormCreator API

**Create Form:**
```
POST /jw/api/form/formCreator/addWithFiles
```

**Headers:**
- `api_id: <JOGET_API_ID>`
- `api_key: <JOGET_API_KEY>`
- `Referer: http://<host>/jw/web/console/app/subsidyApplication/1/forms`

**Body (multipart/form-data):**
- `form_definition_json` - File containing form JSON

**Response:**
```json
{
  "success": true,
  "formId": "md01maritalStatus",
  "message": "Form created successfully"
}
```

---

### Form Data API

**Save/Update Record:**
```
POST /jw/api/form/<formId>/saveOrUpdate
```

**Headers:**
- `api_id: <JOGET_API_ID>`
- `api_key: <JOGET_API_KEY>`
- `Content-Type: application/json`

**Body:**
```json
{
  "code": "single",
  "name": "Single"
}
```

**Response:**
```json
{
  "id": "generated-uuid",
  "code": "single",
  "name": "Single"
}
```

---

## 7.7 Command Line Reference

### Main Commands

**Deploy all metadata:**
```bash
python joget_utility.py --deploy-master-data --yes
```

**Deploy specific forms:**
```bash
python joget_utility.py --deploy-specific md01maritalStatus md02language --yes
```

**Deploy data only (skip forms):**
```bash
python joget_utility.py --deploy-master-data --data-only --yes
```

**Deploy forms only (skip data):**
```bash
python joget_utility.py --deploy-master-data --forms-only --yes
```

**Dry-run (preview):**
```bash
python joget_utility.py --deploy-master-data --dry-run
```

**Verify deployment:**
```bash
python joget_utility.py --verify-deployment
```

**Enable debug logging:**
```bash
python joget_utility.py --deploy-master-data --debug --yes
```

---

### Form Generator

**Generate form from CSV:**
```bash
python processors/form_generator.py \
  --csv data/metadata/md01maritalStatus.csv \
  --form-id md01maritalStatus \
  --form-name "MD.01 - Marital Status" \
  --output data/metadata_forms/md01maritalStatus.json
```

**With optional parameters:**
```bash
python processors/form_generator.py \
  --csv data/metadata/md01maritalStatus.csv \
  --form-id md01maritalStatus \
  --form-name "MD.01 - Marital Status" \
  --output data/metadata_forms/md01maritalStatus.json \
  --description "Marital status options for farmer registration" \
  --section-label "Marital Status Details" \
  --required-fields "code,name"
```

---

### Validation Scripts

**Validate CSV data quality:**
```bash
python scripts/validate_metadata.py
```

**Validate database integrity:**
```bash
python scripts/validate_db_integrity.py
```

---

## 7.8 Quick Lookup Tables

### Form ID to Table Name

| Form ID | Table Name |
|---------|------------|
| md01maritalStatus | app_fd_md01maritalStatus |
| md02language | app_fd_md02language |
| md25equipment | app_fd_md25equipment |
| md27input | app_fd_md27input |

### Pattern Type Reference

| Pattern | Description | Forms Using |
|---------|-------------|-------------|
| Simple | Standalone, no relationships | 32 forms (md01-md24, md26, md28-md37) |
| Pattern 2 | Parent-child with explicit FK | 2 hierarchies (MD25, MD27) |

### Record Counts

| Category | Forms | Records |
|----------|-------|---------|
| Identity & Demographics | 6 | 34 |
| Location & Geography | 4 | 85 |
| Agriculture & Farming | 8 | 58 |
| Equipment & Tools | 10 | 94 |
| Agricultural Inputs | 11 | 69 |
| Program & Subsidy | 11 | 91 |
| Other | 3 | 21 |
| **Total** | **37** | **416** |

---

## 7.9 Related Documentation

### Internal Documentation

- **METADATA_MANUAL.md** (this document) - Comprehensive metadata guide
- **TECHNICAL_DOCUMENTATION.md** - Full technical reference
- **JOGET_NESTED_LOV_GUIDE.md** - Cascading dropdowns guide
- **CREATE-MDM-SPEC.md** - MDM specification and requirements
- **BASIC_FORMS_GUIDE.md** - Basic form creation guide
- **MD19_MERGE_NOTES.md** - md19crops merger documentation
- **DEPLOYMENT_RESULTS.md** - Deployment test results
- **DEPLOYMENT_STRATEGY.md** - Deployment best practices
- **KNOWN_ISSUES.md** - Known transient failures

### External Documentation

- **Joget DX Documentation:** https://dev.joget.org/community/display/DX8/
- **Joget Form Builder:** https://dev.joget.org/community/display/DX8/Form+Builder
- **Joget API Reference:** https://dev.joget.org/community/display/DX8/JSON+API
- **SelectBox Element:** https://dev.joget.org/community/display/DX8/Select+Box

---

## 7.10 Troubleshooting Quick Reference

### Common Issues

| Symptom | Likely Cause | Solution | Reference |
|---------|--------------|----------|-----------|
| Form created, no data | CSV encoding issue | Convert to UTF-8 | Part 5.4 Issue 1 |
| FK is NULL | Missing pattern: "pattern2" | Add to config | Part 5.4 Issue 2 |
| Cascading shows all items | FK is TextField not SelectBox | Change to SelectBox | Part 5.4 Issue 3 |
| API endpoint not found | Form still processing | Wait 5s, retry | Part 5.4 Issue 4 |
| Random failures | Transient Joget issue | Retry deployment | Part 5.4 Issue 5 |

### Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| "Missing required value" | Required field empty in CSV | Check CSV data |
| "API endpoint not found" | Form not fully created | Wait and retry |
| "Table doesn't exist" | Physical table not created | Check form creation logs |
| "Validation failed" | Data doesn't match form | Check field names match |
| "Connection refused" | Joget not running | Start Joget server |

### Quick Diagnostics

**Check deployment status:**
```bash
python joget_utility.py --verify-deployment
```

**Check specific form:**
```sql
SELECT COUNT(*) FROM app_fd_md01maritalStatus;
```

**Check FK injection:**
```sql
SELECT c_code, c_equipment_category FROM app_fd_md25equipment LIMIT 5;
```

**Check form definition:**
```bash
python -c "
import json
with open('data/metadata_forms/md01maritalStatus.json') as f:
    form = json.load(f)
    print('Form ID:', form['properties']['id'])
    print('Fields:', [e['properties']['id'] for e in form['elements'][0]['elements']])
"
```

---

## 7.11 Index

### By Topic

**Adding Metadata:**
- Simple metadata → Part 4.1
- Parent-child relationship → Part 4.2
- Form generation → Part 4.3

**Deployment:**
- Full deployment → Part 5.2
- Selective deployment → Part 5.2
- Production checklist → Part 5.6
- Troubleshooting → Part 5.4

**Maintenance:**
- Updating records → Part 6.1
- Adding records → Part 6.2
- Data quality → Part 6.3
- Versioning → Part 6.4
- Backup/recovery → Part 6.7

**Reference:**
- Form catalog → Part 2, Part 7.1
- Configuration → Part 7.2
- Database schema → Part 7.4
- Commands → Part 7.7

### By Form ID

Quick jump to form details:
- md01-md06: Identity & Demographics → Part 2.1
- md07-md10: Location & Geography → Part 2.1
- md11-md18: Agriculture & Farming → Part 2.1
- md21-md24, md26, md28-md37: Program & Subsidy → Part 2.1
- md25*: Equipment (Pattern 2) → Part 2.2.1
- md27*: Input (Pattern 2) → Part 2.2.2

### By Task

**I want to...**
- Deploy all metadata → Part 1.1, Part 5.2
- Add a new simple form → Part 4.1
- Add a parent-child hierarchy → Part 4.2
- Update existing data → Part 6.1
- Fix a deployment failure → Part 5.4
- Backup metadata → Part 6.7
- Validate data quality → Part 6.3, Part 6.6

---

## 7.12 Version History

**Version 2.0** - October 27, 2025
- Complete rewrite replacing metadata-overview.docx
- Updated to Pattern 2 (Subcategory Source with FK injection)
- Documented md19crops merge into md27input as SEEDS
- 37 forms, 416 records
- Comprehensive deployment and maintenance guides

**Version 1.0** - (metadata-overview.docx)
- Initial metadata specification
- Outdated: Pre-dates Pattern 2 implementation
- Archived: docs/metadata-overview.docx

---

**End of Part 7: Reference Section**

---

# Conclusion

This manual provides comprehensive coverage of the Master Data Management (MDM) system for the subsidy application platform.

## Summary

**37 Metadata Forms, 416 Records**

- **32 Simple Forms** - Standalone lookup tables
- **2 Parent-Child Hierarchies** - Equipment (MD25) and Input (MD27) using Pattern 2
- **Pattern 2 (Recommended)** - Subcategory Source with FK injection for hierarchical data

## Key Takeaways

1. **Pattern 2 is the recommended approach** for hierarchical metadata
2. **CSV files are the source of truth** - always keep them in version control
3. **Verify every deployment** - never assume success
4. **Test locally, then staging, then production** - no exceptions
5. **Backup before production deployments** - prepare for rollback
6. **Use soft deletes (is_active=false)** - never hard delete metadata
7. **Document all changes** - maintain METADATA_CHANGELOG.md

## Getting Help

- **Documentation:** See Part 7.9 Related Documentation
- **Issues:** Check KNOWN_ISSUES.md for known problems
- **Support:** Contact development team
- **Joget Community:** https://dev.joget.org/community/

## Next Steps

1. Read Part 1 (Quick Start) for immediate tasks
2. Review Part 2 (Metadata Catalog) to understand existing forms
3. Study Part 3 (Understanding Patterns) for architecture concepts
4. Follow Part 4 (How-To Guides) when adding new metadata
5. Use Part 5 (Deployment Guide) for deployments
6. Refer to Part 6 (Data Maintenance) for ongoing maintenance
7. Keep Part 7 (Reference) handy for quick lookups

## Document Information

- **Version:** 2.0
- **Last Updated:** October 27, 2025
- **Author:** Development Team
- **File:** `docs/METADATA_MANUAL.md`
- **Lines:** ~7,200
- **Size:** ~190KB

---

**Thank you for using this manual. For questions or feedback, please contact the development team.**

