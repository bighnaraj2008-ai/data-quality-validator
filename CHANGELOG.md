# Changelog

All notable changes to the `data-quality-validator` project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-10-29

### Added
- Modular validation pipeline architecture decoupling checkers from the execution engine.
- `NullChecker` with configurable per-column null thresholds and strict non-nullable constraints.
- `DuplicateChecker` for row-level duplication and primary key collision detection.
- `DriftDetector` supporting schema column matching, type comparison, and anomaly reporting.
- `RangeChecker` providing numerical boundary bounds and minimum/maximum rule validation.
- Pure SQL validation check templates in `sql/checks/` (`null_distribution`, `duplicate_keys`, `schema_drift`, `row_count_anomaly`).
- Declarative YAML configuration loader in `src/config/loader.py` with dynamic environment override parsing.
- Pytest comprehensive unit test suite covering core components and validation rules.
- CLI script entrypoints `run_validation.py` and telemetry reporter `generate_report.py`.
- SQLFluff ANSI configuration and GitHub Actions continuous integration workflow.
- End-to-end smoke test script `smoke_test.sh`.

### Changed
- Refactored monolithic inspection logic into isolated, single-responsibility check classes.
- Enhanced runner error handling with isolated exception boundaries preventing pipeline aborts.

### Security
- Added strict `.gitignore` blocking environment files, local caches, and database files.
