-- ============================================================================
-- SQL CHECK: row_count_anomaly
-- Purpose: Verify dataset record volume falls within expected minimum and
--          maximum count thresholds to detect empty tables or dropped partitions.
--
-- Dialect: ANSI SQL / PostgreSQL / SQLite
-- ============================================================================

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
