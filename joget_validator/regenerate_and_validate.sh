#!/bin/bash

# Quick script to regenerate validation spec and run validation
# Usage: ./regenerate_and_validate.sh

echo "======================================"
echo "GovStack Validation Tool"
echo "======================================"

# Configuration
FORMS_DIR="/Users/aarelaponin/IdeaProjects/gs-plugins/processing-server/doc-forms"
SERVICES_YML="/Users/aarelaponin/IdeaProjects/gs-plugins/processing-server/src/main/resources/docs-metadata/services.yml"
TEST_DATA="/Users/aarelaponin/IdeaProjects/gs-plugins/processing-server/src/main/resources/docs-metadata/test-data.json"
OUTPUT_SPEC="generated/test-validation.yml"

# Step 1: Generate validation spec
echo ""
echo "Step 1: Generating validation specification..."
echo "--------------------------------------"
python3 generate_validation_spec.py \
  --forms-dir "$FORMS_DIR" \
  --services "$SERVICES_YML" \
  --test-data "$TEST_DATA" \
  --output "$OUTPUT_SPEC"

if [ $? -ne 0 ]; then
    echo "Error: Failed to generate validation spec"
    exit 1
fi

# Step 2: Run diagnostic validation
echo ""
echo "Step 2: Running diagnostic validation..."
echo "--------------------------------------"
python3 run_diagnostic_validation.py --spec "$OUTPUT_SPEC"

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "✅ VALIDATION PASSED"
    echo "======================================"
else
    echo ""
    echo "======================================"
    echo "❌ VALIDATION FAILED"
    echo "======================================"
    echo "Check the errors above and fix the issues"
fi