# GAM Utilities

A collection of data management utilities for financial asset management and Joget DX platform integration.

## Overview

This repository contains three main categories of tools:

1. **Financial Asset Management (GAM)**: Process bank statements, track security transactions, and manage investment portfolios
2. **Joget Platform Utilities**: Deploy forms, import data, and validate Joget DX applications
3. **Supporting Utilities**: Configuration management, validation, and testing tools

## Project Structure

```
gam_utilities/
├── data/                          # Data storage
│   ├── bank_statements/           # Input: Bank CSV statements
│   ├── security_transactions/     # Output: Extracted transactions (JSON)
│   ├── security_valuations/       # Output: Market valuations
│   ├── gl_config/                 # General ledger configuration
│   ├── security_statements/       # Security-specific statements
│   ├── test_data/                 # Test datasets
│   └── test_transactions/         # Transaction test data
├── investment_system/             # Investment tracking module
│   ├── assets.py                  # Security definitions
│   ├── customers.py               # Customer account management
│   ├── positions.py               # Position tracking
│   └── transactions.py            # Transaction records
├── joget_utility/                 # Joget data import/deployment
├── joget_validator/               # Database validation for Joget
├── joget_services/                # Form/DB mapping utilities
├── shared_utils/                  # Shared configuration and utilities
└── shared_data/                   # Shared data files
```

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/aarelaponin/gam_utilities.git
cd gam_utilities

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (copy and edit)
cp .env.example .env
```

### Environment Variables

Required environment variables (see `.env.example`):

```bash
# EODHD API for market data
EODHD_API_TOKEN=your_api_token_here

# Database credentials (for Joget utilities)
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=3306
DB_NAME=jwdb
DB_USER=root
```

## Core Components

### 1. Financial Asset Management (GAM)

#### Extract Security Transactions from Bank Statements

Process Estonian bank statement CSV files to extract security-related transactions.

```bash
# Process default bank statement
python get_secu_ops.py

# Process specific file
python get_secu_ops.py --input data/bank_statements/statement.csv \
                       --output data/security_transactions/output.json
```

**Features:**
- Extracts ticker symbols from transaction descriptions
- Identifies buy/sell transactions
- Filters security transactions (excludes currency exchanges, fees)
- Aggregates transactions by date, ticker, and description
- Outputs structured JSON with metadata

**Expected CSV Format (Estonian banks):**
- `Selgitus`: Transaction description
- `Kuupäev`: Transaction date (DD.MM.YYYY)
- `Summa`: Transaction amount

#### Add Security Details

Enrich security transaction data with additional details.

```bash
python add_secu_details.py
```

**Purpose:** Adds metadata like security names, ISINs, and other identifying information to extracted transactions.

#### Get Security Valuations

Retrieve current market valuations for securities using Yahoo Finance.

```bash
# Get current valuations
python secu_values.py

# Specify custom directories
python secu_values.py --input-dir data \
                      --input-file matched_security_transactions.json \
                      --output-file asset_current_values.json
```

**Features:**
- Fetches current prices from Yahoo Finance (yfinance)
- Calculates current portfolio values
- Tracks historical valuation data
- Generates valuation reports

#### Investment System

Object-oriented investment tracking system for managing portfolios.

```bash
python investments.py
```

**Components:**
- **Customer Management** (`customers.py`): Track customer accounts, deposits, withdrawals
- **Security Definitions** (`assets.py`): Define securities with symbols and metadata
- **Position Tracking** (`positions.py`): Monitor holdings per customer per security
- **Transaction Recording** (`transactions.py`): Record all trading activities

**Use Case:** Build a complete portfolio management system with customer accounts, multiple securities, and transaction history.

### 2. Joget Platform Utilities

Tools for working with Joget DX 8 applications.

#### Joget Utility - Data Import & Form Deployment

Import data to Joget forms and deploy master data configurations.

```bash
cd joget_utility

# Import data to a single endpoint
python joget_utility.py --endpoint maritalStatus --input marital_status.csv

