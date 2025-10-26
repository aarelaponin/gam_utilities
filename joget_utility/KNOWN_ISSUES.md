# Known Issues - MDM Deployment System

**Date:** October 27, 2025
**Status:** CRITICAL - Production Impact
**Priority:** HIGH - Requires Investigation

---

## Overview

During full MDM deployment testing, we encountered **two unexplained transient failures** that were resolved by simply retrying the data population. While retry worked, **the root cause remains unknown** and could impact production deployments.

---

## Issue 1: md27inputCategory - Form Builder Corruption

### Symptoms
- Form created successfully via FormCreator API
- API endpoint registered correctly
- Physical table `app_fd_md27inputCategory` created
- **Form could NOT be opened in Joget Form Builder**
- Attempting to add record manually through Joget UI: Error
- Data population via API: Failed with validation errors

### Initial Deployment Result
- Form created: ✓
- API found: ✓
- Data posted: **0/8 records (100% failure)**

### Evidence
1. **JSON definition was correct**:
   - Simple form with 6 TextFields
   - No SelectBox, no form references
   - WorkflowFormBinder for load/store
   - Identical structure to working forms (e.g., md01maritalStatus)

2. **Manual form creation worked**:
   - Created same form manually in Joget builder
   - Uploaded exact same JSON definition
   - Form opened correctly, data posted successfully

3. **Automatic redeploy worked**:
   - Dropped form, API, table
   - Ran automated deployment again
   - Form created correctly, all 8 records posted

### Conclusion
**Form definition was somehow corrupted or incomplete during initial API creation.**
Root cause unknown. Simple retry resolved the issue.

---

## Issue 2: md30targetGroup - Phantom Required Field Error

### Symptoms
- Form created successfully via FormCreator API
- API endpoint registered correctly
- Physical table `app_fd_md30targetGroup` created
- Data population: **Failed with mysterious validation error**

### Error Message
```json
{
  "input_category_code": "Missing required value"
}
```

### Initial Deployment Result
- Form created: ✓
- API found: ✓
- Data posted: **0/10 records (100% failure)**

### Evidence
1. **Field `input_category_code` DOES NOT EXIST in form definition**:
   - Form has only 3 fields: `code`, `name`, `description`
   - No SelectBox elements
   - No validators with `input_category_code`
   - JSON definition verified line-by-line

2. **CSV data structure correct**:
   - Headers: `code,name,description`
   - 10 clean records
   - No extra fields
   - Matches form definition exactly

3. **Retry with identical data worked**:
   - No code changes
   - No data changes
   - No form changes
   - Simply re-ran data population: **10/10 records posted successfully**

### Conclusion
**Joget applied wrong validation rules or used corrupted cached form state.**
Root cause unknown. Simple retry resolved the issue.

---

## Possible Root Causes

### 1. Race Condition
**Hypothesis:** Form creation API returns success before Joget fully processes the form.

**Evidence:**
- FormCreator API returns immediately after saving JSON to database
- Physical table creation is lazy (happens on first access)
- Form definition parsing might be asynchronous
- API endpoint registration might lag behind form creation

**Test:** Add delay between form creation and data population.

---

### 2. Cache Invalidation Issues
**Hypothesis:** Joget caches form definitions, new forms might use stale cache.

**Evidence:**
- Joget uses multiple cache layers (AppDefinition, FormDefinition, etc.)
- `appService.getAppDefinition()` creates temporary filesystem copies
- Cache invalidation might not happen immediately after form creation
- md30 error suggests wrong form definition was cached

**Test:** Force cache clear between operations or use API calls that bypass cache.

---

### 3. OSGi Bundle Reloading
**Hypothesis:** Joget uses OSGi, bundle reloads might cause inconsistent state.

**Evidence:**
- FormCreator plugin hot-reloads via OSGi
- During reload, forms might be in transition state
- Timing of bundle reload vs. form access is unpredictable

**Test:** Monitor OSGi bundle state during deployment.

---

### 4. Transaction Isolation
**Hypothesis:** Database transactions not immediately visible across connections.

