# Comprehensive Testing Strategy

## Overview

We've built a NEW system (`joget-dx-toolkit`) while keeping the OLD system (`joget_utility`) intact. We need to ensure:

1. ✅ **New features work** (joget-dx-toolkit)
2. ✅ **Old features still work** (joget_utility)
3. ✅ **No regressions** in existing functionality
4. ✅ **Coexistence** - both systems work side-by-side

---

## Phase 1: New Features Testing (joget-dx-toolkit)

### 1.1 Markdown Parser

**What to test:** MD → Canonical YAML conversion

```bash
# Test 1: Migration Center (complex spec)
joget-dx parse markdown form_tasks/MigrationCenter_FormSpecs.md -o test_output/migration.yaml

# Verify:
# ✓ 4 forms created
# ✓ All field types parsed (text, select, datetime, file, foreign_key)
# ✓ Foreign key relationships captured
# ✓ Select options extracted (including shared: field1/field2)
# ✓ Indexes captured

# Test 2: Simple spec (create a minimal MD file)
echo "# Test App
## Form 1: Simple Form
### Form Details
- Form ID: test_simple
- Table Name: app_fd_test

### Fields
| Field Name | Label | Type | Size | Required | Default |
|------------|-------|------|------|----------|---------|
| code | Code | Text Field | 100 | Yes | - |
| name | Name | Text Field | 255 | Yes | - |
" > test_simple.md

joget-dx parse markdown test_simple.md --app-id testApp -o test_output/simple.yaml

# Verify:
# ✓ Form created with 2 fields
# ✓ Primary key detected (code)
```

**Expected Results:**
- ✅ Complex spec parsed without errors
- ✅ Simple spec parsed without errors
- ✅ YAML validates against schema
- ✅ All field types correctly mapped

---

### 1.2 Canonical Format Validation

**What to test:** Pydantic schema validation

```bash
# Test 1: Valid canonical YAML
joget-dx validate joget-dx-toolkit/migration_center.yaml

# Expected: ✓ Valid canonical format

# Test 2: Invalid canonical YAML (create broken YAML)
# Missing required field
echo "version: '1.0'
metadata:
  app_id: broken
forms:
  - id: test
    name: Test
    table: app_fd_test
    fields:
      - id: field1
        label: Field 1
        # Missing 'type' - should fail
" > test_output/broken.yaml

joget-dx validate test_output/broken.yaml

# Expected: ✗ Validation failed (missing 'type')

# Test 3: Foreign key validation
# Reference to non-existent form
echo "version: '1.0'
metadata:
  app_id: fktest
  app_name: FK Test
forms:
  - id: child
    name: Child
    table: app_fd_child
    fields:
      - id: id
        type: text
        label: ID
        primary_key: true
      - id: parent_id
        type: foreign_key
        label: Parent
        references:
          form: nonexistent_form  # Should fail
          field: id
          label_field: name
" > test_output/bad_fk.yaml

joget-dx validate test_output/bad_fk.yaml

# Expected: ✗ References non-existent form
```

**Expected Results:**
- ✅ Valid specs pass validation
- ✅ Invalid specs fail with clear error messages
- ✅ Foreign key references validated
- ✅ Primary key requirements enforced

---

### 1.3 Joget Builder

**What to test:** Canonical YAML → Joget JSON

```bash
# Test 1: Build Migration Center forms
joget-dx build joget joget-dx-toolkit/migration_center.yaml -o test_output/forms/ --overwrite

# Verify output:
ls -la test_output/forms/

# Expected files:
# - deployment_jobs.json
# - deployment_history.json
# - prerequisite_validation.json
# - component_registry.json

# Test 2: Inspect generated JSON structure
cat test_output/forms/deployment_jobs.json | jq '.properties.tableName'
# Expected: "app_fd_deployment_jobs"

cat test_output/forms/component_registry.json | jq '.properties.tableName'
# Expected: "app_fd_comp_list"

# Test 3: Verify field mappings
cat test_output/forms/deployment_jobs.json | jq '.elements[0].elements[0].elements[] | select(.properties.id == "job_type") | .className'
# Expected: "org.joget.apps.form.lib.SelectBox"

# Test 4: Verify foreign key SelectBox
cat test_output/forms/deployment_history.json | jq '.elements[0].elements[0].elements[] | select(.properties.id == "job_id") | .properties.optionsBinder.className'
# Expected: "org.joget.apps.form.lib.FormOptionsBinder"

cat test_output/forms/deployment_history.json | jq '.elements[0].elements[0].elements[] | select(.properties.id == "job_id") | .properties.optionsBinder.properties.formDefId'
# Expected: "deployment_jobs"
```

