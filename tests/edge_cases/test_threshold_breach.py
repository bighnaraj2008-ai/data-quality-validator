"""Edge-case unit tests for threshold breach boundaries."""

from __future__ import annotations

import pandas as pd

from validator.core import CheckStatus
from validator.null_checker import NullChecker
from validator.range_checker import RangeChecker


def test_null_rate_exactly_at_threshold_passes():
    """Null rate exactly equal to configured threshold passes."""
    checker = NullChecker(default_threshold=0.20)
    df = pd.DataFrame({"val": [1, 2, None, 4, 5, 6, None, 8, 9, 10]})
    result = checker.check_nulls(df)
    assert result.status == CheckStatus.PASS


def test_null_rate_just_above_threshold_fails():
    """Null rate exceeding configured threshold triggers failure."""
    checker = NullChecker(default_threshold=0.20)
    df = pd.DataFrame({"val": [1, 2, None, 4, None, 6, None, 8, 9, 10]})
    result = checker.check_nulls(df)
    assert result.status == CheckStatus.FAIL


def test_non_nullable_column_single_null_fails():
    """Single null in non-nullable column triggers FAIL even if column threshold is high."""
    checker = NullChecker(default_threshold=0.50)
    df = pd.DataFrame({"user_id": [1, 2, None, 4, 5]})
    result = checker.check_nulls(df, non_nullable_cols=["user_id"])
    assert result.status == CheckStatus.FAIL
    assert len(result.offending_sample) > 0


def test_range_value_at_boundary_passes():
    """Values exactly matching min or max range bounds pass."""
    checker = RangeChecker()
    df = pd.DataFrame({"score": [0.0, 50.0, 100.0]})
    result = checker.check_ranges(df, column_ranges={"score": {"min": 0.0, "max": 100.0}})
    assert result.status == CheckStatus.PASS


def test_range_value_outside_boundary_fails():
    """Values strictly exceeding min or max bounds trigger failure."""
    checker = RangeChecker()
    df = pd.DataFrame({"score": [-0.1, 50.0, 100.1]})
    result = checker.check_ranges(df, column_ranges={"score": {"min": 0.0, "max": 100.0}})
    assert result.status == CheckStatus.FAIL
    assert len(result.offending_sample) > 0


def test_range_column_missing_from_dataset_is_violation():
    """Checking range on non-existent column produces failure."""
    checker = RangeChecker()
    df = pd.DataFrame({"unrelated": [1, 2, 3]})
    result = checker.check_ranges(df, column_ranges={"non_existent": {"min": 0, "max": 10}})
    assert result.status == CheckStatus.FAIL
