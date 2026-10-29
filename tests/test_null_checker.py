"""Unit tests for NullChecker module."""

import pandas as pd
import pytest

from validator.core import CheckStatus
from validator.null_checker import NullChecker


def test_null_check_passes_when_no_nulls():
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
    })
    checker = NullChecker(default_threshold=0.0)
    result = checker.check_nulls(df)
    assert result.status == CheckStatus.PASS
    assert result.metrics["null_counts"]["id"] == 0
    assert result.metrics["null_counts"]["name"] == 0


def test_null_check_passes_within_allowed_threshold():
    df = pd.DataFrame({
        "val": [1, 2, None, 4],
    })
    checker = NullChecker(default_threshold=0.30)
    result = checker.check_nulls(df)
    assert result.status == CheckStatus.PASS


def test_null_check_fails_when_threshold_exceeded():
    df = pd.DataFrame({
        "val": [1, None, None, 4],
    })
    checker = NullChecker(default_threshold=0.25)
    result = checker.check_nulls(df)
    assert result.status == CheckStatus.FAIL
    assert len(result.offending_sample) > 0


def test_null_check_fails_on_non_nullable_column():
    df = pd.DataFrame({
        "id": [1, None, 3],
        "notes": ["a", None, "c"],
    })
    checker = NullChecker(default_threshold=0.50)
    result = checker.check_nulls(df, non_nullable_cols=["id"])
    assert result.status == CheckStatus.FAIL
    assert any(s["column"] == "id" for s in result.offending_sample)


def test_null_check_empty_dataframe():
    df = pd.DataFrame({"id": [], "name": []})
    checker = NullChecker(default_threshold=0.0)
    result = checker.check_nulls(df)
    assert result.status == CheckStatus.PASS
    assert result.metrics["total_rows"] == 0
