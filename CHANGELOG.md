# Changelog

All notable changes to the `data-quality-validator` project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-10-31

### Added
- Comprehensive YAML rule authoring guide in `docs/RULE_AUTHORING.md` covering rule syntax, threshold parameters, severity mapping, and alert webhooks.
- In-warehouse pure SQL check catalog in `docs/SQL_CHECK_CATALOG.md` detailing parameter conventions, null checks, uniqueness constraints, and schema drift queries across 5 warehouse dialects.
- System sequence and component architecture diagrams in `docs/ARCHITECTURE.mmd`.
- Comprehensive Python API reference in `docs/API_REFERENCE.md` for core validator engine, checkers, and configuration loader.
- Production deployment runbook in `docs/DEPLOYMENT_GUIDE.md` with Docker containerization, Kubernetes CronJobs, and Airflow DAG integration.
- Incident diagnostics playbook in `docs/DIAGNOSTICS.md` and schema drift triage runbook in `docs/INCIDENT_PLAYBOOK.md`.
- Security hardening guidelines in `docs/SECURITY_HARDENING.md` covering read-only roles, SQL injection protection, and credential management.
- Contribution guidelines in `docs/CONTRIBUTORS_GUIDE.md` and project FAQ in `docs/FAQ.md`.
- Data engineering glossary in `docs/GLOSSARY.md` and throughput benchmark report in `docs/BENCHMARK_REPORT.md`.
- Automated markdown documentation link and syntax validation tool in `scripts/validate_docs.py`.
- Documentation integrity CI workflow `.github/workflows/docs_check.yml`.
- Schema evolution migration guide in `docs/MIGRATION_V2.md`.
- Performance and query optimization guide in `docs/PERFORMANCE_TUNING.md`.

## [0.3.0] - 2026-10-30

### Added
- Comprehensive test fixture catalog under `tests/fixtures/` (`clean_dataset.csv`, `drifted_dataset.csv`, `null_anomaly.json`, `duplicate_keys.csv`).
- Dedicated test harness modules: `tests/harness/mock_db.py` for simulated warehouse queries and `tests/harness/assertions.py` for quality score assertions.
- Modular edge-case test suites in `tests/edge_cases/` for type mismatches, empty payloads, threshold breach limits, and silent drift.
- Integration test suite in `tests/integration/` validating full pipeline flows and pure SQL check templates.
- Performance and stress benchmarks in `tests/performance/` and `tests/stress/` with > 10,000 rows/second throughput assertions.
- Memory consumption profiling suite in `tests/memory/test_memory_profiler.py` ensuring < 60MB peak memory footprint.
- Automation test scripts: `scripts/run_unit_tests.sh`, `scripts/run_profiler.sh`, and `scripts/generate_test_report.py`.
- Documentation additions: `docs/TEST_COVERAGE.md`, `docs/EDGE_CASES.md`, `docs/FIXTURE_GUIDE.md`, and `docs/BENCHMARK_TEMPLATE.md`.
- GitHub Actions CI workflow `.github/workflows/test_coverage.yml` for continuous testing and coverage verification.

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

<!-- Day 3 Advanced Documentation Sprint Finalized -->
