#!/usr/bin/env python3
"""Repository and SQL warehouse template health validation utility."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SQL_DIR = REPO_ROOT / "sql" / "checks"


def validate_sql_templates() -> int:
    """Dry-run pure SQL check templates against an in-memory SQLite table."""
    required_sql = [
        "null_distribution.sql",
        "duplicate_keys.sql",
        "row_count_anomaly.sql",
        "schema_drift.sql",
    ]
    missing = [name for name in required_sql if not (SQL_DIR / name).exists()]
    if missing:
        print(f"Missing SQL check templates: {missing}", file=sys.stderr)
        return 1

    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE example_table (id INT, order_id INT, name TEXT);")
    conn.executemany(
        "INSERT INTO example_table VALUES (?, ?, ?);",
        [(1, 100, "alpha"), (2, 101, "beta"), (2, 102, "beta-dup")],
    )

    for sql_name in ("duplicate_keys.sql", "row_count_anomaly.sql"):
        sql = (SQL_DIR / sql_name).read_text(encoding="utf-8")
        rows = conn.execute(sql).fetchall()
        print(f"[OK] executed {sql_name} -> {len(rows)} row(s)")

    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(validate_sql_templates())
