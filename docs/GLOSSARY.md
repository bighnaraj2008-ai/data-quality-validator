# Data Engineering & Data Quality Glossary

A comprehensive reference of key terminology used throughout `data-quality-validator`.

---

| Term | Definition |
|:-----|:-----------|
| **Schema Drift** | Unplanned structural changes to incoming data, including dropped columns, renamed attributes, unexpected fields, or shifted data types. |
| **Completeness** | The degree to which expected values are present rather than null, NaN, or empty strings. |
| **Cardinality** | The count of unique values contained in a column relative to the total number of records. |
| **Primary Key Collision** | A condition where two or more records share the identical primary or composite key value, violating relational uniqueness constraints. |
| **Freshness** | The measure of latency between data generation at the source and data arrival at the target destination. |
| **Distribution Anomaly** | A significant divergence in statistical properties (mean, variance, null ratio) compared to historical baseline distributions. |
| **Pure SQL Validation** | Executing validation logic entirely within the database engine via analytical SQL queries, avoiding client data extraction. |
| **Non-Nullable Constraint** | A strict assertion requiring that a specific column must contain zero null values across all records. |
| **Declarative Rules** | Defining *what* data quality conditions must hold (via YAML) rather than writing imperative procedural validation loops. |
| **Circuit Breaker** | An automated mechanism that stops downstream ETL/ELT pipeline execution immediately when upstream quality checks fail. |
| **Telemetry Payload** | Machine-readable JSON summary of validation execution results, timings, metrics, and failure diagnostics. |
| **Composite Key** | A primary key composed of two or more columns that collectively guarantee uniqueness across rows. |
