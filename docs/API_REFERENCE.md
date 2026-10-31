# Python API Reference Manual

This document provides complete class and method signatures for the core
modules of `data-quality-validator`.

---

## 1. Core Validation Engine (`src/validator/core.py`)

### `CheckStatus` (Enum)

Represents the terminal state of an individual quality check:

```python
class CheckStatus(Enum):
    PASS = "PASS"    # Check passed all threshold constraints
    WARN = "WARN"    # Threshold warning (non-fatal, pipeline continues)
    FAIL = "FAIL"    # Threshold violation (fatal, overall status FAIL)
    ERROR = "ERROR"  # Unhandled exception, missing data, or bad config
```

---

### `CheckResult` (Dataclass)

Data structure encapsulating the result of a single check evaluation:

```python
@dataclass
class CheckResult:
    check_name: str
    status: CheckStatus
    message: str
    metrics: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
```

---

### `ValidationReport`

Aggregates multiple `CheckResult` instances and calculates overall pipeline status:

```python
class ValidationReport:
    def __init__(self, dataset_name: str = "dataset") -> None:
        ...

    @property
    def passed_checks(self) -> list[CheckResult]:
        """Returns all checks that succeeded."""

    @property
    def failed_checks(self) -> list[CheckResult]:
        """Returns all checks that failed (FAIL status)."""

    @property
    def warning_checks(self) -> list[CheckResult]:
        """Returns all checks that produced warnings (WARN status)."""

    @property
    def overall_status(self) -> CheckStatus:
        """Calculates overall status: FAIL if any fail, else WARN if any warn, else PASS."""

    def add_result(self, result: CheckResult) -> None:
        """Append a CheckResult to the report."""

    def to_dict(self) -> dict[str, Any]:
        """Serialize report to a Python dictionary."""

    def to_json(self, indent: int = 2) -> str:
        """Serialize report to formatted JSON string."""
```

---

### `DataValidator`

Top-level facade that coordinates dataframe ingestion, rule dispatch, and report generation:

```python
class DataValidator:
    def __init__(self, config: Optional[dict[str, Any]] = None) -> None:
        """Initialize validator with optional configuration dictionary."""

    def validate(self, df: pd.DataFrame, dataset_name: str = "dataset") -> ValidationReport:
        """Execute configured checks against input dataframe."""
```
