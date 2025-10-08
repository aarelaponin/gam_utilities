# Farmers Registry Database Validation Utility - Technical Specification

## 1. Executive Summary

### Purpose
Create a Python utility that validates whether test data from `test-data.json` has been correctly stored in the Joget MySQL database according to the mappings defined in `services.yml`.

### Scope
- **In Scope**: Verify data existence and value matching in database tables
- **Out of Scope**: Data corrections, API interactions, complex transformations

### Approach
Hybrid architecture with shared components between existing joget_utility and new validation tool.

---

## 2. System Architecture

### 2.1 Directory Structure

```
joget_tools/
├── joget_utility/                 # Existing import tool
│   ├── joget_utility.py
│   ├── processors/
│   └── config/
│
├── joget_validator/               # New validation tool
│   ├── validate_registry.py      # Main entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── validator.py          # Main validation orchestrator
│   │   ├── database.py           # Database operations
│   │   └── mapper.py             # Field mapping logic
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── services_parser.py    # Parse services.yml
│   │   └── test_data_parser.py   # Parse test-data.json
│   ├── validators/
│   │   ├── __init__.py
│   │   ├── form_validator.py     # Validate form data
│   │   ├── grid_validator.py     # Validate grid data
│   │   └── field_validator.py    # Field-level validation
│   ├── reports/
│   │   ├── __init__.py
│   │   ├── console_reporter.py   # Console output
│   │   ├── json_reporter.py      # JSON report
│   │   └── html_reporter.py      # HTML report
│   ├── config/
│   │   └── validation.yaml       # Validation config
│   └── requirements.txt
│
└── shared_data/                   # Shared configuration location
    ├── services.yml               # Field mappings
    ├── test-data.json            # Test data
    └── metadata/                  # Metadata CSV files
        ├── md01maritalStatus.csv
        ├── md02language.csv
        └── ...
```

### 2.2 Component Diagram

```
Input Layer:
  - services.yml
  - test-data.json  
  - validation.yaml
      ↓
Parser Layer:
  - Services Parser
  - Test Data Parser
  - Config Loader
      ↓
Validation Core:
  - Registry Validator
  - Database Connector
  - Field Mapper
      ↓
Validation Layer:
  - Form Validator
  - Grid Validator  
  - Field Validator
      ↓
Database:
  - MySQL/Joget DB
      ↓
Output Layer:
  - Report Generator
  - Console/JSON/HTML Output
```

---

## 3. Data Flow Specification

### 3.1 Validation Process Flow

```python
# Pseudo-code for main validation flow
def validate_registry():
    # 1. Load configurations
    services = load_services_yml("shared_data/services.yml")
    test_data = load_test_data("shared_data/test-data.json")
    db_config = load_config("config/validation.yaml")
    
    # 2. Connect to database
    db = connect_mysql(db_config)
    
    # 3. For each farmer in test data
    for farmer in test_data:
        farmer_id = extract_identifier(farmer)
        
        # 4. Validate each form
        for form_name in services.forms:
            form_data = query_form_data(db, form_name, farmer_id)
            validate_form(farmer, form_data, services.mappings[form_name])
        
        # 5. Validate grids
        for grid_name in services.grids:
            grid_data = query_grid_data(db, grid_name, farmer_id)
            validate_grid(farmer, grid_data, services.mappings[grid_name])
    
    # 6. Generate reports
    generate_reports(validation_results)
```

### 3.2 Data Mapping Flow

```
Test Data (JSON) --> Field Path Extraction --> Transformation --> Database Column --> Comparison
                          |                           |                  |
                    services.yml              services.yml        Joget Tables
                    (govstack/jsonPath)        (transform)         (c_ prefix)
```

---

## 4. Module Specifications

### 4.1 Core Modules

#### 4.1.1 Main Entry Point (`validate_registry.py`)

```python
"""
Main entry point for the validation utility.
Handles command-line arguments and orchestrates validation.
"""

class ValidateRegistry:
    def __init__(self, args):
        self.config_path = args.config or "config/validation.yaml"
        self.services_yml = args.services or "shared_data/services.yml"
        self.test_data = args.test_data or "shared_data/test-data.json"
        self.output_format = args.format  # console, json, html, all
        self.output_dir = args.output or "./validation_reports"
        self.verbose = args.verbose
        
    def run(self):
        """Execute validation pipeline"""
        pass
```

