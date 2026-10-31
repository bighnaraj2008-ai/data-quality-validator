# Frequently Asked Questions (FAQ)

### General

#### Q: What is `data-quality-validator`?
**A:** It is a modular, high-throughput data quality and schema testing framework
providing dual-mode validation: an in-memory Python engine for Pandas / PyArrow
dataframes and an in-warehouse SQL check catalog for direct query execution.

#### Q: How does in-memory validation differ from in-warehouse SQL validation?
**A:** In-memory validation loads datasets into client memory to inspect dataframes
with microsecond latency for medium-sized extracts (< 1M rows). In-warehouse
pure SQL checks execute directly on database nodes (Snowflake, BigQuery, Postgres)
without extracting large datasets across the network.

---

### Configuration & Rules

#### Q: How do I override thresholds dynamically in CI/CD pipelines?
**A:** Set environment variables prefixed with `DQ_`. For example:
```bash
export DQ_NULL_THRESHOLD=0.08
export DQ_STRICT_SCHEMA=true
```

#### Q: How can I ignore newly added columns in schema drift detection?
**A:** Set `checks.schema_drift.allow_unexpected_columns: true` in your YAML rule
configuration file.

#### Q: What is the difference between `WARN` and `FAIL` status?
**A:** `WARN` records a degraded condition in telemetry but leaves the overall pipeline
exit code as `0`. `FAIL` indicates a critical threshold breach that sets the
overall status to `FAIL` and exits with code `1`.

---

### Performance & Scaling

#### Q: Can `data-quality-validator` validate datasets larger than RAM?
**A:** Yes. Use the pure SQL check templates (`sql/checks/`) to validate billions
of rows directly within Snowflake, BigQuery, or PostgreSQL without memory limits.

#### Q: What is the average throughput for in-memory checks?
**A:** The in-memory engine achieves throughput > 10,000 rows/second for multi-rule
validation suites on standard modern CPUs.
