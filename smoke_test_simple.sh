#!/bin/bash
# Simple Smoke Test - Core Functionality Only
set -e

export PATH="/Users/aarelaponin/Library/Python/3.12/bin:$PATH"

echo "════════════════════════════════════════════════════════════"
echo "  SMOKE TEST - Joget DX Toolkit Core Features"
echo "════════════════════════════════════════════════════════════"
echo ""

PASSED=0
FAILED=0

test_pass() {
  echo "  ✓ $1"
  PASSED=$((PASSED + 1))
}

test_fail() {
  echo "  ✗ $1"
  echo "    Error: $2"
  FAILED=$((FAILED + 1))
}

# ============================================================================
# Test 1: CLI Installation
# ============================================================================
echo "[1/10] Testing CLI installation..."
if command -v joget-dx &> /dev/null; then
  VERSION=$(joget-dx --version 2>&1 | head -1)
  test_pass "CLI installed: $VERSION"
else
  test_fail "CLI not found" "Run: cd joget-dx-toolkit && pip install -e ."
fi

# ============================================================================
# Test 2: Parse Markdown
# ============================================================================
echo "[2/10] Parsing Migration Center markdown..."
rm -f /tmp/test_migration.yaml
if joget-dx parse markdown form_tasks/MigrationCenter_FormSpecs.md -o /tmp/test_migration.yaml > /dev/null 2>&1; then
  if [ -f /tmp/test_migration.yaml ]; then
    test_pass "Markdown parsed successfully"
  else
    test_fail "Parse succeeded but no output file" "Check /tmp/test_migration.yaml"
  fi
else
  test_fail "Markdown parsing failed" "Run manually: joget-dx parse markdown form_tasks/MigrationCenter_FormSpecs.md"
fi

# ============================================================================
# Test 3: Validate Canonical YAML
# ============================================================================
echo "[3/10] Validating canonical YAML..."
if [ -f /tmp/test_migration.yaml ]; then
  if joget-dx validate /tmp/test_migration.yaml > /dev/null 2>&1; then
    test_pass "Canonical YAML is valid"
  else
    test_fail "Validation failed" "Check YAML structure"
  fi
else
  test_fail "Cannot validate" "YAML file doesn't exist"
fi

# ============================================================================
# Test 4: Build Joget Forms
# ============================================================================
echo "[4/10] Building Joget forms..."
rm -rf /tmp/test_forms
mkdir -p /tmp/test_forms
if joget-dx build joget /tmp/test_migration.yaml -o /tmp/test_forms/ --overwrite > /dev/null 2>&1; then
  test_pass "Forms built successfully"
else
  test_fail "Form building failed" "Run manually to see errors"
fi

# ============================================================================
# Test 5: Verify Form Files Created
# ============================================================================
echo "[5/10] Checking generated files..."
EXPECTED_FORMS=("deployment_jobs.json" "deployment_history.json" "prerequisite_validation.json" "component_registry.json")
MISSING=0
for form in "${EXPECTED_FORMS[@]}"; do
  if [ ! -f "/tmp/test_forms/$form" ]; then
    MISSING=$((MISSING + 1))
  fi
done

if [ $MISSING -eq 0 ]; then
  test_pass "All 4 forms created"
else
  test_fail "Missing $MISSING form files" "Check /tmp/test_forms/"
fi

# ============================================================================
# Test 6: Verify Table Name Fix
# ============================================================================
echo "[6/10] Verifying table name fix..."
if [ -f /tmp/test_forms/component_registry.json ]; then
  TABLE_NAME=$(python3 -c "import json; print(json.load(open('/tmp/test_forms/component_registry.json'))['properties']['tableName'])" 2>/dev/null || echo "ERROR")
  if [ "$TABLE_NAME" = "app_fd_comp_list" ]; then
    test_pass "Table name correct: app_fd_comp_list (17 chars)"
  else
    test_fail "Wrong table name: $TABLE_NAME" "Expected: app_fd_comp_list"
  fi
else
  test_fail "Cannot verify" "component_registry.json missing"
fi

