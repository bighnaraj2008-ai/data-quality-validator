-- ============================================================================
-- SQL CHECK: schema_drift
-- Purpose: Detect table schema drift between a target (incoming) table and a
--          baseline reference schema (missing, added, and type mismatches).
--
-- Dialect: ANSI SQL / PostgreSQL / MySQL
-- ============================================================================

-- Missing columns (defined in baseline but absent in target table)
SELECT
    :baseline_schema AS baseline_schema,
    :baseline_table AS baseline_table,
    b.column_name AS missing_column,
    b.data_type AS expected_data_type,
    NULL AS actual_data_type,
    'missing' AS drift_type
FROM information_schema.columns AS b
LEFT JOIN information_schema.columns AS t
    ON b.column_name = t.column_name
   AND t.table_schema = :target_schema
   AND t.table_name = :target_table
WHERE b.table_schema = :baseline_schema
  AND b.table_name = :baseline_table
  AND t.column_name IS NULL

UNION ALL

-- Added columns (present in target table but not in baseline schema)
SELECT
    :target_schema AS target_schema,
    :target_table AS target_table,
    t.column_name AS added_column,
    NULL AS expected_data_type,
    t.data_type AS actual_data_type,
    'added' AS drift_type
FROM information_schema.columns AS t
LEFT JOIN information_schema.columns AS b
    ON t.column_name = b.column_name
   AND b.table_schema = :baseline_schema
   AND b.table_name = :baseline_table
WHERE t.table_schema = :target_schema
  AND t.table_name = :target_table
  AND b.column_name IS NULL;
