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
