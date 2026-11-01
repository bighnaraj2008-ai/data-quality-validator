"""Unit tests for DuplicateChecker module."""

import pandas as pd

from validator.core import CheckStatus
from validator.duplicate_checker import DuplicateChecker


def test_duplicate_check_passes_with_distinct_rows():
    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "email": ["a@x.com", "b@x.com", "c@x.com"],
        }
    )
    checker = DuplicateChecker()
    result = checker.check_duplicates(df)
    assert result.status == CheckStatus.PASS
    assert result.metrics["duplicate_rows"] == 0


def test_exact_row_duplicates_detected():
    df = pd.DataFrame(
        {
            "id": [1, 2, 2],
            "email": ["a@x.com", "b@x.com", "b@x.com"],
        }
    )
    checker = DuplicateChecker()
    result = checker.check_duplicates(df)
    assert result.status == CheckStatus.FAIL
    assert result.metrics["duplicate_rows"] == 1
    assert len(result.offending_sample) > 0


def test_single_column_primary_key_duplicates():
    df = pd.DataFrame(
        {
            "id": [1, 2, 2],
            "email": ["a@x.com", "b@x.com", "different@x.com"],
        }
    )
    checker = DuplicateChecker()
    result = checker.check_duplicates(df, primary_key=["id"])
    assert result.status == CheckStatus.FAIL
    assert result.metrics["duplicate_keys"] == 1


def test_composite_primary_key_uniqueness():
    df = pd.DataFrame(
        {
            "tenant_id": [1, 1, 2],
            "user_id": [10, 20, 10],
            "val": ["x", "y", "z"],
        }
    )
    checker = DuplicateChecker()
    result = checker.check_duplicates(df, primary_key=["tenant_id", "user_id"])
    assert result.status == CheckStatus.PASS


def test_composite_primary_key_collision():
    df = pd.DataFrame(
        {
            "tenant_id": [1, 1, 2],
            "user_id": [10, 10, 10],
        }
    )
    checker = DuplicateChecker()
    result = checker.check_duplicates(df, primary_key=["tenant_id", "user_id"])
    assert result.status == CheckStatus.FAIL


def test_missing_primary_key_column():
    df = pd.DataFrame({"id": [1, 2]})
    checker = DuplicateChecker()
    result = checker.check_duplicates(df, primary_key=["missing_col"])
    assert result.status == CheckStatus.FAIL
    assert "not found" in result.message
