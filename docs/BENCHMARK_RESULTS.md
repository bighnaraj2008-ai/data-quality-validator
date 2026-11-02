# Baseline Performance Benchmark Results

Recorded using [`tests/benchmarks/bench_validator.py`](../tests/benchmarks/bench_validator.py)
under standardized multi-column anomaly detection loads (10 columns: 1 primary key,
6 numeric, 3 string; 2.0% injected anomaly rate across nulls, duplicates, and range
outliers).

---

## 1. Throughput & Latency Baseline (`v1.0.0`)

| Dataset Rows | Columns | Checks Run | Duration (ms) | Throughput (Rows/s) | p95 Latency (ms) | Status |
|-------------:|--------:|-----------:|--------------:|--------------------:|-----------------:|:------:|
| 1,000        | 10      | 4          | 5.88          | 170,224             | 2.95             | FAIL (expected anomalies caught) |
| 5,000        | 10      | 4          | 2.94          | 1,698,254           | 1.24             | FAIL (expected anomalies caught) |
| 10,000       | 10      | 4          | 7.45          | 1,342,281           | 3.10             | FAIL (expected anomalies caught) |
| 50,000       | 10      | 4          | 34.80         | 1,436,781           | 14.20            | FAIL (expected anomalies caught) |
| 100,000      | 10      | 4          | 72.10         | 1,386,962           | 29.40            | FAIL (expected anomalies caught) |

---

## 2. Memory Allocation Profile (`tracemalloc`)

Measured using [`tests/benchmarks/bench_memory.py`](../tests/benchmarks/bench_memory.py):

| Dataset Rows | Peak Heap Allocation (MB) | Post-Validation Retention (MB) |
|-------------:|--------------------------:|-------------------------------:|
| 1,000        | 0.48 MB                   | 0.06 MB                        |
| 10,000       | 3.92 MB                   | 0.14 MB                        |
| 50,000       | 18.60 MB                  | 0.32 MB                        |

---

## 3. Query & Engine Optimization Findings

1. **Vectorized Pandas Inspection:** Computing per-column null ratios with `df.isnull().sum()`
   and vectorized bounds checks keeps per-check latency under `30 ms` at `100,000` rows.
2. **Primary Key Hash Deduplication:** Pre-indexing composite/primary key slices avoids
   full-row string comparisons when explicit primary keys are declared in `BaselineSchema`.
3. **Database Pushdown (`sql/checks/`):** For datasets exceeding client memory, pure SQL
   templates execute aggregation directly on warehouse compute nodes with `LIMIT :sample_limit`
   to cap wire transfer overhead.
