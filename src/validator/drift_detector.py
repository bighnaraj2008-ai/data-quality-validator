"""Schema drift detection module.

Detects column differences (missing columns, added columns) and data type category
mismatches between incoming DataFrames and baseline schemas.
"""

from __future__ import annotations

import pandas as pd

from validator.core import BaselineSchema, CheckResult, CheckStatus


def normalize_type_category(dtype_str: str) -> str:
    """Normalize common pandas/python/SQL types into high-level categories."""
    d = str(dtype_str).lower()
    if any(k in d for k in ("int", "int64", "int32", "integer")):
        return "integer"
    if any(k in d for k in ("float", "float64", "double", "numeric")):
        return "float"
    if any(k in d for k in ("bool", "boolean")):
        return "boolean"
    if any(k in d for k in ("date", "datetime", "timestamp")):
        return "datetime"
    return "string"


class DriftDetector:
    """Detects missing, added, and type-mismatched columns against a baseline schema."""

    def __init__(self, strict: bool = False) -> None:
        self.strict = strict

    def check_drift(self, df: pd.DataFrame, schema: BaselineSchema) -> CheckResult:
        """Compare DataFrame columns and normalized dtypes against baseline schema."""
        if df is None:
            return CheckResult(
                name="schema_drift",
                status=CheckStatus.ERROR,
                message="Input DataFrame is None; cannot evaluate schema drift.",
                metrics={},
            )
        if not schema or not schema.columns:
            return CheckResult(
                name="schema_drift",
                status=CheckStatus.PASS,
                message="No baseline schema defined; drift check skipped.",
                metrics={},
            )

        actual_cols = set(df.columns)
        expected_cols = set(schema.columns.keys())

        missing = sorted(list(expected_cols - actual_cols))
        added = sorted(list(actual_cols - expected_cols))

        type_mismatches = []
        for col in sorted(list(expected_cols & actual_cols)):
            exp_type = schema.columns[col]
            act_type = str(df[col].dtype)
            if normalize_type_category(exp_type) != normalize_type_category(act_type):
                type_mismatches.append(f"Column '{col}' expected {exp_type} but got {act_type}")

        violations = []
        if missing:
            violations.append(f"Missing required columns: {missing}")
        if type_mismatches:
            violations.append(f"Type mismatches: {type_mismatches}")

        is_strict = self.strict or schema.strict
        if added:
            if is_strict:
                violations.append(f"Unexpected extra columns (strict mode): {added}")
            else:
                msg = f"Schema drift notice: {len(added)} unexpected columns present: {added}"
                if not violations:
                    return CheckResult(
                        name="schema_drift",
                        status=CheckStatus.WARN,
                        message=msg,
                        metrics={"missing": missing, "added": added, "type_mismatches": type_mismatches},
                    )

        if violations:
            return CheckResult(
                name="schema_drift",
                status=CheckStatus.FAIL,
                message=f"Schema drift violation: {'; '.join(violations)}",
                metrics={"missing": missing, "added": added, "type_mismatches": type_mismatches},
            )

        return CheckResult(
            name="schema_drift",
            status=CheckStatus.PASS,
            message=f"Schema perfectly matches baseline ({len(expected_cols)} columns verified).",
            metrics={"missing": [], "added": [], "type_mismatches": []},
        )