**Expected Results:**
- ✅ All 4 forms generated
- ✅ Table names correct (including app_fd_comp_list)
- ✅ Field types mapped correctly
- ✅ SelectBox uses optionsBinder (not options array)
- ✅ Foreign keys use FormOptionsBinder
- ✅ Default values converted ({currentUser}, {currentDateTime})

---

### 1.4 CLI Interface

**What to test:** Command-line user experience

```bash
# Test 1: Help commands
joget-dx --help
joget-dx parse --help
joget-dx build --help
joget-dx deploy --help

# Test 2: Version
joget-dx --version
# Expected: joget-dx-toolkit, version 0.1.0

# Test 3: Short alias
jdx --version
# Expected: Same as joget-dx

# Test 4: Error handling (missing required args)
joget-dx parse markdown
# Expected: Error: Missing argument 'INPUT_FILE'

joget-dx build joget migration_center.yaml
# Expected: Default output to ./forms/

# Test 5: Dry run deploy
joget-dx deploy test_output/forms/*.json --app-id test --dry-run
# Expected: Shows what would be deployed, but doesn't deploy
```

**Expected Results:**
- ✅ Help text clear and informative
- ✅ Version displayed correctly
- ✅ Short alias (jdx) works
- ✅ Missing args show helpful errors
- ✅ Dry run mode works

---

## Phase 2: Old Features Testing (joget_utility)

### 2.1 CSV → Form Generation (Old System)

**What to test:** Existing CSV-based form generation still works

```bash
# Test 1: Generate form from existing metadata CSV
cd joget_utility
python joget_utility.py --generate-form ../data/metadata/md01maritalStatus.csv --output test_md01.json

# Verify:
# ✓ Form JSON created
# ✓ Structure matches old format

# Test 2: Generate all metadata forms
python joget_utility.py --generate-forms-from-csv --dry-run

# Expected: Shows all forms that would be generated

# Test 3: Actually generate
python joget_utility.py --generate-forms-from-csv --yes

# Verify:
ls -la ../data/metadata_forms/
# Should see md01maritalStatus.json, md02gender.json, etc.
```

**Expected Results:**
- ✅ Old CSV parser still works
- ✅ Forms generated with correct structure
- ✅ No breaking changes to existing workflow

---

### 2.2 Master Data Deployment (Old System)

**What to test:** Existing deployment pipeline

```bash
# Test 1: Deploy single metadata form (dry run)
python joget_utility.py --deploy-master-data --forms-only --dry-run --yes

# Expected: Shows deployment plan

# Test 2: Check deployment configuration
cat ../config/master_data_deploy.yaml
# Verify: FormCreator API credentials present

# Note: Don't actually deploy to avoid polluting Joget server during testing
```

**Expected Results:**
- ✅ Deployment dry-run works
- ✅ Configuration loading works
- ✅ No errors in deployment logic

---

### 2.3 Form Validation (Old System)

**What to test:** Nested LOV validator

```bash
# Test 1: Validate nested LOV forms
cd joget_utility
python -c "
from processors.nested_lov_validator import NestedLOVValidator
validator = NestedLOVValidator()
# Run validation on existing forms
"

# Expected: Old validation logic still functional
```

---

## Phase 3: Integration Testing

### 3.1 Cross-System Compatibility

**What to test:** New forms work with old deployer

