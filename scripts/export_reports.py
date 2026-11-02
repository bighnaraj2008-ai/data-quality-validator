#!/usr/bin/env python3
"""Export validation failure logs into structured CSV archives."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

DEFAULT_STATUSES = ("FAIL", "ERROR")
REPORT_FIELDS = (
    "exported_at",
    "dataset_path",
    "overall_status",
    "total_rows",
    "total_columns",
    "checks_run",
    "check_name",
    "status",
    "message",
    "execution_time_ms",
)


def export_csv(input_path: Path, output_path: Path) -> int:
    """Read a JSON validation report and write failing checks to CSV."""
    report: Dict[str, Any] = json.loads(input_path.read_text(encoding="utf-8"))
    exported_at = datetime.now(timezone.utc).isoformat()
    records: List[Dict[str, Any]] = []
    for result in report.get("results", []):
        if result.get("status") not in DEFAULT_STATUSES:
            continue
        records.append(
            {
                "exported_at": exported_at,
                "dataset_path": report.get("dataset_path", ""),
                "overall_status": report.get("overall_status", ""),
                "total_rows": report.get("total_rows", 0),
                "total_columns": report.get("total_columns", 0),
                "checks_run": report.get("checks_run", 0),
                "check_name": result.get("name", ""),
                "status": result.get("status", ""),
                "message": result.get("message", ""),
                "execution_time_ms": result.get("execution_time_ms", 0.0),
            }
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=REPORT_FIELDS)
        writer.writeheader()
        writer.writerows(records)
    return len(records)


def main() -> int:
    parser = argparse.ArgumentParser(description="Export validation failure logs to CSV.")
    parser.add_argument("--input", "-i", required=True)
    parser.add_argument("--output", "-o", required=True)
    args = parser.parse_args()
    count = export_csv(Path(args.input), Path(args.output))
    print(f"Exported {count} failure record(s) -> {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