# Deploy master data (create forms + populate data)
python joget_utility.py --deploy-master-data

# Deploy forms only (no data population)
python joget_utility.py --deploy-master-data --forms-only

# Dry run (test without making changes)
python joget_utility.py --deploy-master-data --dry-run
```

**Key Features:**
- CSV/JSON data import to Joget form APIs
- Batch processing for metadata endpoints
- Master data deployment (two-phase: form creation → data population)
- Form creation via FormCreator API
- Configurable field mappings
- Retry mechanisms and validation

**Configuration:**
- `joget_utility/config/joget.yaml`: Joget server settings, API keys
- `joget_utility/config/metadata_batch.yaml`: Batch processing config
- `joget_utility/config/master_data_deploy.yaml`: Deployment settings

See [joget_utility/README.md](joget_utility/README.md) for detailed documentation.

#### Joget Validator - Database Validation

Validate that test data has been correctly stored in Joget MySQL database.

```bash
# Validate all farmers with default settings
python validate_registry.py

# Validate specific farmer
python validate_registry.py --farmer farmer-001

# Validate specific form
python validate_registry.py --form farmerBasicInfo

# Generate reports
python validate_registry.py --format all --output ./reports

# Test connections
python validate_registry.py --test-connections
```

**Key Features:**
- Validates data against expected test data (`test-data.json`)
- Uses field mappings from `services.yml`
- Multiple report formats (console, JSON, HTML)
- Type-aware value comparisons
- Database connectivity testing

**Configuration:**
- `joget_validator/config/validation.yaml`: Database connection, validation settings
- `shared_data/services.yml`: Field mappings between JSON paths and database columns
- `shared_data/test-data.json`: Expected test data

See [joget_validator/README.md](joget_validator/README.md) for detailed documentation.

#### Joget Services - Form/Database Mapping

Tools for analyzing Joget form structures and validating database schemas.

```bash
cd joget_services

# Validate form structure against database
python validate_form_structure_db.py

# Map form fields to database columns
python database_mapper.py

# Parse form definitions
python form_parser.py
```

**Key Features:**
- Analyzes form JSON definitions
- Maps form fields to database tables/columns
- Validates database schema matches form structure
- Generates validation reports

**Artifacts:**
- `form_structure.yaml`: Form field hierarchy and metadata
- `validation_report.json`: Detailed validation results
- `validation_report.md`: Human-readable validation report

### 3. Supporting Utilities

#### Configuration Management

```python
# shared_utils/config.py
from shared_utils.config import load_validation_config, setup_logging

# Load configuration
config = load_validation_config('config/validation.yaml')

# Setup logging
logger = setup_logging(level='INFO')
```

**Purpose:** Centralized configuration loading, logging setup, and common utilities shared across tools.

#### Testing Utilities

```bash
# Test database connection
python test_db_connection.py

