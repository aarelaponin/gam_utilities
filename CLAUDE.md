# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a financial asset management (GAM) system for processing bank statements, extracting security transactions, and managing investment portfolios. The codebase processes Estonian bank statements to track securities trading activities.

## Commands

### Running scripts
- **Extract security transactions from bank statements**: `python get_secu_ops.py`
- **Add security details**: `python add_secu_details.py`
- **Get security valuations**: `python secu_values.py`
- **Run investment system**: `python investments.py`

### Dependencies
- **Install dependencies**: `pip install -r requirements.txt`
- **Key dependencies**: eodhd (for market data), pandas, yfinance

### Environment Setup
- **Required environment variable**: `EODHD_API_TOKEN` - API key for EODHD market data service

## Architecture

### Core Scripts
- `get_secu_ops.py`: Extracts security transactions from CSV bank statements, identifies tickers, aggregates transactions
- `add_secu_details.py`: Enriches security transaction data with additional details
- `secu_values.py`: Retrieves current market valuations for securities
- `investments.py`: Main investment system managing customers, securities, positions, and transactions
- `submit_config.py`: Configuration submission utility
- `searchapi.py` / `testapi.py`: EODHD API integration utilities

### Investment System Module (`investment_system/`)
Object-oriented investment tracking system with:
- `assets.py`: Security definitions
- `customers.py`: Customer account management
- `positions.py`: Position tracking
- `transactions.py`: Transaction records

### Data Structure (`data/`)
- `bank_statements/`: Input CSV files from banks
- `security_transactions/`: Processed transaction JSON files
- `security_valuations/`: Market valuation data
- `gl_config/`: Configuration files
- `security_statements/`: Security-specific statements
- `test_data/`, `test_transactions/`: Test data sets

## Key Implementation Details

### Transaction Processing Flow
1. Bank statement CSV → `get_secu_ops.py` → Extracts and aggregates security transactions
2. Ticker extraction via regex patterns for symbols in parentheses or ISIN codes
3. Transaction aggregation by date, ticker, and description
4. Output to JSON with metadata including operation counts

### Estonian Bank Statement Format
Expected CSV columns:
- `Selgitus`: Transaction description
- `Kuupäev`: Transaction date
- `Summa`: Transaction amount

### Security Identification
- Keywords: "securities", "stock", "fund" (case-insensitive)
- Excludes: "Currency exchange", "commission fee" transactions
- Ticker formats: (SYMBOL) or ISIN codes (12 characters starting with 2 letters)

## Debugging & Problem-Solving Methodology

**CRITICAL: Always use evidence-based analysis, never speculation**

### Evidence-First Approach
1. **Gather concrete evidence** before forming hypotheses:
   - Check actual database state with SQL queries
   - Examine filesystem with ls, find, grep commands
   - Read actual log files to see what executed
   - Trace code paths using line numbers and actual execution flow

2. **Verify every assumption**:
   - Don't assume a table exists - query it
   - Don't assume code executed - check logs
   - Don't assume files are in a location - list the directory
   - When user provides query results that contradict yours, investigate why

3. **When user says "ultrathink"**:
   - Current approach is speculation-based
   - Stop and gather more evidence
   - Trace actual execution paths in code
   - Look at facts, not theories

4. **Systematic debugging steps**:
   - State the observed behavior (with evidence)
   - Trace code execution path from logs
   - Identify the exact line where behavior diverges from expected
   - Propose fix based on code analysis, not guesses
   - Validate fix will address root cause before implementing

### Red Flags (Stop and Gather Evidence)
- Making claims about database state without recent query
- Assuming code behavior without checking logs
- Proposing fixes without identifying exact failure point
- Contradicting user-provided evidence
- Using phrases like "might be", "could be", "probably" without evidence

## Platform-First Development Protocol

### CRITICAL: Never Rush to Custom Solutions

**Before proposing ANY solution for platform-based work (Joget, Django, Spring, etc.):**