#### 4.1.2 Registry Validator (`core/validator.py`)

```python
"""
Main orchestrator for validation process.
Coordinates between parsers, validators, and reporters.
"""

class RegistryValidator:
    def __init__(self, services_config, test_data, db_config):
        self.services = ServicesParser(services_config)
        self.test_data = TestDataParser(test_data)
        self.db = DatabaseConnector(db_config)
        self.form_validator = FormValidator()
        self.grid_validator = GridValidator()
        
    def validate_all(self) -> ValidationReport:
        """Validate all farmers in test data"""
        pass
        
    def validate_farmer(self, farmer_data: dict) -> FarmerValidationResult:
        """Validate single farmer across all forms and grids"""
        pass
```

#### 4.1.3 Database Connector (`core/database.py`)

```python
"""
Manages MySQL database connections and queries.
"""

class DatabaseConnector:
    def __init__(self, config):
        self.host = config['host']
        self.port = config['port']
        self.database = config['database']
        self.user = config['user']
        self.password = config['password']
        
    def query_form(self, table_name: str, farmer_id: str) -> dict:
        """Query single form record"""
        pass
        
    def query_grid(self, table_name: str, parent_field: str, parent_id: str) -> list:
        """Query grid records"""
        pass
```

### 4.2 Parser Modules

#### 4.2.1 Services Parser (`parsers/services_parser.py`)

```python
"""
Parses services.yml to extract form mappings and transformations.
"""

class ServicesParser:
    def __init__(self, yml_path: str):
        self.yml_path = yml_path
        self.config = self._load_yaml()
        
    def get_form_mappings(self, form_name: str) -> dict:
        """Get field mappings for a specific form"""
        pass
        
    def get_grid_config(self, grid_name: str) -> dict:
        """Get configuration for a grid"""
        pass
        
    def get_transformation(self, transform_type: str) -> callable:
        """Get transformation function"""
        pass
```

#### 4.2.2 Test Data Parser (`parsers/test_data_parser.py`)

```python
"""
Parses test-data.json and provides data extraction methods.
"""

class TestDataParser:
    def __init__(self, json_path: str):
        self.json_path = json_path
        self.data = self._load_json()
        
    def get_farmers(self) -> list:
        """Get list of all farmers"""
        pass
        
    def extract_value(self, data: dict, path: str) -> any:
        """Extract value using dot notation path"""
        pass
```

### 4.3 Validator Modules

#### 4.3.1 Form Validator (`validators/form_validator.py`)

```python
"""
Validates data in main form tables.
"""

class FormValidator:
    def validate(self, test_data: dict, db_data: dict, mappings: dict) -> FormValidationResult:
        """Validate form data against test data"""
        pass
        
    def _map_field(self, field_config: dict, test_data: dict) -> any:
        """Map and transform field value"""
        pass
```

#### 4.3.2 Grid Validator (`validators/grid_validator.py`)

```python
"""
Validates data in grid/sub-form tables.
"""

class GridValidator:
    def validate(self, test_data: list, db_data: list, mappings: dict) -> GridValidationResult:
        """Validate grid data against test data"""
        pass
        
    def _validate_row_count(self, expected: int, actual: int) -> bool:
        """Check if row counts match"""
        pass
```

#### 4.3.3 Field Validator (`validators/field_validator.py`)

```python
"""
Field-level validation logic.
"""

class FieldValidator:
    @staticmethod
    def compare_values(expected: any, actual: any, field_type: str = None) -> bool:
        """Compare two values considering type and format"""
        pass
        
    @staticmethod
    def apply_transformation(value: any, transform: str) -> any:
        """Apply transformation to value"""
        pass
```

### 4.4 Reporter Modules

#### 4.4.1 Console Reporter (`reports/console_reporter.py`)

```python
"""
Generates console output for validation results.
"""

class ConsoleReporter:
    def generate(self, report: ValidationReport) -> None:
        """Print formatted report to console"""
        pass
```

#### 4.4.2 JSON Reporter (`reports/json_reporter.py`)

```python
"""
Generates JSON report file.
"""

class JSONReporter:
    def generate(self, report: ValidationReport, output_path: str) -> None:
        """Generate JSON report file"""
        pass
```

