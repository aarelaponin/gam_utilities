# Joget Data Utility

A configurable utility for importing data to Joget DX8 applications via Form APIs.

## Features

- Import data from CSV and JSON files
- Batch processing for metadata endpoints (standard code/name fields)
- Configurable field mappings
- Dry-run and validation modes
- Configurable data directories
- Retry mechanism for failed requests

## Installation

```bash
cd joget_utility
pip install -r requirements.txt
```

## Configuration

1. Edit `config/joget.yaml` with your Joget server details:
   - Set your `base_url`
   - Configure your `default_api_key`
   - Update data paths if needed

2. For metadata batch processing, edit `config/metadata_batch.yaml`:
   - Add your endpoints with their API IDs
   - Specify the data files to import

## Usage

### Single Endpoint Import

```bash
# Import CSV file
python joget_utility.py --endpoint maritalStatus --input marital_status.csv

# Import JSON file with dry-run
python joget_utility.py --endpoint customer --input customers.json --dry-run

# Validate data without posting
python joget_utility.py --endpoint account --input accounts.csv --validate
```

### Metadata Batch Processing

```bash
# Process all metadata endpoints from batch file
python joget_utility.py --metadata-batch config/metadata_batch.yaml

# Use custom data directory
python joget_utility.py --metadata-batch batch.yaml --data-dir /path/to/data

# Dry run for testing
python joget_utility.py --metadata-batch config/metadata_batch.yaml --dry-run
```

### Other Commands

```bash
# List available endpoints
python joget_utility.py --list

# Test connection to Joget server
python joget_utility.py --test

# Skip confirmation prompts
python joget_utility.py --endpoint maritalStatus --input data.csv --yes
```

## Data File Formats

### CSV Format for Metadata (code/name)
```csv
code,name
SINGLE,Single
MARRIED,Married
DIVORCED,Divorced
```

### JSON Format for Metadata
```json
[
  {"code": "SINGLE", "name": "Single"},
  {"code": "MARRIED", "name": "Married"},
  {"code": "DIVORCED", "name": "Divorced"}
]
```

## Directory Structure

```
joget_utility/
├── config/
│   ├── joget.yaml           # Main configuration
│   └── metadata_batch.yaml  # Batch processing config
├── data/
│   ├── metadata/            # Metadata files
│   ├── csv/                 # CSV files
│   └── json/                # JSON files
└── logs/                    # Log files (created automatically)
```

## Adding New Endpoints

### For Metadata Endpoints (code/name fields)

Edit `config/joget.yaml`:
```yaml
metadata_endpoints:
  yourEndpoint:
    api_id: API-xxxx-xxxx-xxxx-xxxx
    description: "Your endpoint description"
```

### For Custom Endpoints

Edit `config/joget.yaml`:
```yaml
endpoints:
  yourEndpoint:
    api_id: API-xxxx-xxxx-xxxx-xxxx
    required_fields:
      - field1
      - field2
    field_mapping:
      source_field: target_field
```

## Form Generator

The utility includes an automatic form generator that creates Joget form JSON definitions from CSV metadata files.

### Generate Forms from CSV

```bash
# Generate all missing forms automatically
cd joget_utility
python3 test_batch_generate.py

# Generate specific form
python3 -m processors.form_generator \
    data/metadata/md99status.csv \
    data/metadata_forms/md99status.json
```

### Supported Form Types

**Simple Forms**: CSV with `code` + `name` → Basic TextField form
**Nested LOV**: CSV with parent reference column → Form with SelectBox
**Multi-field**: CSV with additional columns → Dynamic form with all fields

### Parent Reference Detection

The generator automatically detects parent references from column names:
- `*_category` (e.g., crop_category)
- `*_type` (e.g., irrigation_type)
- `*_group`
- `parent_*`

**Example**:
```csv
code,name,crop_category
maize,Maize,cereals
```
Generates form with SelectBox referencing the crop_category parent form.

See **docs/FORM_GENERATOR_GUIDE.md** for complete documentation.

## Master Data Deployment

The utility now supports deploying master data forms to a new Joget instance. This feature creates forms/tables and populates them with data in a two-phase process.

### Setup

