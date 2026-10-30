# Test Coverage & Verification Architecture

## 1. Overview & Strategy

The `data-quality-validator` framework enforces a multi-tiered testing strategy designed to guarantee pipeline reliability, zero false alarms, and graceful error degradation across large datasets.

```
       +------------------------------------+
       |  Performance & Stress Benchmarks   |  (10k-100k rows, memory profile)
       +-----------------+------------------+
                         |
       +-----------------v------------------+
       |     Integration Test Suites        |  (End-to-end pipeline, SQL checks)
       +-----------------+------------------+
                         |
       +-----------------v------------------+
       |       Edge-Case Test Suites        |  (Threshold breach, empty payloads, drift)
       +-----------------+------------------+
                         |
       +-----------------v------------------+
       |        Core Unit Test Suite        |  (Drift, Null, Duplicate, Range checkers)
       +------------------------------------+
```

## 2. Test Architecture Layers

### Layer 1: Unit Test Suite (`tests/`)
- Tests modular check classes in isolation (`NullChecker`, `DuplicateChecker`, `DriftDetector`, `RangeChecker`).
- Validates configuration parser and dynamic environment variable override precedence.

### Layer 2: Edge-Case Test Suite (`tests/edge_cases/`)
- Exercises unusual inputs: empty DataFrames, missing CSV files, header-only datasets.
- Tests exact boundary threshold breaches (e.g. 0.2000 vs 0.2001 null ratios).
- Evaluates silent schema drift under lenient vs strict enforcement modes.

### Layer 3: Integration Test Suite (`tests/integration/`)
- Executes complete pipelines with `DataValidator` against realistic dataset fixtures.
- Validates pure ANSI SQL check templates using in-memory mock engines.

### Layer 4: Performance & Memory Profile Suite (`tests/performance/`, `tests/memory/`)
- Throughput validation (> 10,000 rows/second).
- Bounded memory footprint (< 60MB peak consumption).

## 3. Test Fixture Catalog

The test suite uses committed, reproducible fixtures under `tests/fixtures/`:

| Fixture File | Format | Records | Primary Anomaly Tested |
| :--- | :--- | :--- | :--- |
| `clean_dataset.csv` | CSV | 5 rows | Baseline clean data; must pass all checks with score 100.0%. |
| `drifted_dataset.csv` | CSV | 4 rows | Missing `email`, added `notes`, duplicate primary key `id=2`. |
| `null_anomaly.json` | JSON | 5 rows | 80% null injection spike on `name`, `email`, `age`, `income`. |
| `duplicate_keys.csv` | CSV | 5 rows | Duplicate primary keys on IDs `101` and `102`. |

## 4. Edge-Case Test Matrix

| Scenario | Target Checker | Expected Status | Assertion Rule |
| :--- | :--- | :--- | :--- |
| Severe column type mismatch (str in int col) | `DriftDetector` | `FAIL` | `type_mismatches` metric contains column |
| Non-numeric column evaluated in RangeChecker | `RangeChecker` | `FAIL` | Handled gracefully without Python crash |
| Empty DataFrame (0 rows, valid headers) | `NullChecker`, `DuplicateChecker` | `PASS` | 0% null rate, 0 duplicate rows |
| Non-existent CSV file path | `DataValidator` | `ERROR` | Pipeline records error status and trace |
| Corrupted non-CSV binary payload | `DataValidator` | `ERROR` | Catches decoding errors cleanly |
| Null fraction exactly at configured limit | `NullChecker` | `PASS` | Value <= threshold passes |
| Null fraction 1% above threshold | `NullChecker` | `FAIL` | Threshold breach reported |
| Single null in non-nullable column | `NullChecker` | `FAIL` | Non-nullable rule triggers strict failure |
| Added column in lenient mode (`strict=False`) | `DriftDetector` | `WARN` | Unmapped column surfaced in metrics |
| Added column in strict mode (`strict=True`) | `DriftDetector` | `FAIL` | Unmapped column fails validation |
