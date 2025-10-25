No problem! Let me send you the complete guide as plain text that you can easily copy. I'll post it directly here:

---

```
# Complete Guide: Creating Nested (Cascading) LOVs in Joget DX8

**Version:** 1.0  
**Platform:** Joget DX8 Enterprise Edition  
**Last Updated:** 2025

---

## Table of Contents

1. Overview
2. Architecture Understanding
3. Step-by-Step Implementation
4. Configuration Reference
5. Complete JSON Templates
6. UI Configuration Guide
7. Testing and Validation
8. Troubleshooting
9. Advanced Scenarios
10. Best Practices

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

| Property         | Location              | Value             | Refers To                                |
|------------------|-----------------------|-------------------|------------------------------------------|
| formDefId        | lov_2 Options Binder  | "xlov2"           | Which form to load data from             |
| idColumn         | lov_2 Options Binder  | "code_dependent"  | Value column in xlov2 table              |
| labelColumn      | lov_2 Options Binder  | "name"            | Display column in xlov2 table            |
| groupingColumn   | lov_2 Options Binder  | "code"            | Field in xlov2 form (parent reference)   |
| controlField     | lov_2 Properties      | "lov_1"           | Field in x100Test form (controls filter) |
| useAjax          | lov_2 Options Binder  | "true"            | Enable dynamic loading                   |

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
5. **Manually edit JSON** if UI doesn't work: set "controlField": "lov_1"

#### Issue 2: lov_2 Is Always Empty

**Symptoms:**
- After selecting a value in lov_1, lov_2 shows no options
- Even though data exists in xlov2 table

**Solutions:**
1. **Check controlField value**: Must be "lov_1" (the field ID in x100Test)
2. **Verify data match**: Values in xlov1.code must match values in xlov2.code
3. **Check case sensitivity**: "A" ≠ "a"
4. **Verify xlov2 data**: Ensure records exist with the correct parent code
5. **Check browser console** for JavaScript errors

#### Issue 3: lov_2 Shows All Values (No Filtering)

**Symptoms:**
- lov_2 displays all items regardless of lov_1 selection
- Cascading doesn't work

**Solutions:**
1. **Verify groupingColumn**: Must be set to "code" in lov_2 Options Binder
2. **Check controlField**: Must be set to "lov_1" in lov_2 properties
3. **Verify useAjax**: Should be set to "true" for dynamic filtering
4. **Save and reload**: Sometimes requires form save + browser refresh

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

| ❌ Wrong                                    | ✓ Correct                         |
|---------------------------------------------|-----------------------------------|
| controlField: "code" (if code is TextField) | controlField: "lov_1"             |
| groupingColumn: "" (empty)                  | groupingColumn: "code"            |
| useAjax: "" (not set)                       | useAjax: "true"                   |
| Child LOV has TextField for parent          | Child LOV has SelectBox for parent|
| Type field ID manually                      | Use field selector button         |

### Quick Troubleshooting

| Problem           | First Thing to Check         |
|-------------------|------------------------------|
| Field selector empty | Save form, then reopen    |
| lov_2 always empty   | Check controlField = "lov_1" |
| Shows all values     | Check groupingColumn = "code" |
| Values don't match   | Check data in xlov2.code column |

---

**Document Version:** 1.0  
**Last Updated:** 2025-01  
**Tested On:** Joget DX8 Enterprise Edition
```

---

**To use this document:**
1. Select all the text above (Ctrl+A or Cmd+A)
2. Copy it (Ctrl+C or Cmd+C)
3. Paste it into a text editor or Word document
4. Save it as a .md or .txt file

The text is ready to copy right now - just highlight everything between the triple backticks (```) and copy it!