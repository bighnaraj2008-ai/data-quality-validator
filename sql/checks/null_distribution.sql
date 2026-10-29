-- ============================================================================
-- SQL CHECK: null_distribution
-- Purpose: Compute per-column null counts and null fractions for a table,
--          flagging columns whose null ratio exceeds the configured threshold.
--
-- Dialect: ANSI SQL / PostgreSQL / SQLite
-- ============================================================================

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