---

## 5. Data Models

### 5.1 Core Data Classes

```python
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime

class ValidationStatus(Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"

@dataclass
class FieldValidationResult:
    field_name: str
    joget_column: str
    expected_value: Any
    actual_value: Any
    status: ValidationStatus
    error_message: Optional[str] = None

@dataclass
class FormValidationResult:
    form_name: str
    table_name: str
    status: ValidationStatus
    total_fields: int
    passed_fields: int
    failed_fields: int
    field_results: List[FieldValidationResult]

@dataclass
class GridValidationResult:
    grid_name: str
    table_name: str
    status: ValidationStatus
    expected_rows: int
    actual_rows: int
    row_validations: List[Dict[str, Any]]

@dataclass
class FarmerValidationResult:
    farmer_id: str
    national_id: str
    status: ValidationStatus
    form_results: Dict[str, FormValidationResult]
    grid_results: Dict[str, GridValidationResult]
    validation_time: datetime
    duration_seconds: float

@dataclass
class ValidationReport:
    total_farmers: int
    passed: int
    failed: int
    skipped: int
    validation_time: datetime
    duration_seconds: float
    farmer_results: List[FarmerValidationResult]
```

---

## 6. Configuration Files

### 6.1 Validation Configuration (`config/validation.yaml`)

```yaml
# Database connection
database:
  host: localhost
  port: 3306
  database: jogetdb
  user: joget
  password: joget
  
# Data sources
data_sources:
  services_yml: ../shared_data/services.yml
  test_data: ../shared_data/test-data.json
  metadata_dir: ../shared_data/metadata
  
# Validation settings
validation:
  # Check only these forms (leave empty for all)
  forms_to_validate: []
  
  # Check only these grids (leave empty for all)
  grids_to_validate: []
  
  # Skip validation for these fields
  ignore_fields:
    - dateCreated
    - dateModified
    - createdBy
    - modifiedBy
  
  # Comparison settings
  case_sensitive: false
  trim_strings: true
  null_equals_empty: true
  
# Reporting
reporting:
  formats: [console, json, html]  # Options: console, json, html
  output_directory: ./validation_reports
  include_passed_fields: false  # Only show failures in report
  max_errors_per_form: 10  # Limit errors shown per form
  
# Logging
logging:
  level: INFO  # DEBUG, INFO, WARNING, ERROR
  file: ./logs/validation.log
```

---

## 7. Command Line Interface

### 7.1 Command Structure

```bash
python validate_registry.py [OPTIONS]
```

### 7.2 Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--config` | `-c` | `config/validation.yaml` | Path to validation config |
| `--services` | `-s` | `../shared_data/services.yml` | Path to services.yml |
| `--test-data` | `-t` | `../shared_data/test-data.json` | Path to test data |
| `--format` | `-f` | `all` | Output format: console, json, html, all |
| `--output` | `-o` | `./validation_reports` | Output directory for reports |
| `--farmer` | | | Validate specific farmer by ID |
| `--form` | | | Validate specific form only |
| `--verbose` | `-v` | | Enable verbose output |
| `--debug` | | | Enable debug logging |
| `--help` | `-h` | | Show help message |

### 7.3 Usage Examples

```bash
# Basic validation with default settings
python validate_registry.py

# Validate with custom paths
python validate_registry.py --services /path/to/services.yml --test-data /path/to/test.json

# Validate specific farmer
python validate_registry.py --farmer farmer-001

# Generate only JSON report
python validate_registry.py --format json --output ./reports

# Debug mode with verbose output
python validate_registry.py --debug --verbose

# Validate only specific form
python validate_registry.py --form farmerBasicInfo
```

---

## 8. Database Schema Reference

### 8.1 Table Naming Convention

```
Main Forms: app_fd_[form_name]
Grid Tables: app_fd_[grid_name]
Column Prefix: c_
Primary Keys: c_farmer_id (main forms), c_id (grids)
Parent Links: c_farmer_id (in grid tables)
```

### 8.2 Table Mappings

