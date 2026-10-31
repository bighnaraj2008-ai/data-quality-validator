# Performance Tuning & Query Optimization Guide

Strategies to maximize validation throughput and minimize query latency across
large datasets.

---

## 1. In-Memory Engine Optimization (Pandas / PyArrow)

1. **Use PyArrow Engine for Parquet/CSV Ingestion:**
   ```python
   df = pd.read_csv("large_data.csv", engine="pyarrow")
   ```
2. **Column Pruning:** Pass `usecols` to load only columns targeted by rules.
3. **Downcast Numeric Dtypes:** Convert `int64` and `float64` to `int32` / `float32`
   to reduce memory footprint by 50%.

---

## 2. In-Warehouse SQL Query Optimization

1. **Pushdown Filtering:** Always filter partitioned columns (e.g. `WHERE dt = :ds`)
   before running duplicate key and null checks.
2. **Sampling Offending Keys:** Set `:sample_limit` (default 50) on `duplicate_keys.sql`
   to avoid streaming millions of collisions over the wire.
3. **Avoid Full Table Scans:** Ensure primary key candidate columns are backed by
   B-tree indices or clustering keys.
