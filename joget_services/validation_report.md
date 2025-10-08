# Form Structure Database Validation Report

**Validation Date:** 2025-10-02T00:50:09.569138
**Database:** `jwdb@localhost:3306`
**Form Structure File:** `form_structure.yaml`

## Summary

- **Total Forms:** 10
- **Total Fields:** 236
- **Validated Fields:** 226 (95.8%)
- **Failed Validations:** 10
- **Warnings:** 137
- **Missing Tables:** 0
- **Missing Columns:** 10

### ⚠️ Validation Status: ISSUES FOUND

Found 10 validation issues that need attention.

## Missing Columns

| Form | Field | Table | Expected Column | Suggestions |
|------|-------|-------|----------------|-------------|
| `farmerCropsLivestock` | `cropInstruction` | `farmer_crop_livestck` | `c_cropInstruction` | None |
| `farmerCropsLivestock` | `cropInstruction` | `farmer_crop_livestck` | `c_cropInstruction` | None |
| `farmerDeclaration` | `declarationHeader` | `farmer_declaration` | `c_declarationHeader` | `c_declaration_key`, `c_declarationConsent`, `c_declarationFullName` |
| `farmerDeclaration` | `declarationText` | `farmer_declaration` | `c_declarationText` | `c_declaration_key`, `c_declarationConsent`, `c_declarationFullName` |
| `farmerDeclaration` | `registrationInfo` | `farmer_declaration` | `c_registrationInfo` | `c_registrationStation`, `c_registrationChannel`, `c_registrationStatus` |
| `farmerDeclaration` | `declarationHeader` | `farmer_declaration` | `c_declarationHeader` | `c_declaration_key`, `c_declarationConsent`, `c_declarationFullName` |
| `farmerDeclaration` | `declarationText` | `farmer_declaration` | `c_declarationText` | `c_declaration_key`, `c_declarationConsent`, `c_declarationFullName` |
| `farmerDeclaration` | `registrationInfo` | `farmer_declaration` | `c_registrationInfo` | `c_registrationStation`, `c_registrationChannel`, `c_registrationStatus` |
| `farmerHousehold` | `householdInstruction` | `farmer_registry` | `c_householdInstruction` | None |
| `farmerHousehold` | `householdInstruction` | `farmer_registry` | `c_householdInstruction` | None |

## Warnings