1. **Ask: "What's the platform's way?"**
   - Platforms have established patterns for common tasks
   - Custom code is usually wrong if platform provides the feature
   - Example: Joget stores metadata in database, don't create new mechanisms

2. **Search platform source code FIRST**:
   - For Joget: Check `/Users/aarelaponin/IdeaProjects/joget/jw-community`
   - Look for existing implementations of similar features
   - Find official patterns (e.g., API ID storage in `app_builder` table)
   - Document findings with file:line references

3. **Prefer platform APIs over custom code**:
   - Use platform's DAO layer (e.g., FormDataDao, BuilderDefinitionDao)
   - Query platform's database tables directly
   - Don't modify plugins unless absolutely necessary
   - Example: Query `app_builder` table instead of modifying FormCreator plugin

4. **Red Flags (Platform-Unfriendly Solutions)**:
   - Modifying plugins to add features platform already provides
   - Creating custom metadata storage when platform has it
   - Building parallel systems instead of using platform's architecture
   - Proposing code changes before searching platform documentation/source

### Investigation Phase Checklist

Before ANY implementation:
- [ ] Searched platform source code for similar patterns
- [ ] Found official platform implementation examples
- [ ] Documented findings with file paths and line numbers
- [ ] Verified platform doesn't already provide this feature
- [ ] Presented investigation results to user BEFORE coding
- [ ] Got user approval on approach (platform way vs custom)

## Joget DX Platform Specifics

### Architecture
- **OSGi-based**: Hot deployment - plugins reload without server restart
- **Dual storage**: Forms exist in BOTH database AND filesystem
  - Database: `app_form` table (form definitions)
  - Filesystem: `/wflow/app_src/{appId}/{appId}_{version}/forms/*.json`
- **Database**: MySQL on localhost:3308, database name: `jwdb`
- **Lazy table creation**: Physical tables (`app_fd_*`) created when form first accessed, not when defined

### Form Creation Process
1. Form definition registered in `app_form` table
2. Form JSON saved to filesystem
3. API endpoint created (optional)
4. **Physical table created lazily** - must be triggered explicitly

### Critical Joget API Behaviors
- `appService.getAppDefinition(appId, version)` creates TEMPORARY filesystem versions
  - Temp versions have timestamps like `subsidyApplication988377611038166`
  - Database uses version=1, but filesystem creates temp directory
  - **Solution**: Reuse existing AppDefinition when possible, don't load new ones
- `appService.storeFormData()` triggers table creation on first call
- `appService.getFormTableName()` returns table name but doesn't create it

### FormCreator Plugin
- Location: `/Users/aarelaponin/IdeaProjects/gam-plugins/form-creator`
- Build: `mvn clean package -DskipTests`
- Deploy: Copy JAR to `/Users/aarelaponin/joget-enterprise-linux-9.0.0/wflow/`
- Hot reload: OSGi detects and reloads automatically

## Master Data Deployment System

### Components
- **Utility**: `joget_utility/joget_utility.py`
- **Client**: `joget_utility/joget_client.py` (Joget API client)
- **Deployer**: `joget_utility/processors/master_data_deployer.py`
- **Config**: `config/master_data_deploy.yaml`

### Data Structure
- **Form definitions**: `data/metadata_forms/mdXX*.json`
- **Data files**: `data/metadata/mdXX*.csv`
- **Naming convention**: `mdXX<type>` (e.g., md01maritalStatus.json, md01maritalStatus.csv)

### Deployment Process
1. **Phase 1**: Create forms using FormCreator API
   - POST to `/jw/api/form/formCreator/addWithFiles`
   - Multipart upload with form definition JSON as file
   - Requires Referer header to extract formDefId
2. **Phase 2**: Populate data
   - POST to `/jw/api/form/{formId}/saveOrUpdate`
   - Requires forms to have physical tables created

### API Requirements
- **Referer header required**: Plugin extracts formDefId from Referer URL pattern
- **Multipart encoding**: form_definition_json must be uploaded as file, not JSON string
- **API credentials**: api_id and api_key in headers