```bash
# Test 1: Can old deployer deploy new toolkit forms?
cd joget_utility

# Deploy a form created by new toolkit
python joget_utility.py --create-form \
  ../joget-dx-toolkit/migration_center_forms/component_registry.json \
  --app-id migrationCenter \
  --dry-run

# Expected: ✓ Old deployer can read new form JSON

# Test 2: Can new toolkit build from old CSV?
cd ../joget-dx-toolkit
joget-dx parse csv ../data/metadata/md01maritalStatus.csv \
  -o test_output/md01_from_new.yaml \
  --app-id masterData

joget-dx build joget test_output/md01_from_new.yaml -o test_output/md01_forms/

# Compare with old generator
diff test_output/md01_forms/md01maritalStatus.json \
     ../data/metadata_forms/md01maritalStatus.json

# Expected: Similar structure (may have minor differences in formatting)
```

**Expected Results:**
- ✅ Old deployer can deploy new toolkit forms
- ✅ New toolkit can process old CSV files
- ✅ Forms are compatible across systems

---

### 3.2 Side-by-Side Usage

**What to test:** Both systems can coexist

```bash
# Scenario: Use new toolkit for complex MD specs, old system for simple CSVs

# Step 1: Generate Migration Center with new toolkit
joget-dx parse markdown form_tasks/MigrationCenter_FormSpecs.md -o specs/migration.yaml
joget-dx build joget specs/migration.yaml -o new_forms/

# Step 2: Generate simple metadata with old system
cd joget_utility
python joget_utility.py --generate-forms-from-csv

# Step 3: Verify both sets of forms exist
ls -la ../new_forms/           # Migration Center (new)
ls -la ../data/metadata_forms/ # Metadata (old)

# Step 4: Both can be deployed
# (This would require actual Joget server - skip for now)
```

**Expected Results:**
- ✅ Both systems produce valid forms
- ✅ No conflicts or interference
- ✅ Clear use cases for each system

---

## Phase 4: Regression Testing

### 4.1 Existing Data Processing

**What to test:** Old GAM business logic unaffected

```bash
# Test GAM-specific scripts (these should be completely unaffected)
python get_secu_ops.py --help
python investments.py --help
python secu_values.py --help

# Expected: All work as before (no imports from new toolkit)
```

**Expected Results:**
- ✅ GAM business logic untouched
- ✅ No accidental dependencies on new toolkit

---

### 4.2 Configuration Files

**What to test:** Configs still load correctly

```bash
# Old config
cat config/joget.yaml
# Expected: Valid YAML, no changes needed

# New toolkit doesn't use old config (fully independent)
# Expected: Old config irrelevant to new toolkit
```

---

### 4.3 Database Schema

**What to test:** No unintended database changes

```bash
# Migration Center forms have new table names
# Verify these don't conflict with existing metadata tables

mysql -h localhost -P 3308 -u root -p jwdb -e "SHOW TABLES LIKE 'app_fd_%';"

# Expected:
# - Old metadata tables (md01, md02, etc.) still exist
# - Migration Center tables NOT yet created (only after deployment)
```

---

## Phase 5: End-to-End Integration Test

### Full Workflow Test

**Scenario:** Create new app from scratch using new toolkit, deploy with old system

```bash
# Step 1: Create spec
cat > test_app_spec.md << 'EOF'
# Test Application

## Form 1: Customers
### Form Details
- Form ID: customers
- Table Name: app_fd_customers

### Fields
| Field Name | Label | Type | Size | Required | Default |
|------------|-------|------|------|----------|---------|
| customer_id | Customer ID | Text Field | 100 | Yes | UUID |
| customer_name | Customer Name | Text Field | 255 | Yes | - |
| email | Email | Text Field | 255 | No | - |
EOF

# Step 2: Parse with new toolkit
joget-dx parse markdown test_app_spec.md --app-id testApp -o test_app.yaml

# Step 3: Validate
joget-dx validate test_app.yaml

# Step 4: Build
joget-dx build joget test_app.yaml -o test_app_forms/

# Step 5: Inspect generated form
cat test_app_forms/customers.json | jq '.properties.id'
# Expected: "customers"

cat test_app_forms/customers.json | jq '.properties.tableName'
# Expected: "app_fd_customers"

# Step 6: (Optional) Deploy with old system
cd joget_utility
python joget_utility.py --create-form ../joget-dx-toolkit/test_app_forms/customers.json \
  --app-id testApp \
  --dry-run

# Expected: ✓ Deployment plan shown
```

