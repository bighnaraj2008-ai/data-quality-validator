# SQL Validation Checks Authoring & Execution Guide

The `data-quality-validator` framework provides pure SQL validation check templates
under `sql/checks/`. These templates allow data engineers to execute quality checks
directly inside cloud data warehouses (e.g., Snowflake, BigQuery, PostgreSQL, DuckDB)
without pulling large datasets into client memory.

---

## 1. Directory Structure

```text
sql/checks/
├── __init__.sql             # Registry of pure SQL checks
├── null_distribution.sql    # Calculates null percentages and flags violations
├── duplicate_keys.sql       # Detects primary and composite key collisions
├── schema_drift.sql         # Compares information_schema with target schema
└── row_count_anomaly.sql    # Checks row volumes against configured boundaries
```

---

## 2. Template Conventions

All SQL check templates follow standard ANSI SQL conventions with parameter substitution
placeholders:

- `{{table_name}}`: Target table or view name
- `{{primary_key}}` or `{{key_column}}`: Primary identifier column(s)
- `{{min_rows}}` / `{{max_rows}}`: Bounded volume thresholds
- `{{max_null_rate}}`: Acceptable percentage of nulls (0.00 to 1.00)

Every check query returns a standardized schema:
```sql
SELECT
    check_name,
    column_name,
    failed_count,
    violation_rate,
    status  -- 'PASS', 'WARN', or 'FAIL'
FROM ...
```

---

## 3. Authoring New Checks

When adding a new SQL check:
1. Ensure idempotence: the check query must be read-only (`SELECT` only, no `INSERT/UPDATE`).
2. Include both `failed_count` and `violation_rate`.
3. Add the check reference into `sql/checks/__init__.sql`.
4. Run `sqlfluff lint sql/checks/<new_check>.sql` to verify SQL syntax and formatting standards.
