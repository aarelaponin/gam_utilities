# Joget Utility - Technical Documentation

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [System Components](#system-components)
3. [API Reference](#api-reference)
4. [Data Processing Pipeline](#data-processing-pipeline)
5. [Configuration System](#configuration-system)
6. [Error Handling & Recovery](#error-handling--recovery)
7. [Logging & Debugging](#logging--debugging)
8. [Security Considerations](#security-considerations)
9. [Performance Optimization](#performance-optimization)
10. [Extension Guide](#extension-guide)
11. [Testing Strategy](#testing-strategy)
12. [Deployment Guide](#deployment-guide)

---

## Architecture Overview

### System Design

The Joget Utility follows a modular, layered architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    Command Line Interface                    │
│                     (joget_utility.py)                      │
├─────────────────────────────────────────────────────────────┤
│                    Configuration Layer                       │
│                        (utils.py)                           │
├──────────────────┬──────────────────┬──────────────────────┤
│   Data Layer     │  Processing Layer │   Network Layer      │
│                  │                    │                      │
│  ┌────────────┐ │  ┌──────────────┐│  ┌──────────────┐   │
│  │CSV Files   │ │  │BaseProcessor  ││  │JogetClient   │   │
│  │JSON Files  │ │  │CSVProcessor   ││  │- POST        │   │
│  │Config YAML │ │  │JSONProcessor  ││  │- Batch POST  │   │
│  └────────────┘ │  │MetadataProc.  ││  │- Retry Logic │   │
│                  │  └──────────────┘│  └──────────────┘   │
└──────────────────┴──────────────────┴──────────────────────┘
```

### Design Principles

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Dependency Injection**: Configuration and dependencies injected at runtime
3. **Factory Pattern**: Processor selection based on file type
4. **Strategy Pattern**: Different processing strategies for CSV/JSON
5. **Template Method**: Base processor defines algorithm, subclasses implement specifics

### Component Interactions

```mermaid
sequenceDiagram
    CLI->>Config: Load Configuration
    Config->>CLI: Return Config Dict
    CLI->>Logger: Setup Logging
    CLI->>Processor: Create Processor
    Processor->>DataFile: Read File
    DataFile->>Processor: Return Raw Data
    Processor->>Processor: Transform Data
    Processor->>CLI: Return Processed Data
    CLI->>JogetClient: Send Data
    JogetClient->>JogetAPI: HTTP POST
    JogetAPI->>JogetClient: Response
    JogetClient->>CLI: Return Results
    CLI->>User: Display Summary
```

---

## System Components

### Core Modules

#### 1. Main CLI Module (`joget_utility.py`)

**Purpose**: Entry point and orchestration layer

**Key Functions**:
```python
def main() -> None:
    """Main entry point with argument parsing"""

def process_single_endpoint(args: Namespace, config: Dict) -> None:
    """Process single endpoint with data file"""

def process_metadata_batch(args: Namespace, config: Dict) -> None:
    """Process multiple metadata endpoints"""
```

**Command Line Arguments**:
| Argument | Type | Description |
|----------|------|-------------|
| `--endpoint` | str | Target endpoint name |
| `--input` | str | Input file path |
| `--metadata-batch` | str | Batch configuration file |
| `--dry-run` | flag | Preview mode without posting |
| `--validate` | flag | Validation only mode |
| `--debug` | flag | Enable debug logging |
| `--verbose` | flag | Verbose output |
| `--yes` | flag | Skip confirmations |
| `--stop-on-error` | flag | Halt on first error |
| `--config` | str | Alternative config file |
| `--api-key` | str | Override API key |
| `--data-dir` | str | Override data directory |
| `--test` | flag | Test connection |
| `--list` | flag | List endpoints |

#### 2. HTTP Client Module (`joget_client.py`)

**Classes**:

```python
class JogetClient:
    """HTTP client for Joget DX8 API"""

    def __init__(self, base_url: str, api_key: str = None, debug: bool = False):
        """Initialize with connection parameters"""

    def post(self, endpoint: str, api_id: str, data: Dict[str, Any],
             api_key: str = None, retry: bool = True) -> Dict[str, Any]:
        """POST single record with retry logic"""

    def batch_post(self, endpoint: str, api_id: str,
                   records: List[Dict[str, Any]],
                   api_key: str = None,
                   stop_on_error: bool = False) -> Dict[str, Any]:
        """POST multiple records with error handling"""

    def test_connection(self) -> bool:
        """Test server connectivity"""

class JogetAPIError(Exception):
    """Custom exception for API errors"""
```

**HTTP Configuration**:
- Default timeout: 30 seconds
- Retry count: 3 attempts
- Retry delay: 2 seconds
- Connection pooling via requests.Session

#### 3. Processor Modules (`processors/`)

**Base Processor** (`base.py`):
```python
from abc import ABC, abstractmethod

class BaseProcessor(ABC):
    """Abstract base class for data processors"""

    @abstractmethod
    def read_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Read and parse file - must be implemented"""

    def transform_record(self, record: Dict, required_fields: List[str]) -> Dict:
        """Apply field mapping and validation"""

    def validate_record(self, record: Dict, required_fields: List[str]) -> bool:
        """Validate record has required fields"""

    def process_file(self, file_path: Path) -> Dict[str, Any]:
        """Complete processing pipeline"""
```

**CSV Processor** (`csv_processor.py`):
```python
class CSVProcessor(BaseProcessor):
    """CSV file processor with auto-detection"""

    Features:
    - Automatic delimiter detection (comma, semicolon, tab, pipe)
    - UTF-8 with BOM handling
    - Empty row filtering
    - Header validation
    - Configurable encoding
```

**JSON Processor** (`json_processor.py`):
```python
class JSONProcessor(BaseProcessor):
    """JSON file processor with structure flexibility"""

    Supported structures:
    - Direct array: [{}]
    - Wrapped array: {data: [{}]}
    - Named collections: {records: [{}], testData: [{}]}
    - Nested object flattening with configurable separator
```

**Metadata Processor** (`metadata.py`):
```python
class MetadataProcessor:
    """Batch processor for metadata endpoints"""

    def process_batch(self, batch_file: Path) -> Dict[str, Any]:
        """Process multiple endpoints from configuration"""

    def _transform_to_code_name(self, records: List[Dict]) -> List[Dict]:
        """Convert records to standard code/name format"""
```

#### 4. Utilities Module (`utils.py`)

**Configuration Management**:
```python
def load_config(config_path: str = None) -> Dict[str, Any]:
    """Load YAML configuration with defaults"""

def resolve_data_path(file_name: str, config: Dict,
                     data_type: str = 'default') -> Path:
    """Resolve file paths with fallback logic"""
```

**Logging Setup**:
```python
def setup_logging(config: Dict[str, Any] = None) -> logging.Logger:
    """Configure dual console/file logging"""

    Returns logger with:
    - Console handler (stdout)
    - File handler (optional)
    - Configurable format and level
```

**User Interaction**:
```python
def confirm_action(message: str) -> bool:
    """Interactive confirmation prompt"""

def print_summary(results: Dict[str, Any], verbose: bool = False):
    """Display processing results"""

def format_record_for_display(record: Dict[str, Any],
                              max_width: int = 80) -> str:
    """Format record for console display"""
```

---

## API Reference

### JogetClient API

#### Constructor
```python
client = JogetClient(
    base_url="http://localhost:8080/jw/api/form",
    api_key="your_api_key",
    debug=False  # Enable debug logging
)
```

#### Methods

##### post()
```python
result = client.post(
    endpoint="maritalStatus",        # Endpoint name or path
    api_id="API-xxx-xxx",            # API identifier
    data={"code": "S", "name": "Single"},  # Data to post
    api_key="override_key",          # Optional key override
    retry=True                       # Enable retry logic
)

# Returns:
{
    "status": "success",
    "id": "generated_id",
    "message": "Record created"
}

# Raises:
JogetAPIError: On API failures
```

##### batch_post()
```python
results = client.batch_post(
    endpoint="customer",
    api_id="API-xxx",
    records=[
        {"customerId": "001", "customerName": "John"},
        {"customerId": "002", "customerName": "Jane"}
    ],
    stop_on_error=False  # Continue on failures
)

# Returns:
{
    "total": 2,
    "successful": 2,
    "failed": 0,
    "errors": []
}
```

### Processor API

#### BaseProcessor Methods

##### read_file()
```python
records = processor.read_file(Path("data.csv"))
# Returns: List[Dict[str, Any]]
```

##### transform_record()
```python
transformed = processor.transform_record(
    record={"id": "001", "name": "John"},
    required_fields=["customerId", "customerName"]
)
# Returns: Dict with mapped fields
```

##### validate_record()
```python
is_valid = processor.validate_record(
    record={"customerId": "001"},
    required_fields=["customerId", "customerName"]
)
# Returns: bool
```

### Configuration API

#### Configuration Structure
```yaml
# config/joget.yaml
base_url: http://localhost:8080/jw/api/form
default_api_key: your_api_key

data_paths:
  default: ./data
  metadata: ./data/metadata
  csv: ./data/csv
  json: ./data/json

connection:
  timeout: 30
  retry_count: 3
  retry_delay: 2

logging:
  level: INFO
  file: ./logs/joget_utility.log
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

metadata_endpoints:
  endpoint_name:
    api_id: API-xxx
    description: "Description"

endpoints:
  custom_endpoint:
    api_id: API-xxx
    required_fields: [field1, field2]
    field_mapping:
      source: target
```

---

## Data Processing Pipeline

### Processing Flow

```
1. Input Stage
   ├── File Discovery (resolve_data_path)
   ├── Format Detection (file extension)
   └── Processor Selection (CSV/JSON)

2. Reading Stage
   ├── File Loading
   ├── Encoding Detection
   ├── Structure Parsing
   └── Initial Validation

3. Transformation Stage
   ├── Field Mapping
   ├── Type Conversion
   ├── Value Normalization
   └── Code/Name Extraction

4. Validation Stage
   ├── Required Field Check
   ├── Data Type Validation
   ├── Business Rule Validation
   └── Error Collection

5. Posting Stage
   ├── Batch Preparation
   ├── API Authentication
   ├── HTTP POST Execution
   ├── Retry on Failure
   └── Response Processing

6. Results Stage
   ├── Success/Failure Counting
   ├── Error Aggregation
   ├── Summary Generation
   └── User Feedback
```

### Data Transformation Rules

#### Field Mapping
```python
# Configuration
field_mapping:
  source_field: target_field

# Transformation
if field_mapping:
    for source, target in field_mapping.items():
        if source in record:
            transformed[target] = record[source]
```

#### Metadata Transformation
```python
# Auto-detection for code/name
if 'code' in record and 'name' in record:
    result = {'code': record['code'], 'name': record['name']}
else:
    # Use first two fields
    fields = list(record.keys())
    if len(fields) >= 2:
        result = {
            'code': str(record[fields[0]]),
            'name': str(record[fields[1]])
        }
```

### Error Handling in Pipeline

```python
# Error collection pattern
errors = []
warnings = []

for record in records:
    try:
        processed = transform_record(record)
        if not validate_record(processed):
            errors.append(f"Validation failed: {record}")
            continue
        results.append(processed)
    except Exception as e:
        errors.append(f"Processing error: {e}")
        if stop_on_error:
            break
```

---

## Configuration System

### Configuration Loading Hierarchy

```
1. Command line --config argument
2. ./config/joget.yaml
3. ./joget.yaml
4. <module_dir>/config/joget.yaml
5. Built-in defaults
```

### Default Configuration

```python
defaults = {
    'connection': {
        'timeout': 30,
        'retry_count': 3,
        'retry_delay': 2
    },
    'logging': {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    },
    'data_paths': {
        'default': './data',
        'metadata': './data/metadata',
        'csv': './data/csv',
        'json': './data/json'
    }
}
```

### Environment-Specific Configuration

```yaml
# Development
base_url: http://localhost:8080/jw/api/form
logging:
  level: DEBUG

# Production
base_url: https://production.server/jw/api/form
logging:
  level: WARNING
connection:
  timeout: 60
  retry_count: 5
```

### Dynamic Configuration

```python
# Override via command line
python joget_utility.py --api-key OVERRIDE_KEY --data-dir /custom/path

# Override in code
config['logging']['level'] = 'DEBUG' if args.debug else 'INFO'
```

---

## Error Handling & Recovery

### Exception Hierarchy

```python
Exception
├── JogetAPIError                    # Base API exception
│   ├── AuthenticationError (401)    # Invalid credentials
│   ├── NotFoundError (404)          # Endpoint not found
│   ├── ServerError (5xx)            # Server-side errors
│   └── ConnectionError              # Network issues
├── ProcessorError                   # Data processing errors
│   ├── FileNotFoundError           # Input file missing
│   ├── InvalidFormatError          # Malformed data
│   └── ValidationError              # Business rule violations
└── ConfigurationError               # Config issues
```

### Error Recovery Strategies

#### 1. HTTP Retry Logic
```python
for attempt in range(retry_count):
    try:
        response = session.post(url, **kwargs)
        if response.status_code in [200, 201]:
            return response.json()
    except (Timeout, ConnectionError) as e:
        if attempt < retry_count - 1:
            time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
        else:
            raise JogetAPIError(f"Max retries exceeded: {e}")
```

#### 2. Batch Processing Recovery
```python
def batch_post_with_recovery(records):
    results = {"successful": [], "failed": []}

    for record in records:
        try:
            result = post(record)
            results["successful"].append(result)
        except JogetAPIError as e:
            results["failed"].append({
                "record": record,
                "error": str(e)
            })
            if stop_on_error:
                break

    return results
```

#### 3. Validation Recovery
```python
def validate_with_recovery(records):
    valid = []
    invalid = []

    for record in records:
        missing = [f for f in required_fields if f not in record]
        if missing:
            # Try to provide defaults
            for field in missing:
                if field in default_values:
                    record[field] = default_values[field]
                else:
                    invalid.append(record)
                    continue
        valid.append(record)

    return valid, invalid
```

### Error Reporting

```python
# Structured error collection
{
    "total": 100,
    "successful": 95,
    "failed": 5,
    "errors": [
        {
            "index": 12,
            "record": {"id": "001"},
            "error": "Missing required field: name",
            "timestamp": "2024-01-01T10:00:00"
        }
    ],
    "warnings": [
        "Field 'description' truncated to 255 characters"
    ]
}
```

---

## Logging & Debugging

### Logging Configuration

#### Logger Hierarchy
```
joget_utility              # Root logger
├── joget_utility.client   # HTTP client operations
├── joget_utility.processor # Data processing
└── joget_utility.metadata # Batch processing
```

#### Log Levels and Usage

| Level | Usage | Example |
|-------|-------|---------|
| DEBUG | Detailed debugging info | Field values, HTTP payloads |
| INFO | Normal operation flow | Record counts, progress |
| WARNING | Recoverable issues | Missing optional fields |
| ERROR | Critical failures | API errors, invalid config |

#### Debug Mode Features

```python
# Enable with --debug flag
python joget_utility.py --endpoint test --input data.csv --debug

# Logs generated:
[DEBUG] POST Request to: http://localhost:8080/jw/api/form/test
[DEBUG] API ID: API-xxx-xxx
[DEBUG] Headers: {'accept': 'application/json', ...}
[DEBUG] Posted fields:
  - customerId: CUST001
  - customerName: John Doe
  - customerEmail: john@example.com
[DEBUG] Full payload:
{
  "customerId": "CUST001",
  "customerName": "John Doe",
  "customerEmail": "john@example.com"
}
[DEBUG] Response status: 201
[DEBUG] Response data: {"id": "generated_id", "status": "success"}
```

### Log File Management

```python
# Log rotation configuration
logging.handlers.RotatingFileHandler(
    filename='logs/joget_utility.log',
    maxBytes=10485760,  # 10MB
    backupCount=5
)

# Log file location
./logs/
├── joget_utility.log       # Current log
├── joget_utility.log.1     # Previous rotation
└── joget_utility.log.2     # Older rotation
```

### Performance Logging

```python
import time

def timed_operation(func):
    """Decorator for performance logging"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger.debug(f"{func.__name__} took {duration:.2f}s")
        return result
    return wrapper
```

---

## Security Considerations

### API Key Management

```python
# Best Practices:
1. Never hardcode API keys in source code
2. Use environment variables or secure vaults
3. Rotate keys regularly
4. Use different keys for dev/prod

# Environment variable usage
api_key = os.environ.get('JOGET_API_KEY')

# Secure configuration
config:
  api_key: ${JOGET_API_KEY}  # Reference env var
```

### Input Validation

```python
def sanitize_input(data: str) -> str:
    """Remove potentially dangerous characters"""
    # Prevent injection attacks
    dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
    for char in dangerous_chars:
        data = data.replace(char, '')
    return data.strip()
```

### Network Security

```python
# HTTPS enforcement
if not base_url.startswith('https://'):
    logger.warning("Using insecure HTTP connection")

# Certificate verification
session.verify = True  # Verify SSL certificates

# Timeout protection
session.timeout = 30  # Prevent hanging connections
```

### Data Privacy

```python
# Sensitive field masking in logs
SENSITIVE_FIELDS = ['password', 'api_key', 'token', 'ssn']

def mask_sensitive(data: Dict) -> Dict:
    """Mask sensitive fields for logging"""
    masked = data.copy()
    for field in SENSITIVE_FIELDS:
        if field in masked:
            masked[field] = '***MASKED***'
    return masked
```

---

## Performance Optimization

### Batch Processing Optimization

```python
# Optimal batch sizes
BATCH_SIZE = 100  # Records per request

def optimized_batch_post(records):
    """Process in optimized chunks"""
    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i:i + BATCH_SIZE]
        results = client.batch_post(batch)
        yield results
```

### Connection Pooling

```python
# Reuse connections
session = requests.Session()
session.mount('http://', HTTPAdapter(
    pool_connections=10,
    pool_maxsize=20,
    max_retries=3
))
```

### Memory Management

```python
# Stream large files
def stream_csv(file_path):
    """Memory-efficient CSV reading"""
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            yield row  # Process one row at a time
```

### Caching Strategy

```python
# Cache configuration
@functools.lru_cache(maxsize=128)
def get_endpoint_config(endpoint_name):
    """Cache endpoint configurations"""
    return config['endpoints'].get(endpoint_name)
```

### Performance Metrics

```python
# Throughput tracking
class PerformanceMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.record_count = 0

    def record_processed(self):
        self.record_count += 1

    def get_throughput(self):
        elapsed = time.time() - self.start_time
        return self.record_count / elapsed if elapsed > 0 else 0
```

---

## Extension Guide

### Adding New Processors

```python
# custom_processor.py
from processors.base import BaseProcessor

class XMLProcessor(BaseProcessor):
    """Custom XML processor"""

    def read_file(self, file_path: Path) -> List[Dict]:
        """Parse XML file"""
        import xml.etree.ElementTree as ET
        tree = ET.parse(file_path)
        root = tree.getroot()

        records = []
        for element in root.findall('.//record'):
            record = {}
            for child in element:
                record[child.tag] = child.text
            records.append(record)
        return records
```

### Adding Custom Validators

```python
# validators.py
class EmailValidator:
    """Validate email fields"""

    @staticmethod
    def validate(email: str) -> bool:
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

# Usage in processor
def validate_record(self, record):
    if 'email' in record:
        if not EmailValidator.validate(record['email']):
            self.errors.append(f"Invalid email: {record['email']}")
            return False
    return True
```

### Custom Error Handlers

```python
# error_handlers.py
class RetryableError(JogetAPIError):
    """Errors that should trigger retry"""
    pass

class PermanentError(JogetAPIError):
    """Errors that should not retry"""
    pass

def handle_api_response(response):
    if response.status_code in [500, 502, 503]:
        raise RetryableError("Server temporarily unavailable")
    elif response.status_code == 400:
        raise PermanentError("Invalid request format")
```

### Plugin System

```python
# plugin_loader.py
import importlib
import os

class PluginLoader:
    """Dynamic plugin loading"""

    @staticmethod
    def load_plugins(plugin_dir='plugins'):
        plugins = {}
        for file in os.listdir(plugin_dir):
            if file.endswith('_plugin.py'):
                module_name = file[:-3]
                module = importlib.import_module(f'{plugin_dir}.{module_name}')
                if hasattr(module, 'register'):
                    plugins[module_name] = module.register()
        return plugins
```

---

## Testing Strategy

### Unit Testing Structure

```python
# test_joget_client.py
import unittest
from unittest.mock import Mock, patch
from joget_client import JogetClient

class TestJogetClient(unittest.TestCase):
    def setUp(self):
        self.client = JogetClient(
            base_url="http://test.server/api",
            api_key="test_key"
        )

    @patch('requests.Session.post')
    def test_post_success(self, mock_post):
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {"id": "123"}

        result = self.client.post(
            endpoint="test",
            api_id="API-test",
            data={"field": "value"}
        )

        self.assertEqual(result["id"], "123")
        mock_post.assert_called_once()
```

### Integration Testing

```python
# test_integration.py
class IntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Setup test environment"""
        cls.test_server = start_test_server()
        cls.client = JogetClient(base_url="http://localhost:8888")

    def test_end_to_end_import(self):
        """Test complete import workflow"""
        # Create test file
        test_data = [
            {"code": "TEST1", "name": "Test One"},
            {"code": "TEST2", "name": "Test Two"}
        ]

        # Process file
        processor = CSVProcessor()
        records = processor.read_file("test.csv")

        # Send to server
        results = self.client.batch_post(
            endpoint="test",
            api_id="API-test",
            records=records
        )

        # Verify results
        self.assertEqual(results["successful"], 2)
        self.assertEqual(results["failed"], 0)
```

### Test Data Generation

```python
# test_data_generator.py
import random
import string

def generate_test_records(count=100):
    """Generate test data"""
    records = []
    for i in range(count):
        records.append({
            "code": f"CODE_{i:04d}",
            "name": ''.join(random.choices(string.ascii_letters, k=10)),
            "value": random.randint(1, 1000)
        })
    return records
```

### Performance Testing

```python
# test_performance.py
import time

class PerformanceTest(unittest.TestCase):
    def test_batch_throughput(self):
        """Test batch processing performance"""
        records = generate_test_records(1000)

        start_time = time.time()
        results = self.client.batch_post(
            endpoint="test",
            api_id="API-test",
            records=records
        )
        duration = time.time() - start_time

        throughput = len(records) / duration
        self.assertGreater(throughput, 100)  # Min 100 records/second
```

---

## Deployment Guide

### System Requirements

```yaml
# Minimum Requirements
python: ">=3.6"
memory: 512MB
disk: 100MB
network: HTTP/HTTPS access to Joget server

# Recommended Requirements
python: ">=3.8"
memory: 1GB
disk: 500MB
cpu: 2 cores
```

### Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/yourorg/joget-utility.git
cd joget-utility

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure application
cp config/joget.yaml.example config/joget.yaml
# Edit config/joget.yaml with your settings

# 5. Test connection
python joget_utility.py --test

# 6. Create necessary directories
mkdir -p data/metadata data/csv data/json logs
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/logs /app/data

VOLUME ["/app/config", "/app/data", "/app/logs"]

ENTRYPOINT ["python", "joget_utility.py"]
```

```bash
# Build and run
docker build -t joget-utility .
docker run -v $(pwd)/config:/app/config \
           -v $(pwd)/data:/app/data \
           -v $(pwd)/logs:/app/logs \
           joget-utility --list
```

### Production Configuration

```yaml
# config/production.yaml
base_url: https://production.server/jw/api/form
default_api_key: ${JOGET_API_KEY}  # From environment

connection:
  timeout: 60
  retry_count: 5
  retry_delay: 5

logging:
  level: WARNING
  file: /var/log/joget_utility/app.log

data_paths:
  default: /data/joget
  metadata: /data/joget/metadata
```

### Monitoring & Alerting

```python
# monitoring.py
class HealthCheck:
    """Application health monitoring"""

    @staticmethod
    def check_connectivity():
        """Verify Joget server connectivity"""
        client = JogetClient(base_url=config['base_url'])
        return client.test_connection()

    @staticmethod
    def check_disk_space():
        """Verify adequate disk space"""
        import shutil
        usage = shutil.disk_usage('/')
        return usage.free > 100 * 1024 * 1024  # 100MB free

    @staticmethod
    def check_log_rotation():
        """Ensure logs are rotating"""
        log_file = Path('logs/joget_utility.log')
        if log_file.exists():
            return log_file.stat().st_size < 50 * 1024 * 1024  # < 50MB
        return True
```

### Backup & Recovery

```bash
#!/bin/bash
# backup.sh

# Backup configuration and data
BACKUP_DIR="/backups/joget_utility/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Backup configuration
cp -r config/ "$BACKUP_DIR/config"

# Backup processed data logs
cp -r logs/ "$BACKUP_DIR/logs"

# Backup data files
cp -r data/ "$BACKUP_DIR/data"

# Compress backup
tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"

# Retain last 30 days of backups
find /backups/joget_utility -name "*.tar.gz" -mtime +30 -delete
```

### Troubleshooting Guide

| Issue | Cause | Solution |
|-------|-------|----------|
| Import fails silently | Missing error handling | Enable debug logging |
| Slow performance | Large batch sizes | Reduce batch size in config |
| Memory errors | Large files | Use streaming mode |
| Connection timeouts | Network issues | Increase timeout values |
| Authentication failures | Expired API keys | Regenerate API keys |

---

## Appendices

### A. Configuration Schema

```yaml
$schema: http://json-schema.org/draft-07/schema#
type: object
required: [base_url]
properties:
  base_url:
    type: string
    format: uri
  default_api_key:
    type: string
  data_paths:
    type: object
    properties:
      default: {type: string}
      metadata: {type: string}
      csv: {type: string}
      json: {type: string}
  connection:
    type: object
    properties:
      timeout: {type: integer, minimum: 1}
      retry_count: {type: integer, minimum: 0}
      retry_delay: {type: number, minimum: 0}
  logging:
    type: object
    properties:
      level: {enum: [DEBUG, INFO, WARNING, ERROR]}
      file: {type: string}
      format: {type: string}
```

### B. API Response Formats

```json
// Success Response
{
  "status": "success",
  "id": "generated_record_id",
  "message": "Record created successfully"
}

// Error Response
{
  "status": "error",
  "code": "VALIDATION_ERROR",
  "message": "Missing required field: customerName",
  "details": {
    "field": "customerName",
    "requirement": "required"
  }
}

// Batch Response
{
  "total": 100,
  "successful": 95,
  "failed": 5,
  "errors": [
    {
      "index": 23,
      "error": "Duplicate key violation",
      "record": {"id": "DUP001"}
    }
  ]
}
```

### C. Performance Benchmarks

| Operation | Records | Time | Throughput |
|-----------|---------|------|------------|
| CSV Read | 10,000 | 0.5s | 20,000/s |
| JSON Parse | 10,000 | 0.8s | 12,500/s |
| Validation | 10,000 | 1.2s | 8,333/s |
| HTTP POST | 1,000 | 10s | 100/s |
| Batch Process | 10,000 | 15s | 667/s |

### D. Glossary

| Term | Definition |
|------|------------|
| Endpoint | Joget form API endpoint for data submission |
| Metadata | Lookup data with code/name structure |
| Batch Processing | Processing multiple endpoints in sequence |
| Field Mapping | Transformation of source fields to target fields |
| Dry Run | Preview mode without actual data posting |
| API ID | Unique identifier for Joget endpoint |
| API Key | Authentication token for API access |

---

**Document Version**: 1.0.0
**Last Updated**: 2024
**Maintainer**: Development Team
**License**: See LICENSE file