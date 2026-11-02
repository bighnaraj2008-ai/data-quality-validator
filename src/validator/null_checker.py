"""Null value inspection module.

Scans dataset columns for missing/null values against configurable thresholds
and flags non-nullable column violations.
"""

from __future__ import annotations

from typing import List, Optional
import pandas as pd

from validator.core import CheckResult, CheckStatus


class NullChecker:
    """Inspects null percentages across DataFrame columns."""

    def __init__(self, default_threshold: float = 0.0) -> None:
        self.default_threshold = max(0.0, min(1.0, default_threshold))

    def check_nulls(
        self,
        df: pd.DataFrame,
        custom_threshold: Optional[float] = None,
        non_nullable_cols: Optional[List[str]] = None,
    ) -> CheckResult:
        """Evaluate null counts and rates across columns in a single vectorized pass."""
        threshold = self.default_threshold if custom_threshold is None else custom_threshold
        non_nullable = set(non_nullable_cols or [])

        total_rows = len(df)
        if total_rows == 0:
            return CheckResult(
                name="null_values",
                status=CheckStatus.PASS,
                message="Dataset is empty; zero null violations.",
                metrics={"total_rows": 0, "violated_columns": []},
            )

        column_null_counts = df.isna().sum().to_dict()
        inv_rows = 1.0 / total_rows
        column_null_rates = {col: count * inv_rows for col, count in column_null_counts.items()}

        violations = []
        offending_samples = []

        for col, rate in column_null_rates.items():
            count = column_null_counts[col]
            if col in non_nullable and count > 0:
                violations.append(f"Non-nullable column '{col}' has {count} nulls ({rate:.1%})")
                offending_samples.append({"column": col, "null_count": count, "rate": round(rate, 4)})
            elif rate > threshold:
                violations.append(f"Column '{col}' null rate {rate:.1%} exceeds threshold {threshold:.1%}")
                offending_samples.append({"column": col, "null_count": count, "rate": round(rate, 4)})

        status = CheckStatus.FAIL if violations else CheckStatus.PASS
        msg = (
            f"Null check failed: {'; '.join(violations)}"
            if violations
            else f"All columns pass null threshold ({threshold:.1%})."
        )

        return CheckResult(
            name="null_values",
            status=status,
            message=msg,
            metrics={
                "total_rows": total_rows,
                "null_counts": column_null_counts,
                "null_rates": {k: round(v, 4) for k, v in column_null_rates.items()},
                "violations_count": len(violations),
            },
            offending_sample=offending_samples,
        )
