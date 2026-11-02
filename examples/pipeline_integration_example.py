"""Example: Integrating Data Quality Validator into an ETL Pipeline Orchestrator."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from validator.core import BaselineSchema, CheckStatus, DataValidator  # noqa: E402


def run_etl_quality_gate(dataset_path: Path, report_out: Path) -> bool:
    """Validate an incoming CSV extract before downstream warehouse loading."""
    df = pd.read_csv(dataset_path)
    schema = BaselineSchema(
        columns={"id": "int64", "email": "object", "age": "int64", "income": "float64"},
        primary_key=["id"],
        strict=False,
    )
    validator = DataValidator(schema=schema, null_threshold=0.05, strict_schema=False)
    report = validator.validate_df(
        df,
        dataset_path=str(dataset_path),
        column_ranges={"age": {"min": 0.0, "max": 120.0}, "income": {"min": 0.0, "max": 10_000_000.0}},
        non_nullable_cols=["id", "email"],
    )

    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
    print(f"Quality gate result: {report.overall_status.value} ({report.duration_ms:.2f} ms)")
    return report.overall_status != CheckStatus.FAIL


if __name__ == "__main__":
    sample_csv = REPO_ROOT / "tests" / "fixtures" / "clean_dataset.csv"
    out_json = REPO_ROOT / "reports" / "etl_gate_report.json"
    ok = run_etl_quality_gate(sample_csv, out_json)
    print(f"Pipeline ready to proceed: {ok}")
