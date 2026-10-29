# Data Quality Validator

[![CI Build](https://github.com/bighnaraj2008-ai/data-quality-validator/actions/workflows/validator_ci.yml/badge.svg)](https://github.com/bighnaraj2008-ai/data-quality-validator/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Flake8](https://img.shields.io/badge/code%20style-flake8-green.svg)](https://flake8.pycqa.org/)

A high-performance, modular data validation and quality assurance framework designed for modern data engineering pipelines.

## Overview

`data-quality-validator` provides declarative, automated data quality testing for data ingestion and ETL/ELT pipelines. It offers dual-mode validation:
- **In-Memory Engine**: High-throughput validation across Pandas / PyArrow dataframes.
- **In-Database SQL Engine**: Pure SQL check templates for direct execution in data warehouses (Snowflake, BigQuery, PostgreSQL, DuckDB).

### Key Features
- **Null Value Inspection**: Quantifies missing data against configurable threshold ratios.
- **Duplicate Detection**: Identifies row-level duplicates and candidate primary key collisions.
- **Schema Drift Monitoring**: Detects missing columns, unmapped additions, and data type shifts.
- **Range & Boundary Verification**: Validates numerical bounds and statistical bounds.
- **Declarative YAML Rules**: Flexible configuration with environment variable override support.
- **Audit Reports**: Produces machine-readable JSON metrics and markdown summaries.

---

## Modular Architecture

The framework is decoupled into distinct subsystems for maintainability and scalability:

```text
data-quality-validator/
├── src/validator/             # Core Python validation engine
│   ├── core.py                # Pipeline runner & error-isolated orchestrator
│   ├── null_checker.py        # Null distribution & non-nullable assertions
│   ├── duplicate_checker.py   # Row & PK uniqueness validator
│   ├── drift_detector.py      # Schema drift & column type checking
│   └── range_checker.py       # Numerical range boundary check
├── src/config/                # Declarative configuration subsystem
│   ├── loader.py              # YAML parser with DQ_ environment overrides
│   └── validator_config.yaml  # Default rules & thresholds template
├── sql/checks/                # Pure SQL verification templates
│   ├── null_distribution.sql  # Database-native null checks
│   ├── duplicate_keys.sql     # Key collision queries
│   ├── schema_drift.sql       # Information schema drift views
│   └── row_count_anomaly.sql  # Row volume anomaly detection
└── scripts/                   # CLI execution & telemetry reporting
    ├── run_validation.py      # CLI execution entrypoint
    └── generate_report.py     # JSON and Markdown telemetry exporter
```

Detailed architectural diagrams and pipeline execution flow are documented in [`docs/ARCHITECTURE_REFACTOR.md`](docs/ARCHITECTURE_REFACTOR.md).

---

## Quickstart

### 1. Installation

Clone the repository and set up a Python virtual environment:

```bash
git clone https://github.com/bighnaraj2008-ai/data-quality-validator.git
cd data-quality-validator

python -m venv venv
# Linux / macOS
source venv/bin/activate
# Windows PowerShell
.\venv\Scripts\Activate.ps1

pip install -e .
```

### 2. Running Data Validation

Execute the pipeline against a CSV or sample dataset:

```bash
# Run validation via the CLI wrapper
python scripts/run_validation.py --data sample_data.csv --config src/config/validator_config.yaml

# Generate an inspection report
python scripts/generate_report.py --input sample_data.csv --output report.json --format json
```

### 3. Running Unit Tests

Execute the automated test suite:

```bash
pytest tests/ -v
```
