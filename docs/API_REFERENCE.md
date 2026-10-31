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

---

## 2. Check Modules

### `NullChecker` (`src/validator/null_checker.py`)

Inspects null value distribution and enforces completeness rules.

```python
class NullChecker:
    @staticmethod
    def check_nulls(
        df: pd.DataFrame,
        non_nullable_cols: Optional[list[str]] = None,
        column_thresholds: Optional[dict[str, float]] = None,
        default_threshold: float = 0.0,
    ) -> CheckResult:
        """
        Validates null frequencies across dataframe columns.

        Args:
            df: Target pandas DataFrame.
            non_nullable_cols: Columns that must have zero null values.
            column_thresholds: Dict mapping column names to max allowed null ratios [0.0, 1.0].
            default_threshold: Fallback max allowed null ratio.

        Returns:
            CheckResult with status PASS, WARN, or FAIL.
        """
```

---

### `DuplicateChecker` (`src/validator/duplicate_checker.py`)

Identifies full-row duplicates and candidate primary / composite key collisions.

```python
class DuplicateChecker:
    @staticmethod
    def check_duplicates(
        df: pd.DataFrame,
        primary_key: Optional[Union[str, list[str]]] = None,
        allow_duplicates: bool = false,
    ) -> CheckResult:
        """
        Validates row uniqueness and primary key integrity.

        Args:
            df: Target pandas DataFrame.
            primary_key: Column name or list of column names acting as primary key.
            allow_duplicates: If True, duplicate rows emit WARN instead of FAIL.

        Returns:
            CheckResult with count of duplicates and offending keys.
        """
```

---

### `DriftDetector` (`src/validator/drift_detector.py`)

Monitors incoming dataset columns and types against a reference baseline schema.

```python
class DriftDetector:
    @staticmethod
    def detect_drift(
        df: pd.DataFrame,
        baseline_schema: Optional[dict[str, str]] = None,
        allow_unexpected_columns: bool = False,
    ) -> CheckResult:
        """
        Detects schema evolution, column additions, deletions, and type shifts.

        Args:
            df: Target pandas DataFrame.
            baseline_schema: Dict mapping expected column names to expected type strings.
            allow_unexpected_columns: If True, extra unmapped columns yield WARN instead of FAIL.

        Returns:
            CheckResult detailing missing, added, and mismatched columns.
        """
```

---

### `RangeChecker` (`src/validator/range_checker.py`)

Validates numerical columns against upper and lower bounds.

```python
class RangeChecker:
    @staticmethod
    def check_ranges(
        df: pd.DataFrame,
        column_ranges: Optional[dict[str, dict[str, float]]] = None,
    ) -> CheckResult:
        """
        Validates minimum and maximum value constraints.

        Args:
            df: Target pandas DataFrame.
            column_ranges: Dict mapping column names to {'min': float, 'max': float}.

        Returns:
            CheckResult indicating boundary compliance.
        """
```

---

## 3. Configuration Subsystem (`src/config/loader.py`)

### `ConfigLoader`

Parses declarative YAML configurations and applies runtime environment variable overrides.

```python
class ConfigLoader:
    @staticmethod
    def load(config_path: Optional[str] = None) -> dict[str, Any]:
        """
        Loads validation configuration from YAML file and merges environment overrides.

        Args:
            config_path: Optional path to YAML configuration file. If omitted,
                         loads 'src/config/validator_config.yaml'.

        Returns:
            Validated configuration dictionary.

        Raises:
            FileNotFoundError: If the specified config file does not exist.
            ValueError: If threshold or parameter values are outside valid ranges.
        """

    @staticmethod
    def _apply_env_overrides(config: dict[str, Any]) -> dict[str, Any]:
        """
        Inspects os.environ for 'DQ_*' variables and merges them into the config tree.
        """
```

### Exception Hierarchy

- `DataQualityError`: Base class for validator exceptions.
- `ConfigurationError`: Raised when YAML structure or parameter bounds are invalid.
- `CheckExecutionError`: Raised when a check cannot execute due to missing columns or unreadable data.
