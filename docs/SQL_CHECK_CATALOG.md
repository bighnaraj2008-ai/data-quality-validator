# Pure SQL Check Catalog

This catalog documents the pure SQL validation check templates maintained under
`sql/checks/`. Each template is a read-only, parameterized query that executes
directly inside a data warehouse (Snowflake, BigQuery, PostgreSQL, MySQL,
SQLite, DuckDB) so that quality checks never require extracting large datasets
into client memory.

All checks return a standardized result shape:

| Column | Type | Description |
|:-------|:-----|:------------|
| `check_name` | string | Name of the executed check. |
| `column_name` | string | Target column (or `NULL` for table-level checks). |
| `failed_count` | integer | Number of violating rows / values. |
| `violation_rate` | float | Fraction of failures (0.0-1.0). |
| `status` | string | `PASS`, `WARN`, or `FAIL`. |

---

## 1. Check Index

| Check | File | Detects | Default Severity |
|:------|:-----|:--------|:-----------------|
| Null distribution | `null_distribution.sql` | Per-column null counts above threshold | `FAIL` |
| Uniqueness / duplicate keys | `duplicate_keys.sql` | Primary key and composite key collisions | `FAIL` |
| Row count anomaly | `row_count_anomaly.sql` | Volume outside `[min, max]` bounds | `FAIL` |
| Schema drift | `schema_drift.sql` | Missing, added, and type-mismatched columns | `WARN` / `FAIL` |

---

## 2. Parameter Conventions

Templates use named bind parameters prefixed with `:`:

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `:table_name` | identifier | Target table or view name. |
| `:table_schema` | identifier | Schema containing the target table. |
| `:pk_column` | identifier | Primary key column (single or comma-separated composite key). |
| `:sample_limit` | integer | Max offending keys to return. |
| `:null_threshold` | float | Max allowed null fraction (0.0-1.0). |
| `:min_expected_rows` | integer | Minimum acceptable row count. |
| `:max_expected_rows` | integer | Maximum acceptable row count (optional). |
| `:baseline_schema` / `:baseline_table` | identifier | Reference schema for drift comparison. |
| `:target_schema` / `:target_table` | identifier | Table being inspected for drift. |

---

## 3. Check Details

### 3.1 Null Distribution — `null_distribution.sql`

**Purpose.** Computes per-column null counts and null fractions, flagging any
column whose null ratio exceeds `:null_threshold`.

**Dialects.** ANSI SQL, PostgreSQL, SQLite, Snowflake, BigQuery, DuckDB.

**Parameters.** `:table_schema`, `:table_name`, `:null_threshold`.

**Output.** One row per column with `null_fraction` and `null_status`
(`within_threshold` / `threshold_exceeded` / `empty_table`).

**Severity Mapping.** `threshold_exceeded` -> `FAIL`; `empty_table` -> `FAIL`;
otherwise `PASS`.

**Example Query.**

```sql
-- Bind: table_schema='public', table_name='customers', null_threshold=0.05
SELECT
    :table_schema AS table_schema,
    :table_name AS table_name,
    c.column_name AS column_name,
    COUNT(*) AS total_rows,
    COUNT(c.column_name) AS non_null_count,
    (COUNT(*) - COUNT(c.column_name)) AS null_count,
    ROUND(
        1.0 * (COUNT(*) - COUNT(c.column_name)) / NULLIF(COUNT(*), 0),
        4
    ) AS null_fraction,
    :null_threshold AS max_allowed_null_fraction,
    CASE
        WHEN COUNT(*) = 0 THEN 'empty_table'
        WHEN 1.0 * (COUNT(*) - COUNT(c.column_name)) / NULLIF(COUNT(*), 0) > :null_threshold
            THEN 'threshold_exceeded'
        ELSE 'within_threshold'
    END AS null_status
FROM information_schema.columns AS c
CROSS JOIN :table_name AS t
WHERE c.table_schema = :table_schema
  AND c.table_name = :table_name
GROUP BY c.column_name
ORDER BY null_fraction DESC, column_name;
```

**Warehouse Execution Notes:**
- On PostgreSQL and Snowflake, `information_schema.columns` provides instant schema inspection.
- On SQLite, table column names can be discovered via `PRAGMA table_info()` prior to executing the aggregate count.

---

### 3.2 Uniqueness Constraints — `duplicate_keys.sql`

**Purpose.** Identifies duplicate primary key or composite key collisions and
surfaces offending keys with occurrence counts.

**Dialects.** ANSI SQL, PostgreSQL, SQLite, Snowflake, BigQuery, DuckDB.

**Parameters.** `:table_name`, `:pk_column`, `:sample_limit`.

**Output.** One row per colliding key value with `occurrence_count > 1`, ordered
by count descending, capped at `:sample_limit`.

**Severity Mapping.** Any rows returned -> `FAIL`; empty result -> `PASS`.

**Example Query.**

```sql
-- Bind: table_name='orders', pk_column='order_id', sample_limit=50
SELECT
    :pk_column AS primary_key_value,
    COUNT(*) AS occurrence_count
FROM :table_name
GROUP BY :pk_column
HAVING COUNT(*) > 1
ORDER BY occurrence_count DESC
LIMIT :sample_limit;
```

> **Composite Keys.** For composite keys, bind `:pk_column` as the
> comma-separated key list, e.g. `order_id, line_number`.

---

### 3.3 Row Count Anomaly — `row_count_anomaly.sql`

**Purpose.** Verifies dataset record volume falls within expected boundaries to
detect empty tables, dropped partitions, or unexpected spikes.

**Dialects.** ANSI SQL, PostgreSQL, SQLite, Snowflake, BigQuery, DuckDB.

**Parameters.** `:table_name`, `:min_expected_rows`, `:max_expected_rows`.

**Output.** Single row with `actual_row_count` and `volume_status`
(`volume_too_low` / `volume_too_high` / `volume_normal`).

**Severity Mapping.** `volume_too_low` / `volume_too_high` -> `FAIL`;
`volume_normal` -> `PASS`.

**Example Query.**

```sql
-- Bind: table_name='events', min_expected_rows=1000, max_expected_rows=1000000
SELECT
    :table_name AS table_name,
    COUNT(*) AS actual_row_count,
    :min_expected_rows AS min_expected_rows,
    :max_expected_rows AS max_expected_rows,
    CASE
        WHEN COUNT(*) < :min_expected_rows THEN 'volume_too_low'
        WHEN :max_expected_rows IS NOT NULL AND COUNT(*) > :max_expected_rows THEN 'volume_too_high'
        ELSE 'volume_normal'
    END AS volume_status
FROM :table_name;
```