| Form Name | Table Name | Primary Key |
|-----------|------------|-------------|
| farmerBasicInfo | app_fd_farmer_basic | c_farmer_id |
| farmerLocation | app_fd_farmer_location | c_farmer_id |
| farmerAgriculture | app_fd_farmer_agric | c_farmer_id |
| farmerHousehold | app_fd_farmer_household | c_farmer_id |
| farmerCropsLivestock | app_fd_farmer_crop_livestck | c_farmer_id |
| farmerIncomePrograms | app_fd_farmer_income_prog | c_farmer_id |
| farmerDeclaration | app_fd_farmer_declaration | c_farmer_id |

| Grid Name | Table Name | Parent Field |
|-----------|------------|--------------|
| householdMembers | app_fd_household_members | c_farmer_id |
| cropManagement | app_fd_crop_management | c_farmer_id |
| livestockDetails | app_fd_livestock_details | c_farmer_id |

---

## 9. Implementation Guidelines

### 9.1 Development Setup in PyCharm

1. **Project Structure**:
   - Create new Python project: `joget_validator`
   - Set Python interpreter: 3.8+
   - Configure virtual environment

2. **Dependencies** (`requirements.txt`):
   ```
   mysql-connector-python==8.0.33
   PyYAML==6.0
   ```

3. **Run Configuration**:
   - Script path: `validate_registry.py`
   - Working directory: Project root
   - Environment variables: Optional database credentials

### 9.2 Error Handling Strategy

```python
# Consistent error handling pattern
try:
    # Operation
    result = perform_validation()
except mysql.connector.Error as e:
    logger.error(f"Database error: {e}")
    return ValidationStatus.ERROR
except KeyError as e:
    logger.warning(f"Missing field: {e}")
    return ValidationStatus.SKIPPED
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
```

### 9.3 Testing Approach

```python
# Test structure
tests/
├── unit/
│   ├── test_parsers.py
│   ├── test_validators.py
│   └── test_mappers.py
├── integration/
│   ├── test_database.py
│   └── test_end_to_end.py
└── fixtures/
    ├── sample_services.yml
    ├── sample_test_data.json
    └── sample_db_data.sql
```

---

## 10. Sample Output Formats

### 10.1 Console Output

```
========================================
Farmers Registry Validation Report
========================================
Validation Time: 2025-01-23 14:30:00
Duration: 2.34 seconds

Summary:
--------
Total Farmers: 1
✓ Passed: 0
✗ Failed: 1
⊘ Skipped: 0

Detailed Results:
-----------------
Farmer: farmer-001 (NID: 9405156789086) [FAILED]

  Form: farmerBasicInfo [FAILED]
    ✗ first_name: Expected "Thabo", Found "Thaboo"
    ✓ last_name: OK
    ✓ gender: OK
    
  Form: farmerLocation [PASSED]
    All 15 fields validated successfully
    
  Grid: householdMembers [FAILED]
    Expected 5 rows, Found 4 rows
    Missing household member at index 4
```

### 10.2 JSON Output Structure

```json
{
  "validation_report": {
    "metadata": {
      "validation_time": "2025-01-23T14:30:00",
      "duration_seconds": 2.34,
      "tool_version": "1.0.0"
    },
    "summary": {
      "total_farmers": 1,
      "passed": 0,
      "failed": 1,
      "skipped": 0
    },
    "results": [
      {
        "farmer_id": "farmer-001",
        "national_id": "9405156789086",
        "status": "FAILED",
        "forms": {
          "farmerBasicInfo": {
            "status": "FAILED",
            "errors": [
              {
                "field": "first_name",
                "expected": "Thabo",
                "actual": "Thaboo",
                "column": "c_first_name"
              }
            ]
          }
        }
      }
    ]
  }
}
```

---

## 11. Next Steps for Development

1. **Phase 1: Core Infrastructure** (Week 1)
   - Set up project structure
   - Implement parsers for services.yml and test-data.json
   - Create database connector

2. **Phase 2: Validation Logic** (Week 2)
   - Implement form validator
   - Implement grid validator
   - Add field-level comparison logic

3. **Phase 3: Reporting** (Week 3)
   - Console reporter
   - JSON reporter
   - HTML reporter (optional)

4. **Phase 4: Testing & Refinement** (Week 4)
   - Unit tests
   - Integration tests
   - Documentation

---

This specification provides a complete blueprint for implementing the validation utility. The design maintains separation from your existing import tool while allowing for future integration through the shared data directory structure.