# Joget Utility - Quick Reference

Quick reference guide for common testing and development tasks with `joget_utility.py`.

## Table of Contents
- [Ad-Hoc Form Creation](#ad-hoc-form-creation)
- [Batch Deployment](#batch-deployment)
- [Form Generation](#form-generation)
- [Data Import](#data-import)
- [Testing & Validation](#testing--validation)

---

## Ad-Hoc Form Creation

### Create a single form (basic)
```bash
cd joget_utility
python3 joget_utility.py \
  --create-form ../doc_forms/myForm.json \
  --app-id subsidyApplication \
  --port 8888
```

### Create form on different environments
```bash
# Port 8080 (default Joget installation)
python3 joget_utility.py --create-form test.json --app-id myApp --port 8080

# Port 8888 (test environment)
python3 joget_utility.py --create-form test.json --app-id myApp --port 8888

# Port 9999 (another environment)
python3 joget_utility.py --create-form test.json --app-id myApp --port 9999
```

### Dry run first (always a good practice!)
```bash
python3 joget_utility.py \
  --create-form ../doc_forms/myForm.json \
  --app-id subsidyApplication \
  --port 8888 \
  --dry-run
```

### Skip confirmation prompts
```bash
python3 joget_utility.py \
  --create-form ../doc_forms/myForm.json \
  --app-id subsidyApplication \
  --port 8888 \
  --yes
```

### Override form properties
```bash
python3 joget_utility.py \
  --create-form test.json \
  --app-id myApp \
  --port 8888 \
  --form-id custom_form_id \
  --form-name "Custom Form Name" \
  --table-name custom_table_name
```

### Create form without API or CRUD
```bash
# No API endpoint
python3 joget_utility.py \
  --create-form test.json \
  --app-id myApp \
  --port 8888 \
  --no-create-api

# No CRUD interface
python3 joget_utility.py \
  --create-form test.json \
  --app-id myApp \
  --port 8888 \
  --no-create-crud

# Neither API nor CRUD
python3 joget_utility.py \
  --create-form test.json \
  --app-id myApp \
  --port 8888 \
  --no-create-api \
  --no-create-crud
```

### Supported Form Definition Formats
The `--create-form` command supports three JSON formats:

1. **Direct form definition** (from form generator):
   ```json
   {
     "className": "org.joget.apps.form.model.Form",
     "properties": {...}
   }
   ```

2. **CRUD export format** (from Joget export):
   ```json
   {
     "date": "...",
     "code": "200",
     "message": "{\"components\":{\"form\":{...}}}"
   }
   ```

3. **Extracted form**:
   ```json
   {
     "definition": {
       "className": "org.joget.apps.form.model.Form",
       "properties": {...}
     }
   }
   ```

---

## Batch Deployment

### Deploy all metadata forms
```bash
cd joget_utility
python3 joget_utility.py --deploy-master-data
```

### Deploy with custom config
```bash
python3 joget_utility.py \
  --deploy-master-data \
  --deploy-config config/master_data_deploy-8080.yaml
```

### Deploy forms only (no data)
```bash
python3 joget_utility.py --deploy-master-data --forms-only
```

### Populate data only (forms already exist)
```bash
python3 joget_utility.py --deploy-master-data --data-only
```

### Dry run deployment
```bash
python3 joget_utility.py --deploy-master-data --dry-run
```

### Deploy with auto-confirmation
```bash
python3 joget_utility.py --deploy-master-data --yes
```

---

## Form Generation

### Generate forms from all CSV files
```bash
cd joget_utility
python3 joget_utility.py --generate-forms-from-csv
```

### Generate single form from CSV
```bash
python3 joget_utility.py \
  --generate-form data/metadata/md99status.csv
```

### Generate with custom output path
```bash
python3 joget_utility.py \
  --generate-form data/metadata/md99status.csv \
  --output ../custom_forms/md99status.json
```

### Generate and overwrite existing
```bash
python3 joget_utility.py \
  --generate-forms-from-csv \
  --overwrite
```

---

## Data Import

### Import single CSV file to endpoint
```bash
cd joget_utility
python3 joget_utility.py \
  --endpoint maritalStatus \
  --input ../data/metadata/md01maritalStatus.csv
```

### Import JSON data
```bash
python3 joget_utility.py \
  --endpoint customer \
  --input ../data/customers.json
```

### Process metadata batch
```bash
python3 joget_utility.py \
  --metadata-batch config/metadata_batch.yaml
```

---

## Testing & Validation

### Test connection to Joget server
```bash
cd joget_utility
python3 joget_utility.py --test
```

### Validate data without posting
```bash
python3 joget_utility.py \
  --endpoint account \
  --input ../data/accounts.csv \
  --validate
```

### Dry run data import
```bash
python3 joget_utility.py \
  --endpoint maritalStatus \
  --input ../data/metadata/md01maritalStatus.csv \
  --dry-run
```

### List available endpoints
```bash
python3 joget_utility.py --list
```

### Debug mode (verbose logging)
```bash
python3 joget_utility.py \
  --create-form test.json \
  --app-id myApp \
  --port 8888 \
  --debug
```

---

## Environment Configuration

### Configuration Files

- **Main config**: `config/joget.yaml` - Base URL, API keys, endpoints
- **Deployment config**: `config/master_data_deploy.yaml` - FormCreator credentials, target app
- **Environment variables**: `.env.3` - Database credentials (never commit!)

### Port Mappings (Common Setups)

- **8080**: Default Joget installation
- **8888**: Test/development environment
- **9999**: Alternative test environment

### Override Config at Runtime

```bash
# Use custom config file
python3 joget_utility.py --config config/joget-dev.yaml --deploy-master-data

# Override API key
python3 joget_utility.py --api-key YOUR_KEY_HERE --endpoint test --input data.csv

# Use custom data directory
python3 joget_utility.py --data-dir /path/to/data --generate-forms-from-csv
```

---

## Common Workflows

### Workflow 1: Test a new form definition
```bash
cd joget_utility

# 1. Dry run first
python3 joget_utility.py --create-form test.json --app-id myApp --port 8888 --dry-run

# 2. Create form
python3 joget_utility.py --create-form test.json --app-id myApp --port 8888 --yes

# 3. Verify in Joget UI (check form, table, API, CRUD)
```

### Workflow 2: Generate and deploy metadata forms
```bash
cd joget_utility

# 1. Generate form JSONs from CSV files
python3 joget_utility.py --generate-forms-from-csv

# 2. Review generated forms in data/metadata_forms/

# 3. Deploy to Joget (dry run)
python3 joget_utility.py --deploy-master-data --dry-run

# 4. Deploy for real
python3 joget_utility.py --deploy-master-data --yes
```

### Workflow 3: Rapid iteration on a single form
```bash
cd joget_utility

# Edit form definition in doc_forms/test.json

# Test immediately
python3 joget_utility.py --create-form ../doc_forms/test.json --app-id myApp --port 8888 --yes

# Note: Joget may return error if form already exists
# Delete in Joget UI first, or use different form ID
```

---

## Tips & Best Practices

### Always dry-run first
```bash
# Good practice
python3 joget_utility.py --create-form test.json --app-id myApp --port 8888 --dry-run
python3 joget_utility.py --create-form test.json --app-id myApp --port 8888 --yes
```

### Use descriptive form IDs
```bash
# Good: Clear, descriptive
--form-id subsidyApproval_v2

# Bad: Generic, unclear
--form-id test123
```

### Keep one-off scripts minimal
**DON'T** create `send_form.py`, `test_api.py`, etc. for every test.

**DO** use `joget_utility.py --create-form` instead.

### Check logs when things fail
```bash
# Logs are in:
tail -f logs/master_data_deploy.log
tail -f logs/joget_utility.log

# Enable debug for more details
python3 joget_utility.py --create-form test.json --app-id myApp --port 8888 --debug
```

### Verify in database after deployment
```bash
mysql -h localhost -P 3308 -u root -pat456vkm jwdb -e "
  SELECT id, name FROM app_form WHERE appId='subsidyApplication';
  SELECT id, name FROM app_builder WHERE type='api' AND appId='subsidyApplication';
"
```

---

## Troubleshooting

### Error: "API key is required"
**Solution**: Check that `config/master_data_deploy.yaml` has `form_creator_api_key` set.

### Error: "Form definition file not found"
**Solution**: Check path is relative to current directory. Use `--create-form ../doc_forms/file.json` if running from `joget_utility/`.

### Error: "--app-id is required"
**Solution**: Always specify `--app-id` when using `--create-form`:
```bash
python3 joget_utility.py --create-form test.json --app-id subsidyApplication --port 8888
```

### Form already exists in Joget
**Solution**: Either:
1. Delete form in Joget UI first
2. Use different `--form-id` parameter
3. Use `--deploy-master-data --data-only` to only update data

### Connection refused
**Solution**: Check Joget is running:
```bash
# Test connection
python3 joget_utility.py --test

# Check Joget logs
tail -f /Users/aarelaponin/joget-enterprise-linux-9.0.0/apache-tomcat-9.0.90/logs/catalina.out
```

---

## See Also

- **CLAUDE.md**: Detailed project documentation and architectural guidelines
- **README.md**: Project overview and setup instructions
- **config/master_data_deploy.yaml**: Deployment configuration reference