- **cropManagementForm.farmer_id**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **cropManagementForm.cropType**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **cropManagementForm.areaUnit**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **cropManagementForm.fertilizerApplied**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **cropManagementForm.pesticidesApplied**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **cropManagementForm.farmer_id**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **cropManagementForm.cropType**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **cropManagementForm.areaUnit**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **cropManagementForm.fertilizerApplied**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **cropManagementForm.pesticidesApplied**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerAgriculture.agriculture_key**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **farmerAgriculture.cropProduction**: Potential type mismatch: Joget field type 'radio' vs DB column type 'longtext'
- **farmerAgriculture.livestockProduction**: Potential type mismatch: Joget field type 'radio' vs DB column type 'longtext'
- **farmerAgriculture.canReadWrite**: Potential type mismatch: Joget field type 'radio' vs DB column type 'longtext'
- **farmerAgriculture.parent_id**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **farmerAgriculture.mainSourceFarmLabour**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerAgriculture.mainSourceLivelihood**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerAgriculture.agriculturalManagementSkills**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerAgriculture.mainSourceAgriculturalInfo**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerAgriculture.conservationPractices**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerAgriculture.shocks_hazards**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerAgriculture.agriculture_key**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **farmerAgriculture.cropProduction**: Potential type mismatch: Joget field type 'radio' vs DB column type 'longtext'
- **farmerAgriculture.livestockProduction**: Potential type mismatch: Joget field type 'radio' vs DB column type 'longtext'
- **farmerAgriculture.canReadWrite**: Potential type mismatch: Joget field type 'radio' vs DB column type 'longtext'
- **farmerAgriculture.parent_id**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **farmerAgriculture.mainSourceFarmLabour**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerAgriculture.mainSourceLivelihood**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerAgriculture.agriculturalManagementSkills**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerAgriculture.mainSourceAgriculturalInfo**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerAgriculture.conservationPractices**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerAgriculture.shocks_hazards**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerBasicInfo.gender**: Potential type mismatch: Joget field type 'radio' vs DB column type 'longtext'
- **farmerBasicInfo.date_of_birth**: Potential type mismatch: Joget field type 'date' vs DB column type 'longtext'
- **farmerBasicInfo.marital_status**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerBasicInfo.preferred_language**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerBasicInfo.member_of_cooperative**: Potential type mismatch: Joget field type 'radio' vs DB column type 'longtext'
- **farmerBasicInfo.parent_id**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **farmerBasicInfo.gender**: Potential type mismatch: Joget field type 'radio' vs DB column type 'longtext'
- **farmerBasicInfo.date_of_birth**: Potential type mismatch: Joget field type 'date' vs DB column type 'longtext'
- **farmerBasicInfo.marital_status**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerBasicInfo.preferred_language**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerBasicInfo.member_of_cooperative**: Potential type mismatch: Joget field type 'radio' vs DB column type 'longtext'
- **farmerBasicInfo.parent_id**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **farmerCropsLivestock.parent_id**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **farmerCropsLivestock.crops_livestock_key**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **farmerCropsLivestock.hasLivestock**: Potential type mismatch: Joget field type 'radio' vs DB column type 'longtext'
- **farmerCropsLivestock.parent_id**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **farmerCropsLivestock.crops_livestock_key**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **farmerCropsLivestock.hasLivestock**: Potential type mismatch: Joget field type 'radio' vs DB column type 'longtext'
- **farmerCropsLivestock.farmer_id**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **farmerCropsLivestock.cropType**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerCropsLivestock.areaUnit**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerCropsLivestock.fertilizerApplied**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerCropsLivestock.pesticidesApplied**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerCropsLivestock.farmer_id**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **farmerCropsLivestock.livestockType**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerDeclaration.parent_id**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **farmerDeclaration.declaration_key**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **farmerDeclaration.declarationConsent**: Potential type mismatch: Joget field type 'checkbox' vs DB column type 'longtext'
- **farmerDeclaration.field13**: Potential type mismatch: Joget field type 'date' vs DB column type 'longtext'
- **farmerDeclaration.beneficiaryCode**: Potential type mismatch: Joget field type 'id_generator' vs DB column type 'longtext'
- **farmerDeclaration.registrationChannel**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerDeclaration.registrationStatus**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **farmerDeclaration.parent_id**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **farmerDeclaration.declaration_key**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **farmerDeclaration.declarationConsent**: Potential type mismatch: Joget field type 'checkbox' vs DB column type 'longtext'
- **farmerDeclaration.field13**: Potential type mismatch: Joget field type 'date' vs DB column type 'longtext'
- **farmerDeclaration.beneficiaryCode**: Potential type mismatch: Joget field type 'id_generator' vs DB column type 'longtext'
- **farmerDeclaration.registrationChannel**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerDeclaration.registrationStatus**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **farmerHousehold.household_key**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **farmerHousehold.parent_id**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **farmerHousehold.household_key**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **farmerHousehold.parent_id**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **farmerHousehold.farmer_id**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **farmerHousehold.sex**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerHousehold.date_of_birth**: Potential type mismatch: Joget field type 'date' vs DB column type 'longtext'
- **farmerHousehold.relationship**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerHousehold.orphanhoodStatus**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerHousehold.participatesInAgriculture**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerHousehold.disability**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerHousehold.chronicallyIll**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerIncomePrograms.income_programs_key**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **farmerIncomePrograms.mainSourceIncome**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerIncomePrograms.income_sources**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerIncomePrograms.gainfulEmployment**: Potential type mismatch: Joget field type 'radio' vs DB column type 'longtext'
- **farmerIncomePrograms.governmentEmployed**: Potential type mismatch: Joget field type 'radio' vs DB column type 'longtext'
- **farmerIncomePrograms.parent_id**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **farmerIncomePrograms.relativeSupport**: Potential type mismatch: Joget field type 'radio' vs DB column type 'longtext'
- **farmerIncomePrograms.supportFrequency**: Potential type mismatch: Joget field type 'radio' vs DB column type 'longtext'
- **farmerIncomePrograms.supportType**: Potential type mismatch: Joget field type 'checkbox' vs DB column type 'longtext'
- **farmerIncomePrograms.supportProgram**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerIncomePrograms.creditDefault**: Potential type mismatch: Joget field type 'radio' vs DB column type 'longtext'
- **farmerIncomePrograms.everOnISP**: Potential type mismatch: Joget field type 'radio' vs DB column type 'longtext'
- **farmerIncomePrograms.otherInputSupport**: Potential type mismatch: Joget field type 'radio' vs DB column type 'longtext'
- **farmerIncomePrograms.income_programs_key**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **farmerIncomePrograms.mainSourceIncome**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerIncomePrograms.income_sources**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerIncomePrograms.gainfulEmployment**: Potential type mismatch: Joget field type 'radio' vs DB column type 'longtext'
- **farmerIncomePrograms.governmentEmployed**: Potential type mismatch: Joget field type 'radio' vs DB column type 'longtext'
- **farmerIncomePrograms.parent_id**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **farmerIncomePrograms.relativeSupport**: Potential type mismatch: Joget field type 'radio' vs DB column type 'longtext'
- **farmerIncomePrograms.supportFrequency**: Potential type mismatch: Joget field type 'radio' vs DB column type 'longtext'
- **farmerIncomePrograms.supportType**: Potential type mismatch: Joget field type 'checkbox' vs DB column type 'longtext'
- **farmerIncomePrograms.supportProgram**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerIncomePrograms.creditDefault**: Potential type mismatch: Joget field type 'radio' vs DB column type 'longtext'
- **farmerIncomePrograms.everOnISP**: Potential type mismatch: Joget field type 'radio' vs DB column type 'longtext'
- **farmerIncomePrograms.otherInputSupport**: Potential type mismatch: Joget field type 'radio' vs DB column type 'longtext'
- **farmerLocation.district**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerLocation.agroEcologicalZone**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerLocation.residency_type**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerLocation.parent_id**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **farmerLocation.district**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerLocation.agroEcologicalZone**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerLocation.residency_type**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **farmerLocation.parent_id**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **householdMemberForm.farmer_id**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **householdMemberForm.sex**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **householdMemberForm.date_of_birth**: Potential type mismatch: Joget field type 'date' vs DB column type 'longtext'
- **householdMemberForm.relationship**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **householdMemberForm.orphanhoodStatus**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **householdMemberForm.participatesInAgriculture**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **householdMemberForm.disability**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **householdMemberForm.chronicallyIll**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **householdMemberForm.farmer_id**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **householdMemberForm.sex**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **householdMemberForm.date_of_birth**: Potential type mismatch: Joget field type 'date' vs DB column type 'longtext'
- **householdMemberForm.relationship**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **householdMemberForm.orphanhoodStatus**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **householdMemberForm.participatesInAgriculture**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **householdMemberForm.disability**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **householdMemberForm.chronicallyIll**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **livestockDetailsForm.farmer_id**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **livestockDetailsForm.livestockType**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'
- **livestockDetailsForm.farmer_id**: Potential type mismatch: Joget field type 'hidden' vs DB column type 'longtext'
- **livestockDetailsForm.livestockType**: Potential type mismatch: Joget field type 'select' vs DB column type 'longtext'

## Per-Form Validation Results

| Form | Total Fields | Validated | Failed | Status |
|------|--------------|-----------|--------|--------|
| `cropManagementForm` | 14 | 14 | 0 | ✓ |
| `farmerAgriculture` | 28 | 28 | 0 | ✓ |
| `farmerBasicInfo` | 26 | 26 | 0 | ✓ |
| `farmerCropsLivestock` | 19 | 17 | 2 | ⚠ |
| `farmerDeclaration` | 26 | 20 | 6 | ⚠ |
| `farmerHousehold` | 15 | 13 | 2 | ⚠ |
| `farmerIncomePrograms` | 42 | 42 | 0 | ✓ |
| `farmerLocation` | 40 | 40 | 0 | ✓ |
| `householdMemberForm` | 18 | 18 | 0 | ✓ |
| `livestockDetailsForm` | 8 | 8 | 0 | ✓ |