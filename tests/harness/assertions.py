"""Custom Quality Score Assertion Helpers for Test Suites.

Provides specialized assertion utilities to validate quality scores,
rule check statuses, and failure telemetry in test cases.
"""

from __future__ import annotations

from typing import Any, Optional, Union
from validator.core import CheckResult, CheckStatus, ValidationReport


def calculate_quality_score(report: ValidationReport) -> float:
    """Compute normalized data quality score (0.0 to 100.0) from report."""
    total = len(report.results)
    if total == 0:
        return 100.0
    passed = report.passed_checks
    warns = report.warning_checks
    score = ((passed * 1.0) + (warns * 0.5)) / total * 100.0
    return round(score, 2)


def assert_quality_score(report: ValidationReport, min_score: float) -> None:
    """Assert that the overall quality score meets or exceeds minimum threshold."""
    actual_score = calculate_quality_score(report)
    assert actual_score >= min_score, (
        f"Quality score {actual_score:.2f}% below threshold {min_score:.2f}%. "
        f"Passed: {report.passed_checks}, Failed: {report.failed_checks}, Warnings: {report.warning_checks}."
    )


def assert_check_status(
    report: ValidationReport,
    check_name: str,
    expected_status: Union[CheckStatus, str],
) -> None:
    """Assert that a specific check rule produced the expected status with detailed context."""
    expected = CheckStatus(expected_status) if isinstance(expected_status, str) else expected_status
    match = next((r for r in report.results if r.name == check_name), None)
    assert (
        match is not None
    ), f"Check rule '{check_name}' was not executed. Executed checks: {[r.name for r in report.results]}"
    assert match.status == expected, (
        f"Check '{check_name}' status mismatch: expected {expected.value}, got {match.status.value}. "
        f"Diagnostic message: {match.message}. Metrics: {match.metrics}"
    )


def assert_no_errors(report: ValidationReport) -> None:
    """Assert that no execution errors occurred during validation."""
    error_results = [r for r in report.results if r.status == CheckStatus.ERROR]
    assert len(error_results) == 0, (
        f"Validation produced {len(error_results)} execution errors: "
        f"{[f'{r.name}: {r.message}' for r in error_results]}"
    )


def assert_metrics_contain(
    check_result: CheckResult,
    key: str,
    expected_val: Optional[Any] = None,
) -> None:
    """Assert that check metrics contain the given key and optional value."""
    assert key in check_result.metrics, f"Key '{key}' not found in check metrics: {check_result.metrics}"
    if expected_val is not None:
        assert (
            check_result.metrics[key] == expected_val
        ), f"Metric '{key}' expected {expected_val}, got {check_result.metrics[key]}"


def assert_throughput_above(throughput_rps: float, min_rps: float = 1_000.0) -> None:
    """Assert that benchmark throughput exceeds the minimum rows-per-second floor."""
    msg = f"[THROUGHPUT FAILURE] Observed={throughput_rps:,.2f} rows/s | Required>={min_rps:,.2f} rows/s"
    assert throughput_rps >= min_rps, msg
