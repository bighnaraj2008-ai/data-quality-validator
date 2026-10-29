"""Duplicate row and primary key collision detection module.

Detects exact row duplicates and primary/composite key collisions
across incoming DataFrames.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import pandas as pd

from validator.core import CheckResult, CheckStatus


class DuplicateChecker:
    """Detects duplicate rows and primary key uniqueness violations."""

    def check_duplicates(
        self,
        df: pd.DataFrame,
        primary_key: Optional[List[str]] = None,
    ) -> CheckResult:
        total_rows = len(df)
        if total_rows == 0:
            return CheckResult(
                name="duplicate_rows",
                status=CheckStatus.PASS,
                message="Dataset is empty; zero duplicate rows.",
                metrics={"total_rows": 0, "duplicate_count": 0},
            )

        if primary_key:
            missing_pk = [col for col in primary_key if col not in df.columns]
            if missing_pk:
                return CheckResult(
                    name="duplicate_rows",
                    status=CheckStatus.FAIL,
                    message=f"Primary key column(s) not found in dataset: {missing_pk}",
                    metrics={"missing_columns": missing_pk},
                )
            
            duplicates_mask = df.duplicated(subset=primary_key, keep=False)
            dup_count = int(df.duplicated(subset=primary_key, keep='first').sum())
            key_name = ", ".join(primary_key)

            if dup_count > 0:
                offending_df = df[duplicates_mask].head(5)
                offending = offending_df[primary_key].to_dict(orient="records")
                return CheckResult(
                    name="duplicate_rows",
                    status=CheckStatus.FAIL,
                    message=f"Found {dup_count} duplicate primary key entries on [{key_name}].",
                    metrics={
                        "total_rows": total_rows,
                        "duplicate_keys": dup_count,
                        "primary_key": primary_key,
                    },
                    offending_sample=offending,
                )
            return CheckResult(
                name="duplicate_rows",
                status=CheckStatus.PASS,
                message=f"Primary key uniqueness verified on [{key_name}].",
                metrics={"total_rows": total_rows, "duplicate_keys": 0},
            )

        # Full row duplicates
        dup_count = int(df.duplicated().sum())
        if dup_count > 0:
            offending = df[df.duplicated(keep=False)].head(5).to_dict(orient="records")
            return CheckResult(
                name="duplicate_rows",
                status=CheckStatus.FAIL,
                message=f"Found {dup_count} exact duplicate rows in dataset.",
                metrics={"total_rows": total_rows, "duplicate_rows": dup_count},
                offending_sample=offending,
            )

        return CheckResult(
            name="duplicate_rows",
            status=CheckStatus.PASS,
            message="No duplicate rows found; all rows are distinct.",
            metrics={"total_rows": total_rows, "duplicate_rows": 0},
        )
