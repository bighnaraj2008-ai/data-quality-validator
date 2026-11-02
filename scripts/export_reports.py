#!/usr/bin/env python3
"""Export validation failure logs into structured CSV or JSON archives.

Reads validation report JSON file(s) produced by ``data-quality-validator``,
filters the failing/errored checks, and writes a structured archive (CSV or
JSON) suitable for data engineering pipelines, downstream alerting, and
long-term audit storage.

Usage:
    python scripts/export_reports.py --input reports/validation_report.json --output archives/failures.csv
    python scripts/export_reports.py --input reports/ --output archives/failures.json \\
        --format json --statuses FAIL,ERROR --archive-dir reports/processed

Exit codes:
    0 - archive written successfully (even when no failures are found)
    1 - input error or write failure
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

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
    "metrics",
    "offending_sample_count",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export validation failure logs into structured CSV/JSON archives.")
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Validation report JSON file or directory of report JSON files.",
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Archive output path (.csv or .json).",
    )
    parser.add_argument(
        "--format",
        choices=["csv", "json"],
        help="Output format. Defaults to the extension of --output.",
    )
    parser.add_argument(
        "--statuses",
        default=",".join(DEFAULT_STATUSES),
        help=f"Comma-separated check statuses to export (default: {','.join(DEFAULT_STATUSES)}).",
    )
    parser.add_argument(
        "--archive-dir",
        help="After export, move source report files into this directory.",
    )
    return parser.parse_args()


def _resolve_format(output: Path, fmt: str | None) -> str:
    if fmt:
        return fmt
    suffix = output.suffix.lower().lstrip(".")
    if suffix in ("csv", "json"):
        return suffix
    print(f"Cannot infer format from '{output}'; use --format csv|json", file=sys.stderr)
    sys.exit(1)


def _find_report_files(input_path: Path) -> List[Path]:
    if input_path.is_file():
        return [input_path]
    if input_path.is_dir():
        return sorted(input_path.glob("*.json"))
    print(f"Input not found: {input_path}", file=sys.stderr)
    sys.exit(1)


def _load_report(path: Path) -> Dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[SKIP] {path.name}: invalid report ({exc})", file=sys.stderr)
        return None


def _flatten_metrics(metrics: Dict[str, Any]) -> str:
    return json.dumps(metrics, sort_keys=True) if metrics else ""


def _build_failure_records(report: Dict[str, Any], statuses: Iterable[str]) -> List[Dict[str, Any]]:
    statuses = set(statuses)
    exported_at = datetime.now(timezone.utc).isoformat()
    records: List[Dict[str, Any]] = []
    for result in report.get("results", []):
        if result.get("status") not in statuses:
            continue
        offending = result.get("offending_sample") or []
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
                "metrics": _flatten_metrics(result.get("metrics", {})),
                "offending_sample_count": len(offending),
            }
        )
    return records


def _write_csv(records: List[Dict[str, Any]], output: Path) -> None:
    with output.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=REPORT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def _write_json(records: List[Dict[str, Any]], output: Path) -> None:
    archive = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "failure_count": len(records),
        "failures": records,
    }
    output.write_text(json.dumps(archive, indent=2), encoding="utf-8")


def _archive_sources(source_files: List[Path], archive_dir: Path) -> int:
    archive_dir.mkdir(parents=True, exist_ok=True)
    moved = 0
    for src in source_files:
        dest = archive_dir / src.name
        if dest.exists():
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
            dest = archive_dir / f"{src.stem}_{stamp}{src.suffix}"
        shutil.move(str(src), str(dest))
        moved += 1
    return moved


def main() -> int:
    args = parse_args()
    output = Path(args.output)
    fmt = _resolve_format(output, args.format)
    statuses = [s.strip().upper() for s in args.statuses.split(",") if s.strip()]

    input_path = Path(args.input)
    source_files = _find_report_files(input_path)

    records: List[Dict[str, Any]] = []
    processed: List[Path] = []
    for path in source_files:
        report = _load_report(path)
        if report is None:
            continue
        processed.append(path)
        records.extend(_build_failure_records(report, statuses))

    try:
        if fmt == "csv":
            _write_csv(records, output)
        else:
            _write_json(records, output)
    except OSError as exc:
        print(f"Failed to write archive: {exc}", file=sys.stderr)
        return 1

    print(f"Exported {len(records)} failure record(s) from {len(processed)} report(s) -> {output}")

    if args.archive_dir:
        try:
            moved = _archive_sources(processed, Path(args.archive_dir))
            print(f"Archived {moved} source report(s) -> {args.archive_dir}")
        except OSError as exc:
            print(f"Failed to archive source reports: {exc}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
