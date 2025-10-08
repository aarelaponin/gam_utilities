# Joget Data Utility - Comprehensive User Guide

## Table of Contents
1. [Overview](#overview)
2. [Installation & Setup](#installation--setup)
3. [Understanding the Basics](#understanding-the-basics)
4. [Configuration Guide](#configuration-guide)
5. [Usage Scenarios](#usage-scenarios)
6. [Data File Formats](#data-file-formats)
7. [Command Reference](#command-reference)
8. [Troubleshooting](#troubleshooting)
9. [Examples & Best Practices](#examples--best-practices)

---

## Overview

The Joget Data Utility is a command-line tool designed specifically for importing data into Joget DX8 applications through their Form API. It simplifies the process of bulk data imports, especially for metadata tables (lookup tables with code/name pairs).

### Key Capabilities
- **Single Endpoint Import**: Import data to one Joget form endpoint at a time
- **Metadata Batch Processing**: Import multiple metadata tables in one go
- **Format Support**: Handles both CSV and JSON input files
- **Field Mapping**: Transform field names between source files and Joget requirements
- **Validation**: Check data integrity before sending to Joget
- **Dry Run**: Preview what will be sent without actually posting
- **Configurable Paths**: Organize your data files in custom directories

### What This Tool Does NOT Do
- Does not export/download data from Joget
- Does not support Excel files (only CSV and JSON)
- Does not manage multiple environments (dev/staging/prod) - single configuration only
- Does not provide progress bars or real-time batch tracking
- Does not modify existing records (only creates new ones)

---

## Installation & Setup

### Prerequisites
- Python 3.6 or higher
- Network access to your Joget server

### Step 1: Install Dependencies
```bash
cd joget_utility
pip install -r requirements.txt
```

This installs:
- `requests` - For HTTP communication with Joget
- `PyYAML` - For reading configuration files

### Step 2: Configure Joget Connection
Edit `config/joget.yaml`:

```yaml
# MANDATORY: Update these values
base_url: http://localhost:8080/jw/api/form  # Your Joget server URL
default_api_key: 3e56045fe2394b5ba8fb148e74edc029  # Your default API key

# OPTIONAL: Customize data directories
data_paths:
  default: ./data
  metadata: ./data/metadata
  csv: ./data/csv
  json: ./data/json
```

### Step 3: Test Connection
```bash
python joget_utility.py --test
```

If successful, you'll see: `✓ Connection successful`

---

## Understanding the Basics

### What is a Metadata Endpoint?
Metadata endpoints are Joget forms that store simple lookup data with two fields:
- **code**: The identifier (e.g., "US", "SINGLE", "DEPT001")
- **name**: The description (e.g., "United States", "Single", "Sales Department")

Examples: countries, currencies, marital statuses, departments, document types

### What is a Custom Endpoint?
Custom endpoints are Joget forms with any field structure. You define:
- Which fields are required
- How to map your data fields to Joget fields

Examples: customer records, account information, transaction data

### API Credentials
Each Joget form endpoint requires:
- **API ID**: Unique identifier for the endpoint (e.g., `API-aa7cb1c2-791f-4134-a27e-83264138e744`)
- **API Key**: Authentication token (can be shared across endpoints)

To find these in Joget:
1. Go to your app in Joget
2. Open the form you want to import to
3. Go to Properties → Advanced → API Settings

---

## Configuration Guide

### Main Configuration File (`config/joget.yaml`)

```yaml
# Server Configuration
base_url: http://localhost:8080/jw/api/form
default_api_key: 3e56045fe2394b5ba8fb148e74edc029

# Data Directory Configuration
data_paths:
  default: ./data           # Default location for data files
  metadata: ./data/metadata # Metadata-specific files
  csv: ./data/csv          # CSV files
  json: ./data/json        # JSON files

# Connection Settings (usually don't need to change)
connection:
  timeout: 30      # Request timeout in seconds
  retry_count: 3   # Number of retries on failure
  retry_delay: 2   # Seconds between retries

# Metadata Endpoints (standard code/name structure)
metadata_endpoints:
  maritalStatus:  # Endpoint name (used in commands)
    api_id: API-aa7cb1c2-791f-4134-a27e-83264138e744
    description: "Marital status types"

  employmentType:
    api_id: API-bb8dc2d3-892f-5245-b38f-94375249f855
    description: "Employment types"

# Custom Endpoints (flexible field structure)
endpoints:
  customer:
    api_id: API-dd1fe4f5-ab4h-7467-d51h-b6597471h077
    required_fields:  # Fields that must have values
      - customerId
      - customerName
    field_mapping:    # Map source fields to target fields
      id: customerId         # source "id" → target "customerId"
      name: customerName
      email: customerEmail
      phone: customerPhone
```

### Batch Configuration File (`config/metadata_batch.yaml`)

Used for processing multiple metadata endpoints at once:

```yaml
metadata_batch:
  # Each entry processes one endpoint
  - api_id: API-aa7cb1c2-791f-4134-a27e-83264138e744
    endpoint: maritalStatus    # Joget form endpoint name
    file: marital_status.csv   # Data file (relative to data_paths)
    description: "Marital status types"

  - api_id: API-bb8dc2d3-892f-5245-b38f-94375249f855
    endpoint: employmentType
    file: employment_types.json  # Can mix CSV and JSON
    description: "Employment types"

options:
  stop_on_error: false  # Continue even if one endpoint fails
  validate_first: true  # Check all data before processing
  dry_run: false       # Set true to test without posting
```

---

## Usage Scenarios

### Scenario 1: Import a Single Metadata Table

You have a CSV file with country codes:

**countries.csv:**
```csv
code,name
US,United States
UK,United Kingdom
FR,France
```

**Command:**
```bash
python joget_utility.py --endpoint country --input countries.csv
```

### Scenario 2: Import Multiple Metadata Tables at Once

You have several lookup tables to import:

1. Create/edit `config/metadata_batch.yaml` with all endpoints
2. Place data files in `data/metadata/` directory
3. Run:
```bash
python joget_utility.py --metadata-batch config/metadata_batch.yaml
```

### Scenario 3: Import Customer Data with Field Mapping

You have customer data with different field names:

**customers.json:**
```json
[
  {"id": "001", "name": "John Doe", "email": "john@example.com"},
  {"id": "002", "name": "Jane Smith", "email": "jane@example.com"}
]
```

**Configure in `joget.yaml`:**
```yaml
endpoints:
  customer:
    api_id: API-xxxxx
    field_mapping:
      id: customerId
      name: customerName
      email: customerEmail
```

**Command:**
```bash
python joget_utility.py --endpoint customer --input customers.json
```

### Scenario 4: Validate Before Importing

Check data without posting:
```bash
python joget_utility.py --endpoint maritalStatus --input data.csv --validate
```

### Scenario 5: Test Without Making Changes

Preview what would be sent:
```bash
python joget_utility.py --endpoint department --input departments.csv --dry-run
```

---

## Data File Formats

### CSV Format

**For Metadata (code/name):**
```csv
code,name
SINGLE,Single
MARRIED,Married
DIVORCED,Divorced
WIDOWED,Widowed
```

**For Custom Endpoints:**
```csv
customerId,customerName,customerEmail,customerPhone
001,John Doe,john@example.com,555-0001
002,Jane Smith,jane@example.com,555-0002
```

**Notes:**
- First row must contain column headers
- Use commas as separators (tool auto-detects other delimiters)
- Empty rows are ignored
- Quotes are optional unless field contains commas

### JSON Format

**For Metadata (code/name):**
```json
[
  {"code": "USD", "name": "US Dollar"},
  {"code": "EUR", "name": "Euro"},
  {"code": "GBP", "name": "British Pound"}
]
```

**Alternative JSON Structure (also supported):**
```json
{
  "data": [
    {"code": "USD", "name": "US Dollar"},
    {"code": "EUR", "name": "Euro"}
  ]
}
```

**For Custom Endpoints:**
```json
[
  {
    "customerId": "001",
    "customerName": "ACME Corp",
    "customerEmail": "contact@acme.com",
    "customerPhone": "555-0100"
  }
]
```

---

## Command Reference

### Basic Commands

| Command | Description |
|---------|-------------|
| `--endpoint NAME --input FILE` | Import data to a single endpoint |
| `--metadata-batch FILE` | Process multiple metadata endpoints from batch file |
| `--list` | Show all configured endpoints |
| `--test` | Test connection to Joget server |

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--dry-run` | `-d` | Preview without posting data |
| `--validate` | `-v` | Check data validity only |
| `--yes` | `-y` | Skip confirmation prompts |
| `--stop-on-error` | | Stop if any record fails |
| `--verbose` | | Show detailed output |
| `--config FILE` | `-c` | Use alternate config file |
| `--api-key KEY` | | Override default API key |
| `--data-dir PATH` | | Override data directory |

### Examples

```bash
# Basic import
python joget_utility.py --endpoint maritalStatus --input status.csv

# Import with automatic confirmation
python joget_utility.py --endpoint country --input countries.json --yes

# Batch process with dry run
python joget_utility.py --metadata-batch batch.yaml --dry-run

# Use different data directory
python joget_utility.py --endpoint dept --input depts.csv --data-dir /path/to/data

# Override API key for specific import
python joget_utility.py --endpoint secure_data --input data.csv --api-key special_key_123

# Validate all files in batch without posting
python joget_utility.py --metadata-batch batch.yaml --validate
```

---

## Troubleshooting

### Common Issues and Solutions

#### "Connection failed"
- **Check**: Is Joget server running?
- **Check**: Is `base_url` correct in config?
- **Check**: Can you access Joget from browser?
- **Try**: `curl http://your-server:8080/jw` to test connectivity

#### "Authentication failed: HTTP 401"
- **Check**: Is API key correct?
- **Check**: Is API ID correct for this endpoint?
- **In Joget**: Admin → Manage Apps → Your App → API Key Management

#### "Endpoint not found: HTTP 404"
- **Check**: Is endpoint name spelled correctly?
- **Check**: Does the form exist in Joget?
- **Check**: Is the form ID in Joget same as endpoint name?

#### "File not found"
- **Check**: File exists in configured data directory?
- **Check**: File extension is .csv or .json?
- **Try**: Use absolute path: `--input /full/path/to/file.csv`

#### "Missing required fields"
- **Check**: Do all records have required fields?
- **Check**: Are field names spelled correctly?
- **Run**: `--validate` to see which fields are missing

#### "Invalid JSON file"
- **Check**: Is JSON properly formatted?
- **Validate**: Use online JSON validator
- **Common issue**: Missing commas between objects

#### No data imported (0 records)
- **Check**: Is file empty?
- **Check**: For CSV, does first row contain headers?
- **Check**: Are all rows empty or contain only spaces?

### Debug Mode

For detailed troubleshooting:
```bash
python joget_utility.py --endpoint test --input data.csv --verbose --dry-run
```

This shows:
- Exactly what data is being read
- How it's being transformed
- What would be sent to Joget

---

## Examples & Best Practices

### Best Practices

1. **Always Test First**
   ```bash
   # Step 1: Validate
   python joget_utility.py --endpoint mydata --input data.csv --validate

   # Step 2: Dry run
   python joget_utility.py --endpoint mydata --input data.csv --dry-run

   # Step 3: Import
   python joget_utility.py --endpoint mydata --input data.csv
   ```

2. **Organize Your Data Files**
   ```
   data/
   ├── metadata/
   │   ├── countries.csv
   │   ├── currencies.csv
   │   └── departments.json
   ├── csv/
   │   └── customers.csv
   └── json/
       └── accounts.json
   ```

3. **Use Batch Processing for Related Data**
   - Group related metadata imports in one batch file
   - Run them together to ensure consistency

4. **Keep Backups**
   - Always keep original data files
   - Version control your configuration files

5. **Document Your Mappings**
   - Add descriptions to endpoints in config
   - Comment complex field mappings

### Complete Example: Setting Up a New Joget App

Let's say you're setting up a new HR application:

**Step 1: Create your data files**

`data/metadata/departments.csv`:
```csv
code,name
HR,Human Resources
IT,Information Technology
FIN,Finance
```

`data/metadata/employment_types.csv`:
```csv
code,name
FT,Full Time
PT,Part Time
CONTRACT,Contractor
```

**Step 2: Configure batch file**

`config/hr_metadata.yaml`:
```yaml
metadata_batch:
  - api_id: API-dept-xxxx
    endpoint: departments
    file: departments.csv
    description: "Company departments"

  - api_id: API-emptype-xxxx
    endpoint: employmentTypes
    file: employment_types.csv
    description: "Employment types"

options:
  stop_on_error: true
  validate_first: true
```

**Step 3: Import all at once**
```bash
# Test first
python joget_utility.py --metadata-batch config/hr_metadata.yaml --dry-run

# Then import
python joget_utility.py --metadata-batch config/hr_metadata.yaml --yes
```

### Quick Reference Card

Save this for quick lookup:

```bash
# List what's available
python joget_utility.py --list

# Test connection
python joget_utility.py --test

# Single import (with confirmation)
python joget_utility.py -e ENDPOINT -i FILE

# Single import (auto-confirm)
python joget_utility.py -e ENDPOINT -i FILE -y

# Batch import
python joget_utility.py -m config/metadata_batch.yaml

# Validate only
python joget_utility.py -e ENDPOINT -i FILE -v

# Dry run
python joget_utility.py -e ENDPOINT -i FILE -d
```

---

## Need More Help?

1. **Check the README.md** for quick setup instructions
2. **Review config/joget.yaml** for all configuration options
3. **Run with --verbose** for detailed error messages
4. **Check Joget server logs** for API-related issues

Remember: This tool is specifically designed for Joget DX8 Form APIs. It won't work with other Joget APIs or different versions without modification.