# ============================================================================
# Test 7: Verify JSON Structure
# ============================================================================
echo "[7/10] Validating Joget JSON structure..."
if [ -f /tmp/test_forms/deployment_jobs.json ]; then
  CLASS_NAME=$(python3 -c "import json; print(json.load(open('/tmp/test_forms/deployment_jobs.json'))['className'])" 2>/dev/null || echo "ERROR")
  if [ "$CLASS_NAME" = "org.joget.apps.form.model.Form" ]; then
    test_pass "Correct Joget form className"
  else
    test_fail "Wrong className: $CLASS_NAME" "Expected: org.joget.apps.form.model.Form"
  fi
else
  test_fail "Cannot verify" "deployment_jobs.json missing"
fi

# ============================================================================
# Test 8: Verify Field Count
# ============================================================================
echo "[8/10] Checking field counts..."
if [ -f /tmp/test_forms/deployment_jobs.json ]; then
  FIELD_COUNT=$(python3 -c "import json; print(len(json.load(open('/tmp/test_forms/deployment_jobs.json'))['elements'][0]['elements'][0]['elements']))" 2>/dev/null || echo "0")
  if [ "$FIELD_COUNT" -eq 16 ]; then
    test_pass "deployment_jobs has 16 fields"
  else
    test_fail "Wrong field count: $FIELD_COUNT" "Expected: 16"
  fi
else
  test_fail "Cannot verify" "deployment_jobs.json missing"
fi

# ============================================================================
# Test 9: Verify Foreign Key Structure
# ============================================================================
echo "[9/10] Checking foreign key structure..."
if [ -f /tmp/test_forms/deployment_history.json ]; then
  # Check if job_id field has FormOptionsBinder
  HAS_FK=$(python3 -c "
import json
form = json.load(open('/tmp/test_forms/deployment_history.json'))
fields = form['elements'][0]['elements'][0]['elements']
job_id_field = next((f for f in fields if f['properties']['id'] == 'job_id'), None)
if job_id_field and 'optionsBinder' in job_id_field['properties']:
    binder = job_id_field['properties']['optionsBinder']
    if binder.get('className') == 'org.joget.apps.form.lib.FormOptionsBinder':
        if binder.get('properties', {}).get('formDefId') == 'deployment_jobs':
            print('CORRECT')
        else:
            print('WRONG_FORM')
    else:
        print('WRONG_CLASS')
else:
    print('NO_BINDER')
" 2>/dev/null || echo "ERROR")

  if [ "$HAS_FK" = "CORRECT" ]; then
    test_pass "Foreign key correctly configured"
  else
    test_fail "Foreign key issue: $HAS_FK" "Check deployment_history.json job_id field"
  fi
else
  test_fail "Cannot verify" "deployment_history.json missing"
fi

# ============================================================================
# Test 10: Old System Compatibility
# ============================================================================
echo "[10/10] Checking old system compatibility..."
if [ -f joget_utility/joget_utility.py ]; then
  test_pass "Old joget_utility still exists"
else
  test_fail "Old system missing" "joget_utility/joget_utility.py not found"
fi

# ============================================================================
# Summary
# ============================================================================
echo ""
echo "════════════════════════════════════════════════════════════"
echo "  RESULTS"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "  Passed: $PASSED / $((PASSED + FAILED))"
echo "  Failed: $FAILED / $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
  echo "  ✓✓✓ ALL TESTS PASSED ✓✓✓"
  echo ""
  echo "  Your joget-dx-toolkit is working perfectly!"
  echo ""
  echo "  Next steps:"
  echo "    1. Deploy forms: joget-dx deploy migration_center_forms/*.json \\"
  echo "                       --app-id migrationCenter --server URL --api-key KEY --api-id API"
  echo "    2. Test with your own specs"
  echo "    3. Enjoy the new toolkit!"
  echo ""
  exit 0
else
  echo "  ⚠ $FAILED test(s) failed"
  echo ""
  echo "  Review errors above and fix issues."
  echo "  Most critical: Tests 1-6 should pass."
  echo ""
  exit 1
fi
