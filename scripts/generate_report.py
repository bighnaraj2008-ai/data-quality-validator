#!/usr/bin/env python3
"""Telemetry and audit report generation utility script for Data Quality Validator.

Usage:
    python scripts/generate_report.py --input data.csv --output report.md
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from validator.core import BaselineSchema, DataValidator  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate markdown/json telemetry report for data validation")
    parser.add_argument("--input", "-i", required=True, help="Input CSV dataset path")
    parser.add_argument("--schema", "-s", help="Baseline schema JSON path")
    parser.add_argument("--output", "-o", default="data_quality_report.md", help="Output report file path")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Report output format")
    return parser.parse_args()


def generate_markdown(report_dict: dict) -> str:
    lines = [
        "# Data Quality Validation Telemetry Report",
        "",
        f"- **Dataset Path**: `{report_dict['dataset_path']}`",
        f"- **Timestamp**: `{datetime.now(timezone.utc).isoformat()}`",
        f"- **Total Rows**: {report_dict['total_rows']}",
        f"- **Total Columns**: {report_dict['total_columns']}",
        f"- **Overall Status**: **{report_dict['overall_status']}**",
        f"- **Execution Duration**: {report_dict['duration_ms']:.2f} ms",
        "",
        "## Summary of Executed Checks",
        "",
        "| Check Name | Status | Message | Duration (ms) |",
        "|:-----------|:-------|:--------|:--------------|",
    ]
    for r in report_dict["results"]:
        lines.append(f"| `{r['name']}` | **{r['status']}** | {r['message']} | {r['execution_time_ms']:.2f} |")

    lines.append("")
    lines.append("---")
    lines.append("*Generated automatically by `scripts/generate_report.py`.*")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    csv_path = Path(args.input)
    if not csv_path.exists():
        print(f"File not found: {csv_path}", file=sys.stderr)
        return 1

    schema = BaselineSchema.from_json_file(args.schema) if args.schema else None
    validator = DataValidator(schema=schema)
    report = validator.validate_csv(csv_path)

    out_path = Path(args.output)
    if args.format == "json":
        out_path.write_text(report.to_json(), encoding="utf-8")
    else:
        md_text = generate_markdown(report.to_dict())
        out_path.write_text(md_text, encoding="utf-8")

    print(f"Report generated successfully -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
