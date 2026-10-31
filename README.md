# Data Quality Validator

[![CI Build](https://github.com/bighnaraj2008-ai/data-quality-validator/actions/workflows/validator_ci.yml/badge.svg)](https://github.com/bighnaraj2008-ai/data-quality-validator/actions)
[![Test Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](#)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Flake8](https://img.shields.io/badge/code%20style-flake8-green.svg)](https://flake8.pycqa.org/)
[![Day 3 Documentation](https://img.shields.io/badge/docs-Day%203%20Sprint-blueviolet.svg)](#)

A high-performance, modular data validation and quality assurance framework designed for modern data engineering pipelines.

## Overview

`data-quality-validator` delivers declarative, automated data quality testing for data ingestion and ETL/ELT pipelines. It provides dual-mode validation:
- **In-Memory Engine**: High-throughput validation across Pandas / PyArrow dataframes.
- **In-Database SQL Engine**: Pure SQL check templates for direct execution in data warehouses (Snowflake, BigQuery, PostgreSQL, DuckDB, SQLite).

### Key Features
- **Null Value Inspection**: Quantifies missing data against configurable threshold ratios.
- **Duplicate Detection**: Identifies row-level duplicates and candidate primary key collisions.
- **Schema Drift Monitoring**: Detects missing columns, unmapped additions, and data type shifts.
- **Range & Boundary Verification**: Validates numerical bounds and statistical bounds.
- **Declarative YAML Rules**: Flexible configuration with environment variable override support.
- **Audit Reports**: Produces machine-readable JSON metrics and markdown summaries.
