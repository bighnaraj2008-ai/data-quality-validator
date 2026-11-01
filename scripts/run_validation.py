#!/usr/bin/env python3
"""Command-line execution wrapper script for Data Quality Validator.

Usage:
    python scripts/run_validation.py --file data.csv [--schema schema.json] [--strict]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from config.loader import ConfigLoader  # noqa: E402
from validator.core import BaselineSchema, CheckStatus, DataValidator  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Data Quality Validation checks on CSV dataset")
    parser.add_argument("--file", "--data", "-f", "-d", dest="file", required=True, help="Path to input CSV file")
    parser.add_argument("--schema", "-s", help="Path to baseline schema JSON file")
    parser.add_argument("--config", "-c", help="Path to validator configuration YAML file")
    parser.add_argument("--null-threshold", type=float, help="Override default null percentage threshold (0.0 - 1.0)")
    parser.add_argument(
        "--strict", action="store_true", help="Enforce strict schema validation (no unexpected columns)"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    csv_file = Path(args.file)
    if not csv_file.exists():
        print(f"[ERROR] Input file not found: {csv_file}", file=sys.stderr)
        return 1

    config = ConfigLoader.load(args.config)
    null_th = args.null_threshold if args.null_threshold is not None else config["thresholds"]["default_null_threshold"]
    is_strict = args.strict or config["thresholds"].get("strict_schema", False)

    schema = None
    if args.schema:
        schema_path = Path(args.schema)
        if not schema_path.exists():
            print(f"[ERROR] Schema file not found: {schema_path}", file=sys.stderr)
            return 1
        schema = BaselineSchema.from_json_file(schema_path)

    validator = DataValidator(schema=schema, null_threshold=null_th, strict_schema=is_strict)

    ranges = config.get("rules", {}).get("ranges")
    non_nullable = config.get("rules", {}).get("null_checks", {}).get("non_nullable")

    print("================================================================")
    print(f" DATA QUALITY VALIDATION RUNNER: {csv_file.name}")
    print("================================================================")
    report = validator.validate_csv(csv_file, column_ranges=ranges, non_nullable_cols=non_nullable)

    for r in report.results:
        status_tag = f"[{r.status.value}]"
        print(f"{status_tag:<8} {r.name:<18} : {r.message} ({r.execution_time_ms:.1f} ms)")

    print("----------------------------------------------------------------")
    print(f"Total Rows: {report.total_rows} | Total Checks: {len(report.results)}")
    print(f"Passed: {report.passed_checks} | Warnings: {report.warning_checks} | Failed: {report.failed_checks}")
    print(f"Overall Status: {report.overall_status.value} (took {report.duration_ms:.1f} ms)")
    print("================================================================")

    return 0 if report.overall_status in (CheckStatus.PASS, CheckStatus.WARN) else 1


if __name__ == "__main__":
    sys.exit(main())