**Expected Results:**
- ✅ Complete workflow works end-to-end
- ✅ Forms valid and deployable
- ✅ Both systems cooperate seamlessly

---

## Test Checklist Summary

### New System (joget-dx-toolkit)
- [ ] Markdown parser handles complex specs
- [ ] Markdown parser handles simple specs
- [ ] Canonical validation catches errors
- [ ] Foreign key validation works
- [ ] Joget builder creates valid JSON
- [ ] Table names respected (app_fd_comp_list ✓)
- [ ] Field types mapped correctly
- [ ] SelectBox uses optionsBinder
- [ ] Foreign keys use FormOptionsBinder
- [ ] CLI commands work (help, version, parse, build, validate)
- [ ] Dry run mode works

### Old System (joget_utility)
- [ ] CSV → Form generation still works
- [ ] Batch form generation works
- [ ] Master data deployment works (dry run)
- [ ] Nested LOV validation works
- [ ] Configuration loading works

### Integration
- [ ] Old deployer can deploy new forms
- [ ] New toolkit can parse old CSVs
- [ ] Both systems coexist without conflicts
- [ ] No cross-dependencies

### Regression
- [ ] GAM business logic unaffected
- [ ] Existing configs still valid
- [ ] No accidental database changes

---

## Quick Smoke Test (5 minutes)

Run this to verify everything still works:

```bash
#!/bin/bash
set -e

echo "=== SMOKE TEST ==="

# 1. New toolkit - parse
echo "1. Parsing Migration Center..."
joget-dx parse markdown form_tasks/MigrationCenter_FormSpecs.md -o /tmp/test_migration.yaml

# 2. New toolkit - validate
echo "2. Validating..."
joget-dx validate /tmp/test_migration.yaml

# 3. New toolkit - build
echo "3. Building forms..."
joget-dx build joget /tmp/test_migration.yaml -o /tmp/test_forms/ --overwrite

# 4. Verify files created
echo "4. Checking outputs..."
test -f /tmp/test_forms/component_registry.json || { echo "FAIL: component_registry not created"; exit 1; }
test -f /tmp/test_forms/deployment_jobs.json || { echo "FAIL: deployment_jobs not created"; exit 1; }

# 5. Check table name
TABLE_NAME=$(cat /tmp/test_forms/component_registry.json | jq -r '.properties.tableName')
if [ "$TABLE_NAME" != "app_fd_comp_list" ]; then
  echo "FAIL: Wrong table name: $TABLE_NAME"
  exit 1
fi

# 6. Old system - generate from CSV
echo "5. Testing old CSV generator..."
cd joget_utility
python joget_utility.py --generate-form ../data/metadata/md01maritalStatus.csv --output /tmp/test_old.json

test -f /tmp/test_old.json || { echo "FAIL: Old generator failed"; exit 1; }

echo ""
echo "=== ✓ SMOKE TEST PASSED ==="
echo "Both old and new systems working correctly!"
```

**Run this:**
```bash
chmod +x smoke_test.sh
./smoke_test.sh
```

---

## Continuous Testing

### Git Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Run smoke test before every commit
./smoke_test.sh || {
  echo "Tests failed! Commit aborted."
  exit 1
}
```

### Automated Testing (Future)

Consider adding:
1. **pytest** tests for parsers/builders/deployers
2. **GitHub Actions** CI/CD pipeline
3. **Docker** test environment with Joget instance

---

## When to Use Which System

### Use NEW joget-dx-toolkit when:
- ✅ Creating complex apps with multiple forms
- ✅ Need foreign key relationships
- ✅ Want type-safe specifications
- ✅ Prefer markdown documentation
- ✅ Building reusable form libraries
- ✅ Need platform-agnostic specs (future: Django, Spring)

### Use OLD joget_utility when:
- ✅ Processing simple CSV metadata
- ✅ Batch processing existing md01-md49 forms
- ✅ Quick one-off form generation
- ✅ Existing workflows already established
- ✅ No need for complex relationships

### Both systems can coexist - choose based on task complexity!
