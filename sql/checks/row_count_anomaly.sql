-- ============================================================================
-- SQL CHECK: row_count_anomaly
-- Purpose: Verify dataset record volume falls within expected minimum and
--          maximum count thresholds to detect empty tables or dropped partitions.
--
-- Dialect: ANSI SQL / PostgreSQL / SQLite
-- Note: example_table / 0 / 1000000 are runtime substitution values.
-- ============================================================================

SELECT
    'example_table' AS table_name,
    COUNT(*) AS actual_row_count,
    0 AS min_expected_rows,
    1000000 AS max_expected_rows,
    CASE
        WHEN COUNT(*) < 0 THEN 'volume_too_low'
        WHEN 1000000 IS NOT NULL AND COUNT(*) > 1000000 THEN 'volume_too_high'
        ELSE 'volume_normal'
    END AS volume_status
FROM example_table;