## Investigation Before Implementation

### MANDATORY: Investigate BEFORE Proposing Solutions

**Never jump to solutions. Always investigate first.**

### Investigation Protocol

1. **Understand the Platform's Architecture**:
   - Read relevant platform source code
   - Identify where platform stores metadata (database tables, config files)
   - Find existing patterns for similar features
   - Document platform's approach with evidence

2. **Search Codebase for Patterns**:
   ```bash
   # Example: Finding how Joget stores API definitions
   grep -r "builderDefinition" joget/jw-community/
   grep -r "app_builder" joget/jw-community/
   ```
   - Look for DAO classes, service methods, database queries
   - Find usage examples in platform's own code
   - Document file:line references for patterns found

3. **Verify Database Schema**:
   - Query information_schema to see table structure
   - Examine existing data to understand format
   - Check indexes and constraints
   ```sql
   -- Example: Understanding app_builder table
   DESCRIBE app_builder;
   SELECT * FROM app_builder WHERE type='api' LIMIT 5;
   ```

4. **Present Investigation Results FIRST**:
   - Show what you found in platform source code
   - Explain platform's existing mechanisms
   - Propose solution based on platform patterns
   - Get user approval BEFORE writing any code

### Examples of Good Investigation

**Good Example (Joget API ID Query)**:
1. Searched jw-community for "app_builder"
2. Found AppServiceImpl.java uses `builderDefinitionDao`
3. Discovered API IDs stored in `app_builder` table
4. Verified with SQL: `SELECT id FROM app_builder WHERE type='api'`
5. Proposed: Query database instead of modifying plugin
6. **Result**: Correct solution using platform's way

**Bad Example (Modifying Plugin)**:
1. Assumed plugin needs to return API ID
2. Modified FormCreator.java to add return value
3. Built and deployed plugin
4. **Result**: Wrong approach, plugin doesn't need modification

## Code Modification Protocol

### Before Making ANY Code Changes

**ALWAYS explicitly state in the plan:**

1. **Which files will be modified** (full paths)
2. **Type of modification**:
   - Source code (.java, .py)
   - Configuration (.yaml, .properties)
   - Database schema
   - Filesystem structure
3. **Exact changes**: Show complete before/after diff
4. **Build/deployment implications**:
   - Will code need recompiling?
   - Will service need restarting?
   - Are changes backwards compatible?

### Plan Format for Code Changes

```markdown
## Files to Modify

### File: /path/to/file.java
**Type**: Source code modification
**Lines**: 340-360
**Before**:
```java
[exact current code]
```
**After**:
```java
[exact new code]
```
**Reason**: [evidence-based justification]

### Build/Deploy Steps
1. Rebuild: `mvn clean package`
2. Deploy: Copy JAR to /path/to/deployment
3. Reload: Automatic (OSGi) / Manual restart required
```

### Never Assume User Intent
- "Fix the bug" ≠ "Modify plugin source code"
- "Test it" ≠ "Deploy to production"
- Always ask explicitly if changes involve:
  - Modifying source code (not just config)
  - Rebuilding/recompiling
  - Deploying to running systems

## Evidence Verification Checklist

Before making conclusions, verify:

### Database State
- [ ] Queried actual table structure with DESCRIBE
- [ ] Counted actual rows with SELECT COUNT(*)
- [ ] Verified specific records exist with WHERE clauses
- [ ] Checked timestamps to confirm when data was created/modified
- [ ] If query returns unexpected results, investigate connection/credentials

### Filesystem State
- [ ] Listed directories with ls to confirm structure
- [ ] Used find to locate files, not assumed paths
- [ ] Checked file modification times with stat or ls -lt
- [ ] Verified file contents with cat/grep, not assumed

### Log Analysis
- [ ] Read actual log entries with tail/grep
- [ ] Matched log timestamps to operation times
- [ ] Identified which code paths executed based on logged messages
- [ ] Checked for ERROR/WARN messages
- [ ] If logs contradict theory, trust the logs

