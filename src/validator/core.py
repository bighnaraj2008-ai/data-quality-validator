"""Core Data Quality Validation Engine.

Orchestrates modular checkers across schema drift, null values,
row duplicates, and numerical boundaries into an aggregated validation report,
with robust exception handling and execution telemetry.
"""

from __future__ import annotations

from enum import Enum
import json
import logging
from pathlib import Path
import time
import traceback
from typing import Any, Dict, List, Optional, Union

import pandas as pd

logger = logging.getLogger(__name__)


class CheckStatus(str, Enum):
    """Execution status for an individual validation check."""

    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    ERROR = "ERROR"


class CheckResult:
    """Represents the outcome of a single validation check rule."""

    def __init__(
        self,
        name: str,
        status: Union[CheckStatus, str],
        message: str,
        metrics: Optional[Dict[str, Any]] = None,
        offending_sample: Optional[List[Dict[str, Any]]] = None,
        execution_time_ms: float = 0.0,
        error_trace: Optional[str] = None,
    ) -> None:
        self.name = name
        self.status = CheckStatus(status) if isinstance(status, str) else status
        self.message = message
        self.metrics = metrics or {}
        self.offending_sample = offending_sample or []
        self.execution_time_ms = execution_time_ms
        self.error_trace = error_trace

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "metrics": self.metrics,
            "offending_sample": self.offending_sample,
            "execution_time_ms": round(self.execution_time_ms, 3),
        }
        if self.error_trace:
            data["error_trace"] = self.error_trace
        return data


class BaselineSchema:
    """Represents expected column names, types, and primary key definitions."""

    def __init__(
        self,
        columns: Dict[str, str],
        primary_key: Optional[List[str]] = None,
        strict: bool = False,
    ) -> None:
        self.columns = columns
        self.primary_key = primary_key or []
        self.strict = strict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BaselineSchema:
        columns = data.get("columns", {})
        primary_key = data.get("primary_key", [])
        strict = data.get("strict", False)
        return cls(columns=columns, primary_key=primary_key, strict=strict)

    @classmethod
    def from_json_file(cls, path: Union[str, Path]) -> BaselineSchema:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Schema file not found at: {path}")
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)


class ValidationReport:
    """Aggregated summary and detail of all executed validation checks."""

    def __init__(
        self,
        dataset_path: str,
        total_rows: int,
        total_columns: int,
        results: List[CheckResult],
        duration_ms: float = 0.0,
    ) -> None:
        self.dataset_path = dataset_path
        self.total_rows = total_rows
        self.total_columns = total_columns
        self.results = results
        self.duration_ms = duration_ms

    @property
    def passed_checks(self) -> int:
        return sum(1 for r in self.results if r.status == CheckStatus.PASS)

    @property
    def failed_checks(self) -> int:
        return sum(1 for r in self.results if r.status in (CheckStatus.FAIL, CheckStatus.ERROR))

    @property
    def warning_checks(self) -> int:
        return sum(1 for r in self.results if r.status == CheckStatus.WARN)

    @property
    def overall_status(self) -> CheckStatus:
        if any(r.status in (CheckStatus.FAIL, CheckStatus.ERROR) for r in self.results):
            return CheckStatus.FAIL
        if any(r.status == CheckStatus.WARN for r in self.results):
            return CheckStatus.WARN
        return CheckStatus.PASS

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataset_path": self.dataset_path,
            "total_rows": self.total_rows,
            "total_columns": self.total_columns,
            "overall_status": self.overall_status.value,
            "checks_run": len(self.results),
            "passed": self.passed_checks,
            "failed": self.failed_checks,
            "warnings": self.warning_checks,
            "duration_ms": round(self.duration_ms, 2),
            "results": [r.to_dict() for r in self.results],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