1. Configure your deployment in `config/master_data_deploy.yaml`:
```yaml
deployment:
  base_url: http://localhost:8888/jw/api
  form_creator_api_id: API-xxxx-xxxx-xxxx
  form_creator_api_key: your-api-key

target_application:
  app_id: farmers_registry
  app_version: "1"

paths:
  forms_dir: ./data/metadata_forms
  data_dir: ./data/metadata
```

2. Ensure your form definitions are in `data/metadata_forms/` (e.g., `md01maritalStatus.json`)
3. Ensure your data files are in `data/metadata/` (e.g., `md01maritalStatus.csv`)

### Usage

**Deploy all master data (create forms + populate data):**
```bash
python joget_utility.py --deploy-master-data
```

**Deploy with custom configuration:**
```bash
python joget_utility.py --deploy-master-data --deploy-config my_config.yaml
```

**Dry run (test without making changes):**
```bash
python joget_utility.py --deploy-master-data --dry-run
```

**Create forms only (without populating data):**
```bash
python joget_utility.py --deploy-master-data --forms-only
```

**Populate data only (assumes forms already exist):**
```bash
python joget_utility.py --deploy-master-data --data-only
```

**Skip confirmation prompts:**
```bash
python joget_utility.py --deploy-master-data --yes
```

### Deployment Process

**Complete Workflow:**
1. **Create CSV data file** (e.g., `md99status.csv`)
2. **Generate form definition**: `python3 test_batch_generate.py`
3. **Deploy to Joget**: `python3 joget_utility.py --deploy-master-data`

**Phase 1: Form Creation**
- Auto-generates missing form JSONs from CSVs
- Validates table names (max 20 chars, collision detection)
- Creates forms via `/jw/api/form/formCreator` endpoint
- Creates API endpoints (when `create_api_endpoint: "yes"`)
- Creates datalist and userview (when `create_crud: "yes"`)

**Phase 2: Data Population**
- Queries database for API IDs
- Matches forms to CSV data files
- Transforms and validates data
- Posts data to form endpoints
- Verifies record counts

### Configuration Options

```yaml
# Form creation options
form_options:
  create_api_endpoint: "yes"      # Create API endpoints for forms
  api_name_prefix: "api_"         # Prefix for API names
  use_original_form_id: true      # Use form_id from JSON

# Processing options
options:
  validate_forms: true            # Validate form definitions
  validate_data: true             # Validate data files
  dry_run: false                  # Simulate without API calls
  stop_on_error: false            # Continue on errors
  populate_data: true             # Populate data after creating forms
  batch_size: 100                 # Records per batch
  api_call_delay: 0.5             # Delay between API calls (seconds)
```

### Form and Data File Naming Convention

Files should follow the pattern `mdXX<metadata-type>`:
- Form definitions: `md01maritalStatus.json`, `md02language.json`, etc.
- Data files: `md01maritalStatus.csv`, `md02language.csv`, etc.

The utility automatically matches forms to data files by name.

### Example Deployment Output

```
======================================================================
Starting Master Data Deployment
======================================================================

Target Application: farmers_registry
Target Version: 1
Forms to deploy: 20

----------------------------------------------------------------------
PHASE 1: Creating Forms
----------------------------------------------------------------------

[1/20] Processing: md01maritalStatus.json
✓ Created form: maritalStatus

[2/20] Processing: md02language.json
✓ Created form: language

...

----------------------------------------------------------------------
PHASE 2: Populating Data
----------------------------------------------------------------------

[1/20] Populating: maritalStatus
✓ Posted 6 records to maritalStatus

[2/20] Populating: language
✓ Posted 3 records to language

...

======================================================================
DEPLOYMENT SUMMARY
======================================================================
Total forms processed: 20
Forms created: 20
Forms failed: 0
Records posted: 150
Records failed: 0
======================================================================
```

## Troubleshooting

- **Connection errors**: Check your `base_url` in config
- **Authentication errors**: Verify your `api_id` and `api_key`
- **File not found**: Check data paths in configuration
- **Validation errors**: Run with `--validate` to check data before posting
- **Form creation fails**: Verify the formCreator API credentials and endpoint
- **Data population fails**: Ensure forms were created successfully first
- **Naming mismatch**: Ensure form and data files use the same base name (e.g., `md01foo.json` and `md01foo.csv`)
- **Form creation succeeds but Joget rejects form**: Check SelectBox structure - must use `optionsBinder` property, not `options` array. Regenerate form with `test_batch_generate.py --overwrite`