# Test path resolution
python test_path_resolution.py
```

## Development Workflow

### Processing Bank Statements

1. Place bank statement CSV in `data/bank_statements/`
2. Run `python get_secu_ops.py` to extract transactions
3. Run `python add_secu_details.py` to enrich with security details
4. Run `python secu_values.py` to get current market valuations
5. View results in `data/security_transactions/` and `data/security_valuations/`

### Deploying Joget Master Data

1. Prepare form definitions in `joget_utility/data/metadata_forms/` (e.g., `md01maritalStatus.json`)
2. Prepare data files in `joget_utility/data/metadata/` (e.g., `md01maritalStatus.csv`)
3. Configure deployment in `joget_utility/config/master_data_deploy.yaml`
4. Run `python joget_utility.py --deploy-master-data`
5. Validate with `python validate_registry.py`

### Validating Joget Applications

1. Configure database connection in `joget_validator/config/validation.yaml`
2. Ensure `services.yml` defines field mappings
3. Ensure `test-data.json` contains expected test data
4. Run `python validate_registry.py`
5. Review reports in `validation_reports/`

## Dependencies

Core dependencies (see `requirements.txt`):

- **eodhd** (1.0.32): Market data from EODHD API
- **pandas** (2.2.3): Data manipulation and analysis
- **yfinance** (0.2.57): Yahoo Finance market data
- **python-dotenv** (1.0.0): Environment variable management
- **mysql-connector-python** (8.3.0): MySQL database connectivity
- **PyYAML**: YAML configuration file parsing

## Data Formats

### Bank Statement CSV (Input)

```csv
Kuupäev,Selgitus,Summa
01.01.2024,"Securities purchase (AAPL)",-1500.00
02.01.2024,"Securities sale (MSFT)",2500.00
```

### Security Transactions JSON (Output)

```json
{
  "security_transactions": [
    {
      "date": "2024-01-01",
      "ticker": "AAPL",
      "amount": -1500.00,
      "description": "Securities purchase (AAPL)",
      "type": "buy",
      "operations_count": 1
    }
  ],
  "metadata": {
    "processed_date": "2024-10-08T12:00:00",
    "total_transactions": 1,
    "unique_tickers": 1,
    "total_operations": 1
  }
}
```

### Master Data CSV (Input for Joget)

```csv
code,name
SINGLE,Single
MARRIED,Married
DIVORCED,Divorced
```

## Common Issues & Solutions

### EODHD API Token Missing

**Error:** `EODHD_API_TOKEN environment variable not set`

**Solution:** Add your EODHD API token to `.env`:
```bash
EODHD_API_TOKEN=your_token_here
```

### Database Connection Failed

**Error:** `mysql.connector.errors.DatabaseError: 2003`

**Solution:** Check database credentials in `.env` and ensure MySQL is running:
```bash
# Test connection
python test_db_connection.py
```

### Form Creation Fails

**Error:** `Form creation failed: API authentication error`

**Solution:** Verify FormCreator API credentials in `joget_utility/config/master_data_deploy.yaml`

### Ticker Extraction Returns Empty

**Issue:** Transactions don't have ticker symbols extracted

**Cause:** Transaction description format doesn't match expected patterns

**Solution:** Check transaction descriptions contain ticker in parentheses `(AAPL)` or valid ISIN codes

## Key Scripts Reference

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `get_secu_ops.py` | Extract security transactions | CSV bank statement | JSON transactions |
| `add_secu_details.py` | Enrich security data | JSON transactions | Enriched JSON |
| `secu_values.py` | Get current valuations | JSON transactions | JSON valuations |
| `investments.py` | Investment system | - | Portfolio management |
| `joget_utility/joget_utility.py` | Import data to Joget | CSV/JSON | API calls |
| `validate_registry.py` | Validate Joget database | test-data.json | Validation reports |
| `joget_services/validate_form_structure_db.py` | Validate form schema | Form JSON | Validation report |

## Architecture Notes

### Transaction Aggregation

Transactions are aggregated by `(date, ticker, description)` tuple:
- Multiple transactions with same key are summed
- `operations_count` tracks number of aggregated transactions
- `type` (buy/sell) determined by final aggregated amount (negative = buy, positive = sell)

### Joget Form Deployment (Two-Phase)

**Phase 1 - Form Creation:**
- Read form definitions (`md*.json`)
- POST to `/jw/api/form/formCreator/addWithFiles`
- Create physical database tables (lazy creation triggered on first data write)

**Phase 2 - Data Population:**
- Match form to data file by name
- POST to `/jw/api/form/{formId}/saveOrUpdate`
- Retry on failure

### Investment System Design

Object-oriented design with clear separation:
- **Customer**: Manages cash balances and customer info
- **Security**: Defines tradable securities with prices
- **Position**: Tracks holdings per customer/security
- **Transaction**: Immutable record of all operations

## Contributing

When modifying this repository:

1. Follow existing code structure and patterns
2. Update relevant README files
3. Add tests for new functionality
4. Update CLAUDE.md if adding platform-specific guidance
5. Maintain backwards compatibility

## License

See LICENSE file for details.

## Contact

For issues or questions, create a GitHub issue at:
https://github.com/aarelaponin/gam_utilities/issues

---

**Last Updated:** October 2025
