"""Integration tests for end-to-end data quality validation pipeline runs."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from validator.core import BaselineSchema, CheckStatus, DataValidator  # noqa: E402
from tests.harness.assertions import assert_check_status, assert_no_errors, calculate_quality_score  # noqa: E402

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


def test_clean_dataset_passes_full_pipeline():
    """Clean baseline dataset passes schema, null, duplicate, and range checks."""
    schema = BaselineSchema(
        columns={
            "id": "int64",
            "name": "object",
            "email": "object",
            "age": "int64",
            "income": "float64",
            "created_at": "object",
        },
        primary_key=["id"],
    )
    validator = DataValidator(schema=schema, null_threshold=0.0)
    report = validator.validate_csv(
        FIXTURES_DIR / "clean_dataset.csv",
        column_ranges={"age": {"min": 0, "max": 120}, "income": {"min": 0.0}},
        non_nullable_cols=["id", "email"],
    )

    assert_no_errors(report)
    assert report.overall_status == CheckStatus.PASS
    score = calculate_quality_score(report)
    assert score == 100.0


def test_drifted_dataset_fails_expected_checks():
    """Drifted dataset triggers schema drift and duplicate violations."""
    schema = BaselineSchema(
        columns={
            "id": "int64",
            "name": "object",
            "email": "object",
            "age": "int64",
            "income": "float64",
            "created_at": "object",
        },
        primary_key=["id"],
    )
    validator = DataValidator(schema=schema)
    report = validator.validate_csv(
        FIXTURES_DIR / "drifted_dataset.csv",
    )

    assert report.overall_status == CheckStatus.FAIL
    assert_check_status(report, "schema_drift", CheckStatus.FAIL)
    assert_check_status(report, "duplicate_rows", CheckStatus.FAIL)


def test_null_anomaly_detects_spike():
    """JSON fixture with null value spike triggers null check failure."""
    json_path = FIXTURES_DIR / "null_anomaly.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)

    validator = DataValidator(null_threshold=0.20)
    report = validator.validate_df(df, non_nullable_cols=["email"])
    assert report.overall_status == CheckStatus.FAIL
    assert_check_status(report, "null_values", CheckStatus.FAIL)


def test_duplicate_keys_fixture_fails_uniqueness():
    """Duplicate keys CSV fixture triggers primary key collision failure."""
    schema = BaselineSchema(
        columns={"id": "int64", "name": "object", "email": "object", "department": "object", "salary": "float64"},
        primary_key=["id"],
    )
    validator = DataValidator(schema=schema)
    report = validator.validate_csv(FIXTURES_DIR / "duplicate_keys.csv")
    assert report.overall_status == CheckStatus.FAIL
    assert_check_status(report, "duplicate_rows", CheckStatus.FAIL)


def test_pipeline_telemetry_and_json_export():
    """Validation report correctly serializes to JSON with all telemetry metrics."""
    validator = DataValidator()
    report = validator.validate_csv(FIXTURES_DIR / "clean_dataset.csv")
    json_str = report.to_json()
    parsed = json.loads(json_str)

    assert "results" in parsed
    assert "overall_status" in parsed
    assert parsed["checks_run"] >= 2
