# Complete Guide: Creating Nested (Cascading) LOVs in Joget DX8

**Version:** 1.0  
**Platform:** Joget DX8 Enterprise Edition  
**Last Updated:** 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Understanding](#architecture-understanding)
3. [Step-by-Step Implementation](#step-by-step-implementation)
4. [Configuration Reference](#configuration-reference)
5. [Complete JSON Templates](#complete-json-templates)
6. [UI Configuration Guide](#ui-configuration-guide)
7. [Testing and Validation](#testing-and-validation)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Scenarios](#advanced-scenarios)
10. [Best Practices](#best-practices)

---

## Overview

### What are Nested LOVs?

Nested (or Cascading) Lists of Values are dropdown fields where the options in one dropdown depend on the selection made in another dropdown. For example:
- Select "Country" → See only states in that country
- Select "Category" → See only items in that category
- Select "Department" → See only employees in that department

### Key Concepts

**Three Forms Required:**
1. **Parent LOV Form** - Stores master data (categories, countries, etc.)
2. **Child LOV Form** - Stores dependent data with a reference to parent
3. **Main Form** - Uses both LOVs with cascading functionality

**Critical Requirement:**
The Child LOV Form MUST have a **SelectBox field** that loads data from the Parent LOV Form. This is what enables the cascading relationship.

---

## Architecture Understanding

### Data Flow Diagram

```
┌──────────────────┐
│   Parent LOV     │  (e.g., xlov1 - Categories)
│   Table: xlov1   │
├──────────────────┤
│ code  | name     │
│ A     | Cat A    │
│ B     | Cat B    │
└──────────────────┘
        ↓
        │ Referenced by SelectBox in Child LOV
        ↓
┌──────────────────────────────┐
│   Child LOV                  │  (e.g., xlov2 - Items)
│   Table: xlov2               │
├──────────────────────────────┤
│ code_dependent | code | name │
│ A1            | A    | Item1 │ ← "code" is a SelectBox!
│ A2            | A    | Item2 │
│ B1            | B    | Item3 │
└──────────────────────────────┘
        ↓
        │ Both used in Main Form
        ↓
┌────────────────────────────────────────────┐
│   Main Form (e.g., x100Test)               │
├────────────────────────────────────────────┤
│                                            │
│  lov_1 (SelectBox - Parent)                │
│    ├─ Loads from: xlov1                    │
│    └─ Shows: code → name                   │
│                                            │
│  lov_2 (SelectBox - Child with Cascading) │
│    ├─ Loads from: xlov2                    │
│    ├─ Shows: code_dependent → name         │
│    ├─ groupingColumn: "code"               │
│    └─ controlField: "lov_1"                │
│                                            │
└────────────────────────────────────────────┘
```

### How Cascading Works

1. User selects a value in `lov_1` (e.g., "A")
2. The `controlField` property links `lov_2` to `lov_1`
3. Joget filters xlov2 table WHERE `code` = "A"
4. `lov_2` shows only matching records (A1, A2)

---

## Step-by-Step Implementation

### STEP 1: Create Parent LOV Form

**Form Details:**
- Form ID: `xlov1`
- Table Name: `xlov1`
- Purpose: Stores master categories

**Fields to Add:**

```
1. TextField - "code"
   - ID: code
   - Label: Code
   - Validator: DuplicateValueValidator
     * Form: xlov1
     * Field: code
     * Mandatory: Yes
   - Purpose: Unique identifier for each category

2. TextField - "name"
   - ID: name
   - Label: Name
   - Purpose: Display name for the category
```

**Sample Data to Create:**

| code | name       |
|------|------------|
| A    | Category A |
| B    | Category B |
| C    | Category C |

### STEP 2: Create Child LOV Form

**Form Details:**
- Form ID: `xlov2`
- Table Name: `xlov2`
- Purpose: Stores items linked to parent categories

**Fields to Add:**

```
1. TextField - "code_dependent"
   - ID: code_dependent
   - Label: Code Dependent
   - Validator: DuplicateValueValidator
     * Form: xlov2
     * Field: code_dependent
     * Mandatory: Yes
   - Purpose: Unique identifier for each item

2. SelectBox - "code" ⭐ CRITICAL FIELD
   - ID: code
   - Label: Parent Code
   - Load Data From: Form Data
   - Form Options Binder:
     * Form: xlov1
     * Value Column (idColumn): code
     * Label Column: name
     * Add Empty Option: Yes
   - Validator: Default Validator
     * Mandatory: Yes
   - Purpose: Stores which parent category this item belongs to

3. TextField - "name"
   - ID: name
   - Label: Name
   - Purpose: Display name for the item
```

**Sample Data to Create:**

| code_dependent | code | name    |
|----------------|------|---------|
| A1             | A    | Item A1 |
| A2             | A    | Item A2 |
| B1             | B    | Item B1 |
| B2             | B    | Item B2 |
| C1             | C    | Item C1 |

**Important Note:**
When creating records in xlov2, you will select the parent category from the "code" dropdown. This creates the relationship between parent and child.

### STEP 3: Create Main Form with Cascading

**Form Details:**
- Form ID: `x100Test`
- Table Name: `x100_test_form`
- Purpose: Main form that uses cascading LOVs

**Fields to Add:**

```
1. SelectBox - "lov_1" (Parent Dropdown)
   - ID: lov_1
   - Label: LOV 1 (Parent)
   - Load Data From: Form Data
   - Form Options Binder:
     * Form: xlov1
     * Value Column (idColumn): code
     * Label Column: name
     * Grouping Column: [empty]
     * Add Empty Option: Yes
     * Use AJAX: No
   - Control Field: [empty]
   - Purpose: Parent selector that controls child dropdown

2. SelectBox - "lov_2" (Child Dropdown with Cascading)
   - ID: lov_2
   - Label: LOV 2 (Child)
   - Load Data From: Form Data
   - Form Options Binder:
     * Form: xlov2
     * Value Column (idColumn): code_dependent
     * Label Column: name
     * Grouping Column: code ⭐
     * Add Empty Option: Yes
     * Use AJAX for cascade options: Yes ✓
   - Advanced Options:
     * Control Field: lov_1 ⭐
   - Purpose: Child selector that filters based on parent selection
```

---

## Configuration Reference

### Critical Properties Explained

#### groupingColumn
- **Location:** In the child SelectBox (lov_2) Options Binder
- **Value:** "code"
- **What it means:** The field ID in the xlov2 form that stores the parent reference
- **Must match:** The SelectBox field ID in the xlov2 form

#### controlField
- **Location:** In the child SelectBox (lov_2) Advanced Options
- **Value:** "lov_1"
- **What it means:** The field ID in the CURRENT form (x100Test) that controls the filtering
- **Must match:** The parent SelectBox field ID in the main form

#### idColumn
- **Location:** In the Options Binder configuration
- **What it means:** The column that stores the actual value (what gets saved to database)
- **For lov_1:** "code" (from xlov1 table)
- **For lov_2:** "code_dependent" (from xlov2 table)

#### labelColumn
- **Location:** In the Options Binder configuration
- **What it means:** The column that gets displayed to the user
- **For both:** "name"

#### useAjax
- **Location:** In the Options Binder configuration
- **Value:** "true"
- **What it means:** Options are loaded dynamically via AJAX instead of all at once
- **Benefit:** Better performance, especially with large datasets

### Property Mapping Table

| Property | Location | Value | Refers To |
|----------|----------|-------|-----------|
| **formDefId** | lov_2 Options Binder | "xlov2" | Which form to load data from |
| **idColumn** | lov_2 Options Binder | "code_dependent" | Value column in xlov2 table |
| **labelColumn** | lov_2 Options Binder | "name" | Display column in xlov2 table |
| **groupingColumn** | lov_2 Options Binder | "code" | Field in xlov2 form that stores parent reference |
| **controlField** | lov_2 Properties | "lov_1" | Field in x100Test form that controls filtering |
| **useAjax** | lov_2 Options Binder | "true" | Enable dynamic loading |

### The Matching Logic

```
When user selects in lov_1:
  lov_1.value = "A"
       ↓
  controlField links lov_2 to lov_1
       ↓
  lov_2.groupingColumn = "code"
       ↓
  Filters xlov2 WHERE code = "A"
       ↓
  Returns records: A1, A2
       ↓
  lov_2 displays: "Item A1", "Item A2"
```

---

## Complete JSON Templates

### Parent LOV Form (xlov1)

```json
{
    "className": "org.joget.apps.form.model.Form",
    "properties": {
        "id": "xlov1",
        "name": "X LOV 1",
        "tableName": "xlov1",
        "loadBinder": {
            "className": "org.joget.apps.form.lib.WorkflowFormBinder"
        },
        "storeBinder": {
            "className": "org.joget.apps.form.lib.WorkflowFormBinder"
        },
        "description": ""
    },
    "elements": [
        {
            "className": "org.joget.apps.form.model.Section",
            "properties": {
                "label": "Section",
                "id": "section1"
            },
            "elements": [
                {
                    "className": "org.joget.apps.form.model.Column",
                    "properties": {
                        "width": "100%"
                    },
                    "elements": [
                        {
                            "className": "org.joget.apps.form.lib.TextField",
                            "properties": {
                                "id": "code",
                                "label": "code",
                                "validator": {
                                    "className": "org.joget.apps.form.lib.DuplicateValueValidator",
                                    "properties": {
                                        "formDefId": "xlov1",
                                        "fieldId": "code",
                                        "errorDuplicateMsg": "",
                                        "mandatory": "true",
                                        "regex": "",
                                        "errorFormatMsg": ""
                                    }
                                },
                                "requiredSanitize": "",
                                "maxlength": "",
                                "encryption": "",
                                "readonly": "",
                                "size": "",
                                "workflowVariable": "",
                                "style": "",
                                "placeholder": "",
                                "iconIncluded": false,
                                "value": "",
                                "readonlyLabel": "",
                                "storeNumeric": "",
                                "disableIncrementDecrementArrow": ""
                            }
                        },
                        {
                            "className": "org.joget.apps.form.lib.TextField",
                            "properties": {
                                "id": "name",
                                "label": "Name",
                                "validator": {
                                    "className": "",
                                    "properties": {}
                                },
                                "requiredSanitize": "",
                                "maxlength": "",
                                "encryption": "",
                                "readonly": "",
                                "size": "",
                                "workflowVariable": "",
                                "style": "",
                                "placeholder": "",
                                "iconIncluded": false,
                                "value": "",
                                "readonlyLabel": "",
                                "storeNumeric": "",
                                "disableIncrementDecrementArrow": ""
                            }
                        }
                    ]
                }
            ]
        }
    ]
}
```

### Child LOV Form (xlov2)

```json
{
    "className": "org.joget.apps.form.model.Form",
    "properties": {
        "id": "xlov2",
        "name": "X LOV 2",
        "tableName": "xlov2",
        "loadBinder": {
            "className": "org.joget.apps.form.lib.WorkflowFormBinder"
        },
        "storeBinder": {
            "className": "org.joget.apps.form.lib.WorkflowFormBinder"
        },
        "description": ""
    },
    "elements": [
        {
            "className": "org.joget.apps.form.model.Section",
            "properties": {
                "label": "Section",
                "id": "section1"
            },
            "elements": [
                {
                    "className": "org.joget.apps.form.model.Column",
                    "properties": {
                        "width": "100%"
                    },
                    "elements": [
                        {
                            "className": "org.joget.apps.form.lib.TextField",
                            "properties": {
                                "id": "code_dependent",
                                "label": "code_dependent",
                                "validator": {
                                    "className": "org.joget.apps.form.lib.DuplicateValueValidator",
                                    "properties": {
                                        "formDefId": "xlov2",
                                        "fieldId": "code_dependent",
                                        "errorDuplicateMsg": "",
                                        "mandatory": "true",
                                        "regex": "",
                                        "errorFormatMsg": ""
                                    }
                                },
                                "encryption": "",
                                "readonly": "",
                                "style": "",
                                "readonlyLabel": "",
                                "storeNumeric": "",
                                "iconIncluded": false,
                                "value": "",
                                "maxlength": "",
                                "requiredSanitize": "",
                                "placeholder": "",
                                "size": "",
                                "workflowVariable": "",
                                "disableIncrementDecrementArrow": ""
                            }
                        },
                        {
                            "className": "org.joget.apps.form.lib.SelectBox",
                            "properties": {
                                "id": "code",
                                "label": "code",
                                "optionsBinder": {
                                    "className": "org.joget.apps.form.lib.FormOptionsBinder",
                                    "properties": {
                                        "formDefId": "xlov1",
                                        "idColumn": "code",
                                        "labelColumn": "name",
                                        "groupingColumn": "",
                                        "extraCondition": "",
                                        "addEmptyOption": "true",
                                        "emptyLabel": "",
                                        "useAjax": "",
                                        "cacheInterval": ""
                                    }
                                },
                                "validator": {
                                    "className": "org.joget.apps.form.lib.DefaultValidator",
                                    "properties": {
                                        "mandatory": "true",
                                        "type": "",
                                        "message": ""
                                    }
                                },
                                "readonly": "",
                                "multiple": "",
                                "readonlyLabel": "",
                                "iconIncluded": false,
                                "options": [],
                                "value": "",
                                "controlField": "",
                                "size": "",
                                "workflowVariable": ""
                            }
                        },
                        {
                            "className": "org.joget.apps.form.lib.TextField",
                            "properties": {
                                "id": "name",
                                "label": "Name",
                                "validator": {
                                    "className": "",
                                    "properties": {}
                                },
                                "requiredSanitize": "",
                                "maxlength": "",
                                "encryption": "",
                                "readonly": "",
                                "size": "",
                                "workflowVariable": "",
                                "style": "",
                                "placeholder": "",
                                "iconIncluded": false,
                                "value": "",
                                "readonlyLabel": "",
                                "storeNumeric": "",
                                "disableIncrementDecrementArrow": ""
                            }
                        }
                    ]
                }
            ]
        }
    ]
}
```

### Main Form with Cascading (x100Test)

```json
{
    "className": "org.joget.apps.form.model.Form",
    "properties": {
        "id": "x100Test",
        "name": "X100 Test Form",
        "tableName": "x100_test_form",
        "loadBinder": {
            "className": "org.joget.apps.form.lib.WorkflowFormBinder"
        },
        "storeBinder": {
            "className": "org.joget.apps.form.lib.WorkflowFormBinder"
        },
        "description": ""
    },
    "elements": [
        {
            "className": "org.joget.apps.form.model.Section",
            "properties": {
                "label": "Section",
                "id": "section1"
            },
            "elements": [
                {
                    "className": "org.joget.apps.form.model.Column",
                    "properties": {
                        "width": "100%"
                    },
                    "elements": [
                        {
                            "className": "org.joget.apps.form.lib.SelectBox",
                            "properties": {
                                "id": "lov_1",
                                "label": "lov 1",
                                "optionsBinder": {
                                    "className": "org.joget.apps.form.lib.FormOptionsBinder",
                                    "properties": {
                                        "formDefId": "xlov1",
                                        "idColumn": "code",
                                        "labelColumn": "name",
                                        "groupingColumn": "",
                                        "extraCondition": "",
                                        "addEmptyOption": "true",
                                        "emptyLabel": "",
                                        "useAjax": "",
                                        "cacheInterval": ""
                                    }
                                },
                                "validator": {
                                    "className": "",
                                    "properties": {}
                                },
                                "readonly": "",
                                "multiple": "",
                                "readonlyLabel": "",
                                "iconIncluded": false,
                                "options": [],
                                "value": "",
                                "controlField": "",
                                "size": "",
                                "workflowVariable": ""
                            }
                        },
                        {
                            "className": "org.joget.apps.form.lib.SelectBox",
                            "properties": {
                                "id": "lov_2",
                                "label": "lov 2",
                                "optionsBinder": {
                                    "className": "org.joget.apps.form.lib.FormOptionsBinder",
                                    "properties": {
                                        "formDefId": "xlov2",
                                        "idColumn": "code_dependent",
                                        "labelColumn": "name",
                                        "groupingColumn": "code",
                                        "extraCondition": "",
                                        "addEmptyOption": "true",
                                        "emptyLabel": "",
                                        "useAjax": "true",
                                        "cacheInterval": ""
                                    }
                                },
                                "validator": {
                                    "className": "",
                                    "properties": {}
                                },
                                "readonly": "",
                                "multiple": "",
                                "readonlyLabel": "",
                                "iconIncluded": false,
                                "options": [],
                                "value": "",
                                "controlField": "lov_1",
                                "size": "",
                                "workflowVariable": ""
                            }
                        }
                    ]
                }
            ]
        }
    ]
}
```

---

## UI Configuration Guide

### Part 1: Create Parent LOV (5 minutes)

1. **Navigate to App Composer**
   - Open your application
   - Go to Forms section
   - Click "New Form"

2. **Configure Form**
   - Form ID: `xlov1`
   - Form Name: `X LOV 1`
   - Table Name: `xlov1`

3. **Add Fields**
   - Drag TextField → Set ID: `code`, Label: `Code`
   - Add DuplicateValueValidator to `code` field
   - Drag TextField → Set ID: `name`, Label: `Name`

4. **Save Form**

5. **Add Sample Data**
   - Preview form and add records:
     - A | Category A
     - B | Category B
     - C | Category C

### Part 2: Create Child LOV (10 minutes)

1. **Create New Form**
   - Form ID: `xlov2`
   - Form Name: `X LOV 2`
   - Table Name: `xlov2`

2. **Add TextField: code_dependent**
   - ID: `code_dependent`
   - Label: `code_dependent`
   - Add DuplicateValueValidator

3. **Add SelectBox: code** (CRITICAL!)
   - Drag SelectBox element
   - ID: `code`
   - Label: `code`
   
4. **Configure SelectBox Options Binder**
   - Click on the SelectBox
   - Go to "Load Data From" tab
   - Choose: "Form Data"
   - Click "Configure Form Data"
   - Form: Select `xlov1`
   - Value Column: `code`
   - Label Column: `name`
   - Add Empty Option: Yes (checked)

5. **Add Validator to SelectBox**
   - Go to "Validation" tab
   - Choose: "Default Validator"
   - Mandatory: Yes (checked)

6. **Add TextField: name**
   - ID: `name`
   - Label: `Name`

7. **Save Form**

8. **Add Sample Data**
   - Preview form and add records:
     - code_dependent: A1 | code: A | name: Item A1
     - code_dependent: A2 | code: A | name: Item A2
     - code_dependent: B1 | code: B | name: Item B1

### Part 3: Create Main Form with Cascading (15 minutes)

1. **Create New Form**
   - Form ID: `x100Test`
   - Form Name: `X100 Test Form`
   - Table Name: `x100_test_form`

2. **Add First SelectBox: lov_1 (Parent)**
   - Drag SelectBox
   - ID: `lov_1`
   - Label: `lov 1`

3. **Configure lov_1 Options Binder**
   - Load Data From: Form Data
   - Form: `xlov1`
   - Value Column: `code`
   - Label Column: `name`
   - Add Empty Option: Yes

4. **Add Second SelectBox: lov_2 (Child)**
   - Drag SelectBox
   - ID: `lov_2`
   - Label: `lov 2`

5. **Configure lov_2 Options Binder**
   - Load Data From: Form Data
   - Form: `xlov2`
   - Value Column: `code_dependent`
   - Label Column: `name`
   - **Grouping Column: `code`** ⭐
   - Add Empty Option: Yes
   - **Use AJAX for cascade options: Yes** ✓

6. **SAVE THE FORM** (Critical step!)

7. **Configure Control Field**
   - Reopen the form for editing
   - Click on `lov_2` SelectBox
   - Go to "Advanced Options" tab
   - Look for "Field ID to control available options based on Grouping"
   - **Click the field selector icon** (don't type manually)
   - Select: `lov_1`

8. **Save Form Again**

### Important UI Tips

- **Always save after setting groupingColumn** before trying to set controlField
- **Use the field selector** (the icon button) instead of typing field IDs manually
- **The field selector will only show SelectBox/Radio/Checkbox fields** - TextFields won't appear
- If the field selector is empty, save the form and reopen it

---

## Testing and Validation

### Test Checklist

- [ ] Parent LOV (xlov1) has sample data
- [ ] Child LOV (xlov2) has sample data with parent references
- [ ] Main form (x100Test) has both SelectBoxes
- [ ] groupingColumn is set to "code"
- [ ] controlField is set to "lov_1"
- [ ] useAjax is set to "true"

### Manual Testing Steps

1. **Preview the Main Form (x100Test)**

2. **Test Cascading Behavior**
   - Initially, lov_2 should be empty or show all values
   - Select "Category A" in lov_1
   - lov_2 should update to show only "Item A1" and "Item A2"
   - Select "Category B" in lov_1
   - lov_2 should update to show only "Item B1" and "Item B2"

3. **Test Data Persistence**
   - Select values in both dropdowns
   - Submit the form
   - Edit the record
   - Both values should be correctly loaded

4. **Test Edge Cases**
   - Clear lov_1 selection → lov_2 should reset
   - Select a category with no items → lov_2 should be empty
   - Select a category with items → lov_2 should show them

### Expected Behavior

| lov_1 Selection | Expected lov_2 Options |
|-----------------|------------------------|
| (empty)         | All items or empty     |
| Category A      | Item A1, Item A2       |
| Category B      | Item B1, Item B2       |
| Category C      | Item C1                |

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: Field Selector Shows No Fields

**Symptoms:**
- When configuring lov_2, the "Field ID to control available options" dropdown is empty
- Can't select lov_1 from the dropdown

**Solutions:**
1. **Save the form first** after setting groupingColumn
2. **Close and reopen** the lov_2 configuration
3. **Verify lov_1 exists** and is a SelectBox (not TextField)
4. **Clear browser cache** and try again
5. **Manually edit JSON** if UI doesn't work: set `"controlField": "lov_1"`

#### Issue 2: lov_2 Is Always Empty

**Symptoms:**
- After selecting a value in lov_1, lov_2 shows no options
- Even though data exists in xlov2 table

**Solutions:**
1. **Check controlField value**: Must be `"lov_1"` (the field ID in x100Test)
2. **Verify data match**: Values in xlov1.code must match values in xlov2.code
3. **Check case sensitivity**: "A" ≠ "a"
4. **Verify xlov2 data**: Ensure records exist with the correct parent code
5. **Check browser console** for JavaScript errors

#### Issue 3: lov_2 Shows All Values (No Filtering)

**Symptoms:**
- lov_2 displays all items regardless of lov_1 selection
- Cascading doesn't work

**Solutions:**
1. **Verify groupingColumn**: Must be set to `"code"` in lov_2 Options Binder
2. **Check controlField**: Must be set to `"lov_1"` in lov_2 properties
3. **Verify useAjax**: Should be set to `"true"` for dynamic filtering
4. **Save and reload**: Sometimes requires form save + browser refresh

#### Issue 4: Wrong Values Are Displayed

**Symptoms:**
- lov_2 shows items from wrong category
- Data appears mixed up

**Solutions:**
1. **Check idColumn vs labelColumn**: 
   - idColumn: What gets saved (code_dependent)
   - labelColumn: What gets displayed (name)
2. **Verify groupingColumn**: Must match the SelectBox field ID in xlov2
3. **Check data integrity**: Ensure xlov2.code values are correct

#### Issue 5: Cascading Works but Data Doesn't Save

**Symptoms:**
- Filtering works correctly
- But selected values don't save to database

**Solutions:**
1. **Check idColumn**: Must be set correctly (code_dependent for lov_2)
2. **Verify table structure**: Ensure x100_test_form table has lov_2 column
3. **Check StoreBinder**: Must be WorkflowFormBinder
4. **Verify permissions**: Database write permissions

### Debugging Checklist

When cascading doesn't work, check in this order:

1. **Form Structure**
   - [ ] xlov2 has a SelectBox field named "code"
   - [ ] The SelectBox in xlov2 loads from xlov1
   - [ ] x100Test has both lov_1 and lov_2 SelectBoxes

2. **Configuration Values**
   - [ ] lov_2 groupingColumn = "code"
   - [ ] lov_2 controlField = "lov_1"
   - [ ] lov_2 useAjax = "true"
   - [ ] lov_2 idColumn = "code_dependent"
   - [ ] lov_2 labelColumn = "name"

3. **Data Integrity**
   - [ ] xlov1 has records with code values (A, B, C)
   - [ ] xlov2 has records with matching code values
   - [ ] Values are exact matches (no spaces, same case)

4. **Technical Issues**
   - [ ] Form saved after configuration changes
   - [ ] Browser cache cleared
   - [ ] No JavaScript errors in console
   - [ ] Correct Joget version (DX8)

---

## Advanced Scenarios

### Three-Level Cascading (Country → State → City)

For hierarchical data with three or more levels:

#### LOV Structure

```
xlov_country (Level 1)
├─ code (TextField)
└─ name (TextField)

xlov_state (Level 2)
├─ code (TextField)
├─ country (SelectBox → xlov_country)
└─ name (TextField)

xlov_city (Level 3)
├─ code (TextField)
├─ state (SelectBox → xlov_state)
└─ name (TextField)

Main Form
├─ country_field (SelectBox)
├─ state_field (SelectBox - cascades on country_field)
└─ city_field (SelectBox - cascades on state_field)
```

#### Configuration

**state_field SelectBox:**
```json
{
    "groupingColumn": "country",
    "controlField": "country_field",
    "useAjax": "true"
}
```

**city_field SelectBox:**
```json
{
    "groupingColumn": "state",
    "controlField": "state_field",
    "useAjax": "true"
}
```

### Multiple Parent Dependencies

For scenarios where a child depends on multiple parent fields:

#### Example: Products filtered by Category AND Brand

**Product LOV Form:**
```
xlov_product
├─ code (TextField)
├─ category (SelectBox → xlov_category)
├─ brand (SelectBox → xlov_brand)
└─ name (TextField)
```

**Main Form Configuration:**
```json
{
    "groupingColumn": "category;brand",
    "controlField": "category_field;brand_field",
    "useAjax": "true"
}
```

**Important:**
- Use semicolons (;) to separate multiple values
- Order must match exactly in both properties
- Click field selectors, only type the semicolon

### Dynamic Filtering with Extra Conditions

Add additional SQL filtering using extraCondition:

```json
{
    "formDefId": "xlov2",
    "idColumn": "code_dependent",
    "labelColumn": "name",
    "groupingColumn": "code",
    "extraCondition": "WHERE active = 'Y' AND deleted = 'N'",
    "useAjax": "true"
}
```

---

## Best Practices

### Design Principles

1. **Keep LOV Forms Simple**
   - Only include necessary fields
   - Use clear, descriptive names
   - Add validation for unique identifiers

2. **Use Meaningful IDs**
   - Form IDs: Prefix with purpose (e.g., `lov_`, `x_`)
   - Field IDs: Use lowercase with underscores
   - Avoid generic names like "field1", "dropdown"

3. **Data Organization**
   - Create parent LOVs before child LOVs
   - Populate parent data before child data
   - Maintain referential integrity

4. **Performance Optimization**
   - Always use `useAjax: "true"` for cascading
   - Keep LOV tables indexed on code columns
   - Limit the number of records in LOVs (< 1000 recommended)

### Development Workflow

1. **Plan Your Hierarchy**
   - Draw out the relationship diagram
   - Identify parent-child relationships
   - List all required fields

2. **Build Bottom-Up**
   - Create leaf LOVs first
   - Add parent LOVs next
   - Build main forms last

3. **Test Incrementally**
   - Test each LOV independently
   - Test parent-child relationships
   - Test cascading in main form

4. **Document Your LOVs**
   - Keep a list of all LOV forms
   - Document the relationships
   - Note any special filtering rules

### Naming Conventions

#### Form Naming
```
Parent LOV: xlov_[entity]        (e.g., xlov_category)
Child LOV:  xlov_[entity]        (e.g., xlov_product)
Main Form:  x[number]_[purpose]  (e.g., x100_order_form)
```

#### Field Naming
```
Unique ID:     code, [entity]_code        (e.g., product_code)
Display Name:  name, [entity]_name        (e.g., product_name)
Parent Ref:    [parent]_code              (e.g., category_code)
SelectBox:     lov_[entity], [entity]_sel (e.g., lov_category)
```

### Common Patterns

#### Pattern 1: Simple Parent-Child
```
Category → Products
Department → Employees
Country → Cities
```

#### Pattern 2: Multi-Level Hierarchy
```
Region → Country → State → City
Division → Department → Team → Employee
```

#### Pattern 3: Multiple Parents
```
(Category + Brand) → Products
(Department + Role) → Employees
```

### Maintenance Tips

1. **Regular Data Validation**
   - Check for orphaned records (child without parent)
   - Verify data integrity
   - Clean up unused LOV entries

2. **Version Control**
   - Export LOV forms regularly
   - Keep JSON backups
   - Document changes

3. **Testing After Changes**
   - Test cascading after any LOV modification
   - Verify existing forms still work
   - Check for broken relationships

### Security Considerations

1. **Access Control**
   - Limit who can edit LOV forms
   - Protect LOV data with appropriate permissions
   - Use separate LOV management forms

2. **Data Validation**
   - Always use DuplicateValueValidator on codes
   - Add mandatory validators where needed
   - Validate parent-child relationships

---

## Quick Reference Card

### Essential Configuration

```
Parent SelectBox (lov_1):
├─ formDefId: "xlov1"
├─ idColumn: "code"
├─ labelColumn: "name"
├─ groupingColumn: ""
└─ controlField: ""

Child SelectBox (lov_2):
├─ formDefId: "xlov2"
├─ idColumn: "code_dependent"
├─ labelColumn: "name"
├─ groupingColumn: "code"      ← Field in xlov2 form
├─ controlField: "lov_1"        ← Field in current form
└─ useAjax: "true"
```

### Common Mistakes

| ❌ Wrong | ✓ Correct |
|---------|-----------|
| controlField: "code" (if code is TextField) | controlField: "lov_1" |
| groupingColumn: "" (empty) | groupingColumn: "code" |
| useAjax: "" (not set) | useAjax: "true" |
| Child LOV has TextField for parent | Child LOV has SelectBox for parent |
| Type field ID manually | Use field selector button |

### Quick Troubleshooting

| Problem | First Thing to Check |
|---------|---------------------|
| Field selector empty | Save form, then reopen |
| lov_2 always empty | Check controlField = "lov_1" |
| Shows all values | Check groupingColumn = "code" |
| Values don't match | Check data in xlov2.code column |

---

## Additional Resources

### Joget Documentation
- Knowledge Base: https://dev.joget.org/community/display/DX8/
- Dynamic Cascading: https://dev.joget.org/community/display/DX8/Dynamic+Cascading+Drop-Down+List
- AJAX Cascading: https://dev.joget.org/community/display/DX8/Ajax+Cascading+Drop-Down+List

### Support Channels
- Joget Forum: https://dev.joget.org/community/display/FORUM/
- GitHub: https://github.com/jogetworkflow/jw-community

---

## Appendix: Complete Working Example

This example demonstrates a working cascading LOV setup for a product catalog:

### Scenario
- **Categories**: Electronics, Clothing, Food
- **Products**: Each belongs to one category
- **Order Form**: Select category first, then product

### Data Structure

**xlov_category:**
| code | name        |
|------|-------------|
| ELEC | Electronics |
| CLOT | Clothing    |
| FOOD | Food        |

**xlov_product:**
| code | category | name            |
|------|----------|-----------------|
| LP01 | ELEC     | Laptop          |
| PH01 | ELEC     | Phone           |
| SH01 | CLOT     | Shirt           |
| PN01 | CLOT     | Pants           |
| AP01 | FOOD     | Apple           |
| BR01 | FOOD     | Bread           |

### Expected Behavior

1. User selects "Electronics" → Shows "Laptop" and "Phone"
2. User selects "Clothing" → Shows "Shirt" and "Pants"
3. User selects "Food" → Shows "Apple" and "Bread"

---

**Document Version:** 1.0  
**Last Updated:** 2025-01  
**Tested On:** Joget DX8 Enterprise Edition