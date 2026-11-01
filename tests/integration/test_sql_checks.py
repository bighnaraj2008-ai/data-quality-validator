"""Integration test for pure SQL check templates against an in-memory SQL database."""

from pathlib import Path
import sqlite3

SQL_CHECKS_DIR = Path(__file__).resolve().parent.parent.parent / "sql" / "checks"


def _read_sql(filename: str) -> str:
    path = SQL_CHECKS_DIR / filename
    assert path.exists(), f"SQL check template {filename} does not exist"
    return path.read_text(encoding="utf-8")


def test_duplicate_keys_sql_check_template():
    """Verify duplicate_keys.sql detects duplicate primary keys."""
    sql = _read_sql("duplicate_keys.sql")

    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE example_table (id INT, name TEXT);")
    conn.executemany(
        "INSERT INTO example_table VALUES (?, ?);",
        [
            (1, "Alice"),
            (2, "Bob"),
            (2, "Bob Duplicate"),
            (3, "Charlie"),
            (3, "Charlie Duplicate"),
        ],
    )

    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    assert len(rows) == 2
    keys = {r[0]: r[1] for r in rows}
    assert keys[2] == 2
    assert keys[3] == 2
    conn.close()


def test_row_count_anomaly_sql_check_template():
    """Verify row_count_anomaly.sql computes table row counts."""
    sql = _read_sql("row_count_anomaly.sql")

    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE example_table (order_id INT);")
    conn.executemany("INSERT INTO example_table VALUES (?);", [(i,) for i in range(10)])

    cur = conn.cursor()
    cur.execute(sql)
    row = cur.fetchone()
    assert row is not None
    assert row[1] == 10
    conn.close()
