# Joget DX Toolkit

A comprehensive developer toolkit for Joget DX platform, providing tools for form generation, deployment, validation, and management.

## Features

- **Canonical Format**: Platform-agnostic YAML specification for forms
- **Multi-Format Parsers**: Convert Markdown, CSV, or YAML to canonical format
- **Form Builders**: Generate Joget DX JSON from canonical specifications
- **Deployers**: Deploy forms to Joget servers via API
- **Validators**: Validate form definitions and data integrity
- **CLI Interface**: Unified command-line tools (`joget-dx` or `jdx`)

## Architecture

```
Input Formats               Canonical Format           Platform Output
┌──────────────┐           ┌──────────────┐           ┌──────────────┐
│  Markdown    │──┐        │              │           │              │
│  Tables      │  │        │              │           │   Joget DX   │
└──────────────┘  ├──────▶ │     YAML     │──────────▶│     JSON     │
┌──────────────┐  │        │              │           │              │
│     CSV      │──┘        │  (Type-safe) │           └──────────────┘
└──────────────┘           └──────────────┘
```

## Quick Start

### Installation

```bash
cd joget-dx-toolkit
pip install -e .
```

### Convert Markdown Spec to Forms

```bash
# Step 1: Parse markdown to canonical YAML
joget-dx parse markdown form_specs.md -o specs/myapp.yaml

# Step 2: Build Joget forms from canonical spec
joget-dx build joget specs/myapp.yaml -o forms/

# Step 3: Deploy to Joget server
joget-dx deploy forms/*.json --app-id myApp --server http://localhost:8080
```

### All-in-One Deployment

```bash
joget-dx deploy --from-md form_specs.md --app-id myApp
```

## Canonical Format Example

```yaml
version: "1.0"
metadata:
  app_id: migrationCenter
  app_name: Migration Center

forms:
  - id: deployment_jobs
    name: Deployment Jobs
    table: app_fd_deployment_jobs

    fields:
      - id: job_id
        type: text
        label: Job ID
        size: 100
        required: true
        primary_key: true

      - id: job_type
        type: select
        label: Job Type
        required: true
        options:
          - export
          - import
```

## Command Reference

### Parse Commands

```bash
# Parse markdown tables to canonical YAML
joget-dx parse markdown spec.md -o output.yaml

# Parse CSV to canonical YAML
joget-dx parse csv data.csv -o output.yaml

# Validate canonical YAML
joget-dx validate specs/myapp.yaml
```

### Build Commands

```bash
# Build Joget forms from canonical spec
joget-dx build joget specs/myapp.yaml -o forms/

# Build with custom options
joget-dx build joget specs/myapp.yaml -o forms/ --create-api --create-crud
```

### Deploy Commands

```bash
# Deploy forms to Joget server
joget-dx deploy forms/*.json --app-id myApp --server http://localhost:8080

# Deploy with credentials
joget-dx deploy forms/*.json --app-id myApp --api-key YOUR_KEY

# Dry run (preview without deploying)
joget-dx deploy forms/*.json --app-id myApp --dry-run
```

## Development

### Setup Development Environment

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
pytest --cov=joget_toolkit
```

### Code Quality

```bash
black joget_toolkit/
ruff check joget_toolkit/
mypy joget_toolkit/
```

## Project Structure

```
joget-dx-toolkit/
├── joget_toolkit/           # Main package
│   ├── specs/              # Canonical format models
│   ├── parsers/            # Input → Canonical
│   ├── builders/           # Canonical → Platform
│   ├── deployers/          # Deploy to servers
│   ├── validators/         # Validation logic
│   └── cli/                # CLI interface
├── tests/                  # Test suite
├── examples/               # Example specifications
└── docs/                   # Documentation
```

## Documentation

- [Canonical Format Specification](docs/CANONICAL_FORMAT.md)
- [Parser Development Guide](docs/PARSERS.md)
- [Builder Development Guide](docs/BUILDERS.md)
- [Migration Guide](docs/MIGRATION.md)

## License

MIT License - see LICENSE file for details
