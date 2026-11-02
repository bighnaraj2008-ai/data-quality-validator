#!/usr/bin/env python3
"""Automated data quality telemetry summary report generator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


def build_summary_markdown(reports: List[Dict[str, Any]]) -> str:
    """Render an executive Markdown telemetry summary from parsed JSON reports."""
    lines = [
        "# Data Quality Telemetry Summary",
        "",
        "| Dataset | Status | Total Rows | Checks Run | Duration (ms) |",
        "|:--------|:------:|-----------:|-----------:|--------------:|",
    ]
    for r in reports:
        lines.append(
            f"| `{r.get('dataset_path', 'unknown')}` "
            f"| **{r.get('overall_status', 'UNKNOWN')}** "
            f"| {r.get('total_rows', 0):,} "
            f"| {r.get('checks_run', 0)} "
            f"| {r.get('duration_ms', 0.0):.2f} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate telemetry Markdown summary from JSON reports.")
    parser.add_argument("--input-dir", required=True, help="Directory of JSON reports.")
    parser.add_argument("--output", required=True, help="Output Markdown summary path.")
    args = parser.parse_args()

    in_dir = Path(args.input_dir)
    parsed: List[Dict[str, Any]] = []
    if in_dir.is_dir():
        for path in sorted(in_dir.glob("*.json")):
            try:
                parsed.append(json.loads(path.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, OSError):
                continue

    md = build_summary_markdown(parsed)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(f"Generated telemetry summary ({len(parsed)} report(s)) -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
