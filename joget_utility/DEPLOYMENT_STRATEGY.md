# MDM Deployment Strategy & Best Practices

**Version:** 1.0
**Date:** October 27, 2025
**Status:** Production-Ready with Known Limitations

---

## Table of Contents
1. [Overview](#overview)
2. [Deployment Phases](#deployment-phases)
3. [Best Practices](#best-practices)
4. [Retry Logic](#retry-logic)
5. [Verification Steps](#verification-steps)
6. [Troubleshooting](#troubleshooting)
7. [Production Checklist](#production-checklist)

---

## Overview

This document outlines the recommended strategy for deploying Master Data Management (MDM) forms and data to Joget DX instances, based on lessons learned from production testing.

**Key Principle:** *Never assume success - always verify*

---

## Deployment Phases

### Phase 1: Pre-Deployment Validation

```bash
# 1. Validate all JSON form definitions
python joget_utility.py --validate-forms

# 2. Validate all CSV data files
python joget_utility.py --validate-data

# 3. Check Joget instance connectivity
python joget_utility.py --test
```

**Success Criteria:**
- All JSON files are valid Joget form definitions
- All CSV files match form field definitions
- Joget API is accessible and responding

---

### Phase 2: Form Creation

**Strategy:** Create all forms first, then populate data separately.

```bash
python joget_utility.py --deploy-master-data --forms-only
```

**Timing Considerations:**
- **Delay between forms:** 0.5-1 second (configurable)
- **After all forms created:** Wait 5-10 seconds for Joget processing

**Why:**
- Allows Joget to fully process form definitions
- Separates form creation errors from data errors
- Easier to debug and retry

**Expected Output:**
```
Phase 1: Creating Forms
  ✓ md01maritalStatus (1/37)
  ✓ md02language (2/37)
  ...
  ✓ md37collectionPoint (37/37)

Forms created: 37/37 (100%)
```

---

### Phase 3: API Verification

**Before populating data, verify all API endpoints exist.**

```python
# Automatic verification (built into deployment)
for form in forms:
    api_id = query_api_id_from_database(form.id)
    if not api_id:
        raise DeploymentError(f"API not found for {form.id}")
```

**Manual Verification:**
```sql
SELECT id, name FROM app_builder
WHERE id LIKE 'api_md%'
ORDER BY name;
```

**Expected:** 37 API endpoints (one per form)

---

### Phase 4: Data Population

**Strategy:** Populate with automatic retry logic.

```bash
python joget_utility.py --deploy-master-data --data-only
```

**Retry Pattern:**
```python
def populate_with_retry(form_metadata, csv_file, max_attempts=3):
    for attempt in range(max_attempts):
        result = populate_form_data(form_metadata, csv_file)

        if result['success']:
            logger.info(f"✓ {form_metadata['form_id']}: {result['records_posted']} records")
            return result

        if attempt < max_attempts - 1:
            delay = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
            logger.warning(f"Retry {attempt + 1}/{max_attempts} after {delay}s...")
            time.sleep(delay)
        else:
            logger.error(f"✗ {form_metadata['form_id']}: Failed after {max_attempts} attempts")
            return result
```

**Why Retry:**
- See [KNOWN_ISSUES.md](KNOWN_ISSUES.md) for transient deployment failures
- ~5% failure rate observed on first attempt
- 100% success rate on immediate retry

---

### Phase 5: Post-Deployment Verification

**Verify all data was populated correctly:**

```python
# Check database record counts
for form in forms:
    db_count = query_record_count(form.table_name)
    csv_count = count_csv_records(form.csv_file)

    if db_count != csv_count:
        logger.error(f"✗ {form.id}: Expected {csv_count}, got {db_count}")
    else:
        logger.info(f"✓ {form.id}: {db_count} records")
```

**Manual Verification:**
```sql
-- Quick count of all tables
SELECT
    TABLE_NAME,
    TABLE_ROWS
FROM information_schema.TABLES
WHERE TABLE_NAME LIKE 'app_fd_md%'
ORDER BY TABLE_NAME;

-- Accurate count (slower but reliable)
SELECT COUNT(*) FROM app_fd_md01maritalStatus;
SELECT COUNT(*) FROM app_fd_md02language;
-- ... etc
```

---

## Best Practices

### 1. Use Separate Phases
❌ **Don't:** Create form and populate data in single operation
✅ **Do:** Separate form creation from data population

**Reason:** Easier to identify failure point, allows retry of just data phase

---

### 2. Add Delays Between Operations
❌ **Don't:** Deploy all forms and data as fast as possible
✅ **Do:** Add configurable delays

```yaml
# config/master_data_deploy.yaml
options:
  api_call_delay: 0.5        # Delay between API calls (seconds)
  form_creation_delay: 1.0   # Delay after creating form
  data_population_delay: 2.0 # Delay before populating data
```

**Reason:** Gives Joget time to process asynchronous operations

---

### 3. Always Verify Before Proceeding
❌ **Don't:** Assume API creation succeeded because HTTP 200 returned
✅ **Do:** Query database to verify API ID exists

```python
# Bad
response = create_form(form_json)
if response.status_code == 200:
    populate_data()  # Might fail!

# Good
response = create_form(form_json)
if response.status_code == 200:
    time.sleep(2)
    api_id = query_api_id_from_db(form_id)
    if api_id:
        populate_data()
    else:
        raise Error("API not found after creation")
```

---

### 4. Implement Comprehensive Logging
✅ **Log everything:**
- Exact timing of each operation
- API request/response bodies
- Database query results
- Retry attempts with delays

```python
logger.info(f"[{timestamp}] Creating form: {form_id}")
logger.debug(f"Request: POST /formCreator/addWithFiles")
logger.debug(f"Form JSON: {json_content[:200]}...")
logger.info(f"[{timestamp}] Response: 200 OK")
logger.info(f"[{timestamp}] Waiting 2s for Joget processing...")
```

**Reason:** Essential for diagnosing intermittent failures

---

### 5. Respect Parent-Child Dependencies
✅ **Always deploy parent forms before children:**

```python
# Correct order
deployment_order = [
    # Parents first
    'md25equipmentCategory',
    'md27inputCategory',

    # Then children
    'md25generalTools',
    'md25irrigationEquipment',
    # ... other md25 children
    'md27fertilizer',
    'md27input',
    # ... other md27 children

    # Then independent forms
    'md01maritalStatus',
    # ... etc
]
```

**Reason:** Child forms have SelectBox elements referencing parent forms

---

### 6. Test Locally Before Production
✅ **Development → Staging → Production pipeline:**

1. **Local Joget instance:**
   - Drop all forms and data
   - Full deployment test
   - Verify all 37 forms work

2. **Staging environment:**
   - Mirror production configuration
   - Full deployment test
   - Performance testing under load

3. **Production:**
   - Deploy during maintenance window
   - Monitor logs in real-time
   - Have rollback plan ready

---

## Retry Logic

### When to Retry Automatically

✅ **Retry these errors:**
- "Missing required value" for field that doesn't exist
- Connection timeout/refused
- HTTP 500 Internal Server Error
- Record validation failed (might be transient)

❌ **Don't retry these errors:**
- HTTP 401 Unauthorized (fix credentials)
- HTTP 404 Not Found (form doesn't exist)
- Invalid JSON syntax (fix form definition)
- Missing required CSV column (fix data)

### Retry Implementation

```python
class RetryableError(Exception):
    """Errors that should trigger automatic retry"""
    pass

def is_retryable(error):
    retryable_patterns = [
        "Missing required value",
        "Connection refused",
        "Internal Server Error",
        "Timeout"
    ]
    return any(pattern in str(error) for pattern in retryable_patterns)

def deploy_with_retry(operation, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            result = operation()
            if result['success']:
                return result

            if not is_retryable(result.get('error', '')):
                # Non-retryable error, fail immediately
                return result

        except Exception as e:
            if not is_retryable(str(e)):
                raise

        if attempt < max_attempts - 1:
            delay = 2 ** attempt
            logger.warning(f"Retrying in {delay}s (attempt {attempt + 2}/{max_attempts})...")
            time.sleep(delay)

    return {'success': False, 'error': 'Max retries exceeded'}
```

---

## Verification Steps

### Form Verification Checklist

After each form creation:
- [ ] Form exists in `app_form` table
- [ ] Form JSON exists on filesystem (`/wflow/app_src/...`)
- [ ] API endpoint exists in `app_builder` table
- [ ] Form is accessible in Joget builder (manual spot check)

### Data Verification Checklist

After each data population:
- [ ] Physical table exists (`app_fd_{formId}`)
- [ ] Record count matches CSV row count
- [ ] No validation errors in logs
- [ ] Sample records contain expected data

### Full Deployment Verification Script

```bash
# Run after deployment
python verify_deployment.py

# Expected output:
# ✓ Forms: 37/37
# ✓ APIs: 37/37
# ✓ Tables: 37/37
# ✓ Records: 416/416
# ✓ Deployment: 100% success
```

---

## Troubleshooting

### Issue: Form Created but Data Population Fails

**Symptoms:**
- Form exists in database
- API endpoint found
- Data population returns validation errors

**Investigation:**
1. Check form in Joget builder - can it be opened?
2. Try adding record manually through UI
3. Check `catalina.out` for Joget errors
4. Query form definition from database

**Solution:**
- Retry data population immediately
- If still fails, drop form and recreate
- See [KNOWN_ISSUES.md](KNOWN_ISSUES.md) for similar cases

---

### Issue: API ID Not Found

**Symptoms:**
- Form created successfully
- Database query returns no API ID
- Data population cannot proceed

**Investigation:**
```sql
-- Check if API exists with different name
SELECT id, name FROM app_builder
WHERE appId = 'subsidyApplication'
AND appVersion = '1'
AND type = 'api'
ORDER BY dateCreated DESC;
```

**Solution:**
- Wait 5-10 seconds, query again
- Check Joget logs for API creation errors
- Manually create API endpoint in Joget if needed
- Verify FormCreator plugin configuration

---

### Issue: Phantom Validation Errors

**Symptoms:**
- Error references field that doesn't exist in form
- Example: "input_category_code: Missing required value"

**Investigation:**
1. Read form JSON definition - does field exist?
2. Check form in Joget builder - inspect validators
3. Clear Joget cache and retry

**Solution:**
- **Immediate:** Retry data population (usually works)
- **Long-term:** See [KNOWN_ISSUES.md](KNOWN_ISSUES.md) - requires investigation

---

## Production Checklist

### Pre-Deployment

- [ ] All CSV files reviewed and validated
- [ ] All JSON form definitions tested locally
- [ ] Parent-child dependencies identified and ordered
- [ ] Deployment script tested on staging environment
- [ ] Rollback plan documented
- [ ] Maintenance window scheduled
- [ ] Stakeholders notified

### During Deployment

- [ ] Monitor logs in real-time
- [ ] Check each phase completes before proceeding
- [ ] Verify record counts after data population
- [ ] Note any errors or retries
- [ ] Keep stakeholders updated

### Post-Deployment

- [ ] Run full verification script
- [ ] Manual spot check of key forms
- [ ] Test form accessibility in Joget UI
- [ ] Verify SelectBox dropdowns show correct options
- [ ] Document any issues encountered
- [ ] Confirm with stakeholders deployment success

---

## Configuration Reference

### Recommended Settings

```yaml
# config/master_data_deploy.yaml
options:
  # Processing
  validate_forms: true
  validate_data: true
  stop_on_error: false    # Continue to collect all errors

  # Timing
  api_call_delay: 0.5     # Between each API call
  form_processing_delay: 2.0  # After form creation

  # Retry
  max_retry_attempts: 3
  retry_backoff_base: 2   # Exponential: 2^0=1s, 2^1=2s, 2^2=4s

  # Logging
  log_api_details: true   # Debug mode
  log_file: ./logs/deployment.log
```

---

## Summary

**Golden Rules:**
1. **Separate phases:** Forms first, then data
2. **Add delays:** Give Joget time to process
3. **Always verify:** Query database, don't trust API responses
4. **Implement retry:** ~5% of operations may need retry
5. **Log everything:** Essential for debugging transient issues

**See Also:**
- [KNOWN_ISSUES.md](KNOWN_ISSUES.md) - Documented unexplained failures
- [DEPLOYMENT_RESULTS.md](DEPLOYMENT_RESULTS.md) - Full deployment test results
- [MD19_MERGE_NOTES.md](MD19_MERGE_NOTES.md) - Architecture decisions

---

**Document Version:** 1.0
**Last Updated:** October 27, 2025
**Maintainer:** Development Team
