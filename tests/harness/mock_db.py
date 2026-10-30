"""Mock Database Connection and Engine Fixture Handler.

Provides in-memory simulated database connections, cursors, and query execution
for validating SQL check templates without requiring a live external database.
"""

from __future__ import annotations

import sqlite3
from typing import Any, Dict, List, Optional, Tuple, Union
import pandas as pd


class MockCursor:
    """Simulated database cursor executing queries against an in-memory database."""

    def __init__(self, sqlite_cursor: sqlite3.Cursor) -> None:
        self._cursor = sqlite_cursor

    def execute(self, query: str, parameters: Optional[Union[Dict[str, Any], Tuple[Any, ...]]] = None) -> MockCursor:
        if parameters:
            self._cursor.execute(query, parameters)
        else:
            self._cursor.execute(query)
        return self

    def fetchall(self) -> List[Tuple[Any, ...]]:
        return self._cursor.fetchall()

    def fetchone(self) -> Optional[Tuple[Any, ...]]:
        return self._cursor.fetchone()

    @property
    def description(self):
        return self._cursor.description


class MockConnection:
    """Simulated database connection supporting transaction context and queries."""

    def __init__(self, database: str = ":memory:") -> None:
        self._conn = sqlite3.connect(database)
        self._conn.row_factory = sqlite3.Row

    def cursor(self) -> MockCursor:
        return MockCursor(self._conn.cursor())

    def execute(self, query: str, parameters: Optional[Union[Dict[str, Any], Tuple[Any, ...]]] = None) -> MockCursor:
        cur = self.cursor()
        cur.execute(query, parameters)
        return cur

    def register_dataframe(self, table_name: str, df: pd.DataFrame) -> None:
        df.to_sql(table_name, self._conn, if_exists="replace", index=False)

    def commit(self) -> None:
        self._conn.commit()

    def rollback(self) -> None:
        self._conn.rollback()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> MockConnection:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()


def create_mock_engine(database: str = ":memory:") -> MockConnection:
    """Factory creating a configured MockConnection instance."""
    return MockConnection(database=database)