**Evidence:**
- Form created in one database transaction
- Data population queries API ID in separate transaction
- MySQL default isolation level (REPEATABLE READ) might hide uncommitted changes
- Physical table creation happens outside main transaction

**Test:** Add explicit transaction commits or use READ COMMITTED isolation.

---

### 5. Form Definition Processing Error
**Hypothesis:** JSON parsing/validation fails silently and uses default/previous form.

**Evidence:**
- md30 validation error referenced non-existent field
- Suggests form definition wasn't fully parsed
- Joget might have fallen back to template or cached version

**Test:** Verify form definition in database immediately after creation.

---

## Production Risk Assessment

### Risk Level: **HIGH**

**Impact:**
- Deployments may fail unpredictably
- Failures are silent until data population phase
- No clear error messages (phantom validation errors)
- Retry might not always work in production

**Frequency:**
- Observed: 2 out of 38 forms (5.3% failure rate)
- Could be higher under load or with concurrent deployments

**Detection:**
- Failures only detected during data population
- Forms appear created successfully (false positive)
- Requires database query to verify actual state

**Mitigation Difficulty:**
- Root cause unknown
- Cannot reproduce reliably
- No configuration setting to prevent
- Requires code-level retry logic

---

## Recommended Mitigation Strategies

### 1. Immediate (Current Implementation)
✅ **Manual retry** - If deployment fails, retry data population
- Works for both observed issues
- No code changes required
- Relies on operator intervention

### 2. Short-term (Recommended)
🔧 **Add automatic retry logic to deployment code**
- Exponential backoff (1s, 2s, 4s delays)
- Max 3 retry attempts
- Log each retry for monitoring
- Fail loudly after exhausting retries

### 3. Medium-term (Investigation Required)
🔍 **Add verification steps between operations**
- After form creation: verify form in database
- Query form definition to ensure it's complete
- Test form accessibility before data population
- Add configurable delays between operations

### 4. Long-term (Architectural Fix)
🏗️ **Work with Joget to identify root cause**
- Report issue to Joget support with detailed logs
- Request timing guarantees for API operations
- Explore transaction isolation settings
- Consider alternative deployment approach (bulk import?)

---

## Workarounds

### For Manual Deployment
1. Deploy forms first (without data)
2. **Wait 5-10 seconds** for Joget to process
3. Verify forms are accessible in builder
4. Then populate data
5. If data population fails: **retry immediately**

### For Automated Deployment
```python
# Recommended pattern
for form in forms_to_deploy:
    create_form(form)
    time.sleep(2)  # Allow Joget to process

    for attempt in range(3):
        result = populate_data(form)
        if result.success:
            break
        if attempt < 2:
            time.sleep(2 ** attempt)  # Exponential backoff
        else:
            log_error(f"Failed after 3 attempts: {form.id}")
```

---

## Testing Recommendations

### Reproduce the Issue
1. Deploy all 37 forms in rapid succession
2. Immediately populate data without delays
3. Monitor failure rate
4. Vary timing to identify threshold

### Stress Testing
1. Deploy multiple forms concurrently
2. Test under Joget server load
3. Test with slow database connection
4. Test after Joget restart vs. running server

### Diagnostic Logging
1. Log exact timing of all operations
2. Query database state before/after each step
3. Capture Joget server logs during deployment
4. Monitor OSGi bundle states

---

## References

- **DEPLOYMENT_RESULTS.md**: Full deployment test results
- **test_md27_full_deploy.py**: Successful retry test for md27
- **test_md30_data.py**: Successful retry test for md30

---

## Status & Next Steps

**Current Status:** Issues documented, workaround identified (retry)

**Required Actions:**
1. ❌ **Root cause identification** - Requires deeper investigation
2. ❌ **Automatic retry logic** - Should be added to deployment code
3. ❌ **Verification script** - Check deployment health automatically
4. ❌ **Joget support ticket** - Report issue with full details

**Owner:** Development Team
**Target Resolution:** Q4 2025

---

**⚠️ WARNING:** Do not consider these issues "solved" just because retry worked.
The underlying problem persists and could cause production deployment failures.
