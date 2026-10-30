"""Edge-case unit tests for empty payloads and missing input files."""

from __future__ import annotations

from pathlib import Path
import pandas as pd

from validator.core import CheckStatus, DataValidator
from validator.null_checker import NullChecker
from validator.duplicate_checker import DuplicateChecker
from validator.range_checker import RangeChecker


def test_empty_dataframe_null_check_passes():
    """Empty DataFrame should cleanly pass null check with 0% null rate."""
    checker = NullChecker(default_threshold=0.05)
    df = pd.DataFrame(columns=["col_a", "col_b"])
    result = checker.check_nulls(df)
    assert result.status == CheckStatus.PASS
    assert result.metrics["total_rows"] == 0


def test_empty_dataframe_duplicate_check_passes():
    """Empty DataFrame should pass duplicate check with 0 duplicates."""
    checker = DuplicateChecker()
    df = pd.DataFrame(columns=["id", "name"])
    result = checker.check_duplicates(df, primary_key=["id"])
    assert result.status == CheckStatus.PASS
    assert result.metrics["total_rows"] == 0


def test_empty_dataframe_range_check_passes():
    """Empty DataFrame should pass range check without out-of-bound errors."""
    checker = RangeChecker()
    df = pd.DataFrame({"amount": pd.Series(dtype="float64")})
    result = checker.check_ranges(df, column_ranges={"amount": {"min": 0.0, "max": 1000.0}})
    assert result.status == CheckStatus.PASS
    assert result.metrics["total_rows"] == 0


def test_missing_csv_file_returns_error(tmp_path: Path):
    """Attempting to validate non-existent CSV file returns an ERROR check result."""
    validator = DataValidator()
    report = validator.validate_csv(tmp_path / "non_existent_file.csv")
    assert report.overall_status in (CheckStatus.ERROR, CheckStatus.FAIL)
    assert any(r.status == CheckStatus.ERROR for r in report.results)


def test_csv_parse_error_returns_error(tmp_path: Path):
    """Corrupted CSV content produces ERROR check result gracefully."""
    bad_file = tmp_path / "corrupt.csv"
    bad_file.write_bytes(b"\x00\xff\xfe\x00corrupted\x00data\xff")
    validator = DataValidator()
    report = validator.validate_csv(bad_file)
    assert report.overall_status in (CheckStatus.ERROR, CheckStatus.FAIL)


def test_header_only_csv_passes(tmp_path: Path):
    """CSV containing only header row with 0 data rows validates successfully."""
    header_file = tmp_path / "header_only.csv"
    header_file.write_text("id,name,value\n", encoding="utf-8")
    validator = DataValidator()
    report = validator.validate_csv(header_file)
    assert report.overall_status in (CheckStatus.PASS, CheckStatus.WARN)