class DataValidator:
    """Core data quality inspection runner class with robust error isolation."""

    def __init__(
        self,
        schema: Optional[BaselineSchema] = None,
        null_threshold: float = 0.0,
        strict_schema: bool = False,
    ) -> None:
        self.schema = schema
        self.null_threshold = null_threshold
        self.strict_schema = strict_schema

    def _execute_check(self, check_name: str, check_fn) -> CheckResult:
        """Safely execute a check function with time measurement and exception handling."""
        start = time.perf_counter()
        try:
            result = check_fn()
            result.execution_time_ms = (time.perf_counter() - start) * 1000.0
            return result
        except Exception as exc:
            elapsed = (time.perf_counter() - start) * 1000.0
            logger.exception("Validation check '%s' raised unexpected exception: %s", check_name, exc)
            return CheckResult(
                name=check_name,
                status=CheckStatus.ERROR,
                message=f"Check failed due to unexpected error: {exc}",
                execution_time_ms=elapsed,
                error_trace=traceback.format_exc(),
            )

    def validate_df(
        self,
        df: pd.DataFrame,
        dataset_path: str = "in_memory",
        column_ranges: Optional[Dict[str, Dict[str, float]]] = None,
        non_nullable_cols: Optional[List[str]] = None,
    ) -> ValidationReport:
        from validator.drift_detector import DriftDetector
        from validator.null_checker import NullChecker
        from validator.duplicate_checker import DuplicateChecker
        from validator.range_checker import RangeChecker

        start_time = time.perf_counter()
        results: List[CheckResult] = []

        # 1. Schema Drift Check
        if self.schema:
            drift_detector = DriftDetector(strict=self.strict_schema or self.schema.strict)
            results.append(
                self._execute_check(
                    "schema_drift",
                    lambda: drift_detector.check_drift(df, self.schema),
                )
            )

        # 2. Null Value Check
        null_checker = NullChecker(default_threshold=self.null_threshold)
        results.append(
            self._execute_check(
                "null_values",
                lambda: null_checker.check_nulls(df, non_nullable_cols=non_nullable_cols),
            )
        )

        # 3. Duplicate Row / Key Check
        pk_cols = self.schema.primary_key if self.schema else None
        duplicate_checker = DuplicateChecker()
        results.append(
            self._execute_check(
                "duplicate_rows",
                lambda: duplicate_checker.check_duplicates(df, primary_key=pk_cols),
            )
        )

        # 4. Numerical Range Check
        if column_ranges:
            range_checker = RangeChecker()
            results.append(
                self._execute_check(
                    "range_boundaries",
                    lambda: range_checker.check_ranges(df, column_ranges),
                )
            )

        duration_ms = (time.perf_counter() - start_time) * 1000.0
        return ValidationReport(
            dataset_path=dataset_path,
            total_rows=len(df),
            total_columns=len(df.columns),
            results=results,
            duration_ms=duration_ms,
        )

    def validate_csv(
        self,
        csv_path: Union[str, Path],
        column_ranges: Optional[Dict[str, Dict[str, float]]] = None,
        non_nullable_cols: Optional[List[str]] = None,
    ) -> ValidationReport:
        path = Path(csv_path)
        if not path.exists():
            return ValidationReport(
                dataset_path=str(csv_path),
                total_rows=0,
                total_columns=0,
                results=[
                    CheckResult(
                        name="file_read",
                        status=CheckStatus.ERROR,
                        message=f"File not found: {csv_path}",
                    )
                ],
                duration_ms=0.0,
            )
        try:
            df = pd.read_csv(path)
            return self.validate_df(
                df,
                dataset_path=str(csv_path),
                column_ranges=column_ranges,
                non_nullable_cols=non_nullable_cols,
            )
        except Exception as exc:
            return ValidationReport(
                dataset_path=str(csv_path),
                total_rows=0,
                total_columns=0,
                results=[
                    CheckResult(
                        name="csv_parse",
                        status=CheckStatus.ERROR,
                        message=f"Failed to parse CSV file: {exc}",
                        error_trace=traceback.format_exc(),
                    )
                ],
                duration_ms=0.0,
            )
