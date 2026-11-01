"""Numerical range and boundary validation module.

Validates that numerical values in specified columns fall within
configured minimum and maximum boundary thresholds.
"""

from __future__ import annotations

from typing import Any, Dict
import pandas as pd

from validator.core import CheckResult, CheckStatus


class RangeChecker:
    """Inspects numerical column boundaries against min and max criteria."""

    def check_ranges(
        self,
        df: pd.DataFrame,
        column_ranges: Dict[str, Dict[str, float]],
    ) -> CheckResult:
        if not column_ranges or len(df) == 0:
            return CheckResult(
                name="range_boundaries",
                status=CheckStatus.PASS,
                message="No range validation criteria provided or empty dataset.",
                metrics={"total_rows": len(df)},
            )

        violations = []
        offending_samples = []
        metrics: Dict[str, Any] = {"total_rows": len(df), "columns_checked": []}

        for col, bounds in column_ranges.items():
            if col not in df.columns:
                violations.append(f"Column '{col}' not found in dataset for range check.")
                continue

            series = pd.to_numeric(df[col], errors="coerce")
            min_val = bounds.get("min")
            max_val = bounds.get("max")

            col_violations = 0
            if min_val is not None:
                under_mask = series < min_val
                under_count = int(under_mask.sum())
                if under_count > 0:
                    col_violations += under_count
                    violations.append(f"Column '{col}' has {under_count} values below minimum ({min_val})")

            if max_val is not None:
                over_mask = series > max_val
                over_count = int(over_mask.sum())
                if over_count > 0:
                    col_violations += over_count
                    violations.append(f"Column '{col}' has {over_count} values above maximum ({max_val})")

            metrics["columns_checked"].append(
                {
                    "column": col,
                    "min_bound": min_val,
                    "max_bound": max_val,
                    "violations": col_violations,
                }
            )

            if col_violations > 0:
                offending_samples.append(
                    {
                        "column": col,
                        "violation_count": col_violations,
                    }
                )

        status = CheckStatus.FAIL if violations else CheckStatus.PASS
        msg = (
            f"Range check failed: {'; '.join(violations)}"
            if violations
            else f"All {len(column_ranges)} specified column ranges satisfied."
        )

        return CheckResult(
            name="range_boundaries",
            status=status,
            message=msg,
            metrics=metrics,
            offending_sample=offending_samples,
        )
