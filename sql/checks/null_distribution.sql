-- ============================================================================
-- SQL CHECK: null_distribution
-- Purpose: Compute per-column null counts and null fractions for a table,
--          flagging columns whose null ratio exceeds the configured threshold.
--
-- Dialect: ANSI SQL / PostgreSQL / SQLite
-- Note: example_schema / example_table / 0.1 are runtime substitution values.
-- ============================================================================

SELECT
    example_schema AS table_schema,
    example_table AS table_name,
    column_name,
    COUNT(*) AS total_rows,
    COUNT(column_name) AS non_null_count,
    (COUNT(*) - COUNT(column_name)) AS null_count,
    ROUND(
        1.0 * (COUNT(*) - COUNT(column_name)) / NULLIF(COUNT(*), 0),
        4
    ) AS null_fraction,
    0.1 AS max_allowed_null_fraction,
    CASE
        WHEN COUNT(*) = 0 THEN 'empty_table'
        WHEN 1.0 * (COUNT(*) - COUNT(column_name)) / NULLIF(COUNT(*), 0) > 0.1
            THEN 'threshold_exceeded'
        ELSE 'within_threshold'
    END AS null_status
FROM information_schema.columns
CROSS JOIN example_table
WHERE
    table_schema = example_schema
    AND table_name = example_table
GROUP BY column_name
ORDER BY null_fraction DESC, column_name;
