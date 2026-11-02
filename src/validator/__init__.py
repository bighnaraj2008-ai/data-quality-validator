"""Data Quality Validator public package interface (v1.0.0).

Exposes the core orchestration engine, schema definitions, status enums,
and individual rule-checking modules:

- ``DataValidator``: Unified pipeline orchestrator with error isolation.
- ``ValidationReport`` / ``CheckResult`` / ``CheckStatus``: Execution telemetry.
- ``BaselineSchema``: Reference column-type and primary-key definition.
- ``NullChecker``, ``DuplicateChecker``, ``DriftDetector``, ``RangeChecker``: Modular rules.
"""

from validator.core import BaselineSchema, CheckResult, CheckStatus, DataValidator, ValidationReport
from validator.drift_detector import DriftDetector
from validator.duplicate_checker import DuplicateChecker
from validator.null_checker import NullChecker
from validator.range_checker import RangeChecker

__version__ = "1.0.0"

__all__ = [
    "DataValidator",
    "ValidationReport",
    "CheckResult",
    "CheckStatus",
    "BaselineSchema",
    "NullChecker",
    "DuplicateChecker",
    "DriftDetector",
    "RangeChecker",
]
