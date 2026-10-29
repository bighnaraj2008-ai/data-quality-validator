# Architecture Refactoring Guide — Data Quality Validator

**Day 1 — Core Modularization, SQL Validation Rules, and Config Engine**

This document details the architectural refactoring undertaken on Day 1 to transform
`data-quality-validator` into a decoupled, high-performance data quality testing
and inspection suite.

---

## 1. Architectural Goals & Motivation

Modern data quality verification requires both application-level flexibility
(working with Pandas / Arrow dataframes in ingestion pipelines) and database-level
efficiency (pushing computations to data warehouses via SQL).

| Objective | Architectural Design |
|:----------|:---------------------|
| **Single-Responsibility Checkers** | Individual check modules (`NullChecker`, `DuplicateChecker`, `DriftDetector`, `RangeChecker`) isolated from the runner engine. |
| **Pure SQL Rule Templates** | Parameterized SQL templates under `sql/checks/` for database-native execution without data extraction. |
| **Declarative YAML Configuration** | Centralized `src/config/validator_config.yaml` specifying thresholds, non-nullable columns, and numerical bounds. |
| **Deterministic Result Structures** | Typed `CheckResult`, `CheckStatus`, and `ValidationReport` data objects providing telemetry metrics. |

---

## 2. Directory Layout

```text
data-quality-validator/
├── pyproject.toml              # Build & dependency metadata
├── Makefile                    # Developer automation targets
├── src/
│   ├── config/                 # Declarative configuration subsystem
│   │   ├── loader.py           # Configuration loader with env overrides
│   │   └── validator_config.yaml # Base configuration template
│   └── validator/              # Core validation engine
│       ├── __init__.py         # Package exports
│       ├── core.py             # DataValidator pipeline orchestrator
│       ├── null_checker.py     # Null inspection check
│       ├── duplicate_checker.py # Row & PK duplicate check
│       ├── drift_detector.py   # Schema drift & type mismatch check
│       └── range_checker.py    # Numerical boundary validation check
├── sql/
│   └── checks/                 # Pure SQL check query templates
│       ├── __init__.sql        # Module index
│       ├── null_distribution.sql # Null distribution check
│       ├── duplicate_keys.sql  # Primary key collisions
│       ├── schema_drift.sql    # Column mapping & drift view
│       └── row_count_anomaly.sql # Row volume thresholds
├── tests/                      # Pytest unit & integration test suites
│   ├── test_null_checker.py
│   ├── test_duplicate_checker.py
│   ├── test_drift_detector.py
│   └── test_config_loader.py
├── scripts/                    # CLI execution & reporting helpers
│   ├── run_validation.py
│   ├── generate_report.py
│   └── smoke_test.sh
└── docs/                       # Technical documentation
    ├── ARCHITECTURE_REFACTOR.md
    └── SQL_CHECKS_GUIDE.md
```

---

## 3. Core Component Architecture

The refactored validator adheres to the following decoupled architecture:

```text
[Data Input (DataFrame / SQL Table)]
              │
              ▼
   ┌──────────────────────┐
   │  DataValidator Core  │ ◄─── [src/config/validator_config.yaml]
   └──────────┬───────────┘
              │ (dispatches to independent checks)
      ┌───────┼───────┬────────┐
      ▼       ▼       ▼        ▼
    [Null]  [Dup]  [Drift]  [Range]
      │       │       │        │
      └───────┼───────┴────────┘
              ▼
   ┌──────────────────────┐
   │   ValidationReport   │
   └──────────┬───────────┘
              ├─► CLI Console Output
              ├─► JSON Telemetry Report
              └─► Markdown Audit Summary
```

---

## 4. Modular Validation Pipeline & Check Execution Flow

The validation pipeline follows a deterministic four-phase execution lifecycle:

### Phase 1: Configuration Resolution & Schema Binding
1. `ConfigLoader.load_config(path)` parses the YAML specification.
2. Environment variables with `DQ_` prefix are parsed to override configuration thresholds dynamically.
3. The expected schema (column names, types, constraints) is bound to the validator runner.

### Phase 2: Input Sanity & Volume Verification
1. Evaluates row count against `min_rows` and `max_rows` thresholds.
2. Checks table emptiness and triggers early failure if row count fails tolerance.

### Phase 3: Check Execution & Error Isolation
1. **Schema Drift Detection**: Evaluates missing columns, unexpected columns, and data type mismatches against expected schema.
2. **Null Value Inspection**: Analyzes null rates per column against individual column nullability thresholds.
3. **Duplicate Detection**: Identifies row duplicates and primary key collisions across specified candidate keys.
4. **Range & Boundary Check**: Asserts numerical bounds (`[min_val, max_val]`) across numerical features.
Each checker runs inside an isolated `try...except` boundary to prevent failure cascade.

### Phase 4: Report Synthesis & Exit Code Resolution
1. Results are aggregated into a `ValidationReport`.
2. Overall status (`PASS`, `WARN`, `FAIL`, `ERROR`) is derived.
3. Telemetry dictionary and serializable formats are generated.
