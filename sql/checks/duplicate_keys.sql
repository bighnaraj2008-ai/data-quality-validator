-- ============================================================================
-- SQL CHECK: duplicate_keys
-- Purpose: Identify duplicate primary key or composite key collisions
--          and surface offending keys with duplicate occurrence counts.
--
-- Dialect: ANSI SQL / PostgreSQL / SQLite
-- Note: id / example_table / 10 are runtime substitution values.
-- ============================================================================

SELECT
    id AS primary_key_value,
    COUNT(*) AS occurrence_count
FROM example_table
GROUP BY id
HAVING COUNT(*) > 1
ORDER BY occurrence_count DESC
LIMIT 10;
