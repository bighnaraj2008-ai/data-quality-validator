# Guidelines for Contributing Custom Validation Rules

We welcome contributions to `data-quality-validator`! This guide describes how to
develop, test, and submit new validation modules and check templates.

---

## 1. Architecture of a Validator Module

All Python checkers should be placed under `src/validator/` and adhere to these
principles:

1. **Stateless execution:** Checkers should operate as pure functions or classes
   with static methods.
2. **Explicit types:** Annotate all parameters and return types (`CheckResult`).
3. **No side effects:** Do not mutate input dataframes in place.
4. **Resilient error handling:** Catch domain exceptions and return `CheckStatus.ERROR`
   instead of crashing the caller.

---

## 2. Implementing a Custom Check Class

Here is a template for a custom regex pattern checker:

```python
# src/validator/pattern_checker.py
import re
import pandas as pd
from typing import Optional
from src.validator.core import CheckResult, CheckStatus

class PatternChecker:
    @staticmethod
    def check_regex(
        df: pd.DataFrame,
        column: str,
        pattern: str,
        max_failure_rate: float = 0.0,
    ) -> CheckResult:
        if column not in df.columns:
            return CheckResult(
                check_name="pattern_match",
                status=CheckStatus.ERROR,
                message=f"Target column '{column}' not found in dataframe.",
            )

        series = df[column].dropna().astype(str)
        compiled_regex = re.compile(pattern)
        matches = series.str.match(compiled_regex)
        non_matching_count = (~matches).sum()
        total_count = len(series)
        failure_rate = non_matching_count / total_count if total_count > 0 else 0.0

        status = CheckStatus.PASS if failure_rate <= max_failure_rate else CheckStatus.FAIL
        return CheckResult(
            check_name="pattern_match",
            status=status,
            message=f"Column '{column}' pattern failure rate: {failure_rate:.2%} ({non_matching_count} rows)",
            metrics={"failure_rate": failure_rate, "failed_count": int(non_matching_count)},
        )
```

---

## 3. Writing Unit Tests

Add corresponding unit tests under `tests/`:

```python
# tests/test_pattern_checker.py
import pandas as pd
from src.validator.pattern_checker import PatternChecker
from src.validator.core import CheckStatus

def test_pattern_checker_valid_emails():
    df = pd.DataFrame({"email": ["alice@domain.com", "bob@domain.org"]})
    result = PatternChecker.check_regex(df, "email", r"^[^@]+@[^@]+\.[^@]+$")
    assert result.status == CheckStatus.PASS
```

---

## 4. Code Style & Review Checklist

Before opening a Pull Request:
- [ ] Run flake8 linting: `flake8 src/ tests/`
- [ ] Run test suite: `pytest tests/ -v`
- [ ] Ensure all new markdown files pass doc link checks: `python scripts/validate_docs.py`
- [ ] Update `CHANGELOG.md` with description of changes.
