"""Unit tests for DriftDetector module."""

import pandas as pd

from validator.core import BaselineSchema, CheckStatus
from validator.drift_detector import DriftDetector


def test_schema_drift_passes_when_matching():
    schema = BaselineSchema(
        columns={"id": "integer", "name": "string"},
        primary_key=["id"],
    )
    df = pd.DataFrame({"id": [1, 2], "name": ["a", "b"]})
    detector = DriftDetector()
    result = detector.check_drift(df, schema)
    assert result.status == CheckStatus.PASS
    assert len(result.metrics["missing"]) == 0
    assert len(result.metrics["added"]) == 0


def test_missing_column_triggers_failure():
    schema = BaselineSchema(columns={"id": "integer", "email": "string"})
    df = pd.DataFrame({"id": [1, 2]})
    detector = DriftDetector()
    result = detector.check_drift(df, schema)
    assert result.status == CheckStatus.FAIL
    assert "email" in result.metrics["missing"]


def test_added_column_triggers_warn_in_lenient_mode():
    schema = BaselineSchema(columns={"id": "integer"}, strict=False)
    df = pd.DataFrame({"id": [1, 2], "extra": ["a", "b"]})
    detector = DriftDetector(strict=False)
    result = detector.check_drift(df, schema)
    assert result.status == CheckStatus.WARN
    assert "extra" in result.metrics["added"]


def test_added_column_triggers_fail_in_strict_mode():
    schema = BaselineSchema(columns={"id": "integer"}, strict=True)
    df = pd.DataFrame({"id": [1, 2], "extra": ["a", "b"]})
    detector = DriftDetector(strict=True)
    result = detector.check_drift(df, schema)
    assert result.status == CheckStatus.FAIL
    assert "extra" in result.metrics["added"]


def test_type_mismatch_triggers_failure():
    schema = BaselineSchema(columns={"age": "integer"})
    df = pd.DataFrame({"age": ["twenty", "thirty"]})
    detector = DriftDetector()
    result = detector.check_drift(df, schema)
    assert result.status == CheckStatus.FAIL
    assert len(result.metrics["type_mismatches"]) > 0


def test_no_baseline_schema_skips():
    df = pd.DataFrame({"a": [1]})
    detector = DriftDetector()
    result = detector.check_drift(df, None)
    assert result.status == CheckStatus.PASS
