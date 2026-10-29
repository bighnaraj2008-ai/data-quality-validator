"""Data Quality Validator package.

Modular architecture providing data validation, schema drift detection,
null checks, row duplication analysis, and numerical range verification.
"""

from __future__ import annotations

from validator.core import (
    CheckResult,
    CheckStatus,
    DataValidator,
    ValidationReport,
    BaselineSchema,
)
from validator.null_checker import NullChecker
from validator.duplicate_checker import DuplicateChecker
from validator.drift_detector import DriftDetector
from validator.range_checker import RangeChecker

__version__ = "0.1.0"

__all__ = [
    "DataValidator",
    "CheckResult",
    "CheckStatus",
    "ValidationReport",
    "BaselineSchema",
    "NullChecker",
    "DuplicateChecker",
    "DriftDetector",
    "RangeChecker",
]
