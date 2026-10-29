-- ============================================================================
-- SQL CHECK: duplicate_keys
-- Purpose: Identify duplicate primary key or composite key collisions
--          and surface offending keys with duplicate occurrence counts.
--
-- Dialect: ANSI SQL / PostgreSQL / SQLite
-- ============================================================================

SELECT
    :pk_column AS primary_key_value,
    COUNT(*) AS occurrence_count
FROM :table_name
GROUP BY :pk_column
HAVING COUNT(*) > 1
ORDER BY occurrence_count DESC
LIMIT :sample_limit;
