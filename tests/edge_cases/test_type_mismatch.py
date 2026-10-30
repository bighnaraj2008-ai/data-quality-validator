"""Edge-case unit tests for severe column type mismatch scenarios."""

from __future__ import annotations

import pandas as pd

from validator.core import BaselineSchema, CheckStatus
from validator.drift_detector import DriftDetector
from validator.range_checker import RangeChecker


def test_severe_type_mismatch_integer_column_holds_strings():
    """Verify that an integer column holding arbitrary strings is flagged as schema drift."""
    schema = BaselineSchema(columns={"id": "int64", "age": "int64", "name": "object"})
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "age": ["invalid_str", "another_bad_val", "not_a_num"],
        "name": ["Alice", "Bob", "Charlie"],
    })
    detector = DriftDetector()
    result = detector.check_drift(df, schema)
    assert result.status == CheckStatus.FAIL
    assert len(result.metrics.get("type_mismatches", [])) > 0


def test_mixed_type_column_shifts_to_string_category():
    """Verify handling of columns with string values when float was expected."""
    schema = BaselineSchema(columns={"score": "float64"})
    df = pd.DataFrame({"score": ["bad_val", "corrupted", "45.2"]})
    detector = DriftDetector()
    result = detector.check_drift(df, schema)
    assert result.status == CheckStatus.FAIL
    assert len(result.metrics.get("type_mismatches", [])) > 0


def test_range_checker_handles_non_numeric_column_without_crash():
    """Verify that RangeChecker handles non-numeric column gracefully."""
    checker = RangeChecker()
    df = pd.DataFrame({"notes": ["entry_a", "entry_b", "entry_c"]})
    result = checker.check_ranges(df, column_ranges={"notes": {"min": 0, "max": 100}})
    assert result.status in (CheckStatus.PASS, CheckStatus.FAIL)
    assert result.name == "range_boundaries"


def test_type_mismatch_boolean_vs_integer():
    """Verify boolean dtype when integer was expected."""
    schema = BaselineSchema(columns={"is_active": "int64"})
    df = pd.DataFrame({"is_active": [True, False, True]})
    detector = DriftDetector()
    result = detector.check_drift(df, schema)
    assert result.status == CheckStatus.FAIL
    assert len(result.metrics.get("type_mismatches", [])) > 0