### Code Execution Path
- [ ] Traced execution with line numbers from logs
- [ ] Identified which methods returned true/false
- [ ] Found where execution stopped (last logged message)
- [ ] Checked if exceptions were caught and suppressed
- [ ] Verified assumptions about method behavior with code reading

### When Evidence Contradicts Theory
1. **Trust the evidence** (database, logs, filesystem)
2. Re-examine code to understand why behavior differs
3. Check for:
   - Hidden exception handling
   - Cache layers
   - Multiple database connections
   - OSGi class loading issues
   - Transaction rollbacks

### Testing Protocol

**CRITICAL: Tests must match real execution context**

#### Before Claiming Fix Works

1. **Test in Real Execution Context**:
   - Run from actual execution directory (not just project root)
   - Use actual configuration files (not test config)
   - Test with real data (not mock data)
   - Example: If script runs from `joget_utility/`, test from there, not project root

2. **End-to-End Verification**:
   - Deploy the fix
   - Run full deployment process
   - Check logs for success messages
   - Verify data actually populated in database
   - Query database to confirm results
   - **Only then** claim success

3. **Test Failure Analysis**:
   - If test passes but deployment fails → test was wrong
   - If test passes but user sees errors → test doesn't match reality
   - Rewrite test to match actual execution conditions
   - Re-test until test matches deployment behavior

4. **Common Testing Mistakes**:
   - Testing from wrong directory (Path.cwd() issues)
   - Testing with wrong environment variables (.env vs .env.3)
   - Testing with mock data that doesn't match real data structure
   - Testing individual functions without end-to-end integration
   - Claiming success based on unit tests without deployment verification

#### Test Evidence Requirements

Never claim fix works without:
- [ ] Full deployment logs showing success
- [ ] Database queries confirming data inserted
- [ ] Logs from actual execution directory
- [ ] Test from same environment as production
- [ ] User confirmation that issue is resolved

## Lessons from Past Failures

### Failure Case Studies

Understanding past mistakes to avoid repeating them.

#### Case Study 1: FormCreator Plugin Modification (WRONG APPROACH)

**What Happened**:
- Task: Get API ID for data population
- My approach: Modified FormCreator.java plugin to return API ID
- Built plugin, deployed, seemed to work
- **Reality**: Wrong approach - Joget already stores API IDs in database

**Root Cause**:
- Didn't search Joget source code first
- Didn't check if platform already provides this
- Jumped to custom solution without investigation
- Ignored "What's the Joget way?" question

**Correct Approach**:
1. Search jw-community for API ID storage
2. Find `app_builder` table stores all API definitions
3. Query database: `SELECT id FROM app_builder WHERE type='api' AND name=?`
4. Use platform's existing mechanism, don't modify plugin

**Lesson**: **Always investigate platform's way BEFORE coding custom solutions**

---

#### Case Study 2: Database Connection Path Resolution (INCOMPLETE TESTING)

**What Happened**:
- Task: Fix database connection for API ID queries
- Fixed `load_dotenv()` to use `override=True`
- Tested from project root - passed ✓
- Claimed success
- **Reality**: Deployment from `joget_utility/` failed - `.env.3` not found

**Root Cause**:
- Tested from wrong directory (project root)
- Didn't test from actual execution directory (`joget_utility/`)
- `Path.cwd()` returned different path than expected
- Test didn't match real deployment conditions

**Correct Approach**:
1. Test from ACTUAL execution directory
2. Verify path resolution: `Path.cwd()` vs `Path(__file__)`
3. Create test that simulates real deployment
4. Run full deployment as final verification
5. Only claim success after deployment logs show success

**Lesson**: **Tests must match real execution context, not idealized conditions**

---

### Key Takeaways

1. **Platform First**: Search platform source before coding custom solutions
2. **Investigate Before Implement**: Document platform patterns with evidence
3. **Test in Real Context**: Match actual execution environment
4. **No False Confidence**: Only claim success after deployment verification
5. **Evidence Over Theory**: Trust logs/database over assumptions