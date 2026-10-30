"""Edge-case unit tests for silent schema drift and evolution."""

from __future__ import annotations

import pandas as pd

from validator.core import BaselineSchema, CheckStatus
from validator.drift_detector import DriftDetector


def test_added_column_silent_drift_warns_in_lenient_mode():
    """Added columns trigger WARN when strict=False."""
    schema = BaselineSchema(columns={"id": "int64", "name": "object"}, strict=False)
    df = pd.DataFrame({"id": [1, 2], "name": ["a", "b"], "unexpected_feature": [10, 20]})
    detector = DriftDetector(strict=False)
    result = detector.check_drift(df, schema)
    assert result.status == CheckStatus.WARN
    assert "unexpected_feature" in result.metrics["added"]


def test_added_column_silent_drift_fails_in_strict_mode():
    """Added columns trigger FAIL when strict=True."""
    schema = BaselineSchema(columns={"id": "int64", "name": "object"}, strict=True)
    df = pd.DataFrame({"id": [1, 2], "name": ["a", "b"], "unexpected_feature": [10, 20]})
    detector = DriftDetector(strict=True)
    result = detector.check_drift(df, schema)
    assert result.status == CheckStatus.FAIL
    assert "unexpected_feature" in result.metrics["added"]


def test_dropped_column_always_fails_regardless_of_mode():
    """Missing schema columns trigger FAIL in both lenient and strict modes."""
    schema = BaselineSchema(columns={"id": "int64", "name": "object", "required_token": "object"})
    df = pd.DataFrame({"id": [1, 2], "name": ["a", "b"]})
    for strict in (True, False):
        detector = DriftDetector(strict=strict)
        result = detector.check_drift(df, schema)
        assert result.status == CheckStatus.FAIL
        assert "required_token" in result.metrics["missing"]


def test_no_baseline_schema_skips_drift_check():
    """When baseline schema is None, drift check reports SKIPPED / PASS."""
    detector = DriftDetector()
    df = pd.DataFrame({"col_x": [1, 2, 3]})
    result = detector.check_drift(df, schema=None)
    assert result.status in (CheckStatus.PASS, CheckStatus.WARN)


def test_column_order_change_does_not_trigger_drift():
    """Permuted column ordering with identical names and types passes."""
    schema = BaselineSchema(columns={"id": "int64", "alpha": "object", "beta": "float64"})
    df = pd.DataFrame({"beta": [1.5, 2.5], "id": [1, 2], "alpha": ["x", "y"]})
    detector = DriftDetector()
    result = detector.check_drift(df, schema)
    assert result.status == CheckStatus.PASS
