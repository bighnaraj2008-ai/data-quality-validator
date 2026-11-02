#!/usr/bin/env python3
"""Report rotation and historical validation log pruning utility.

Prunes aged validation report archives from a reports directory based on file
modification age, a keep-latest count, and a minimum retention floor. Safe by
design: prints a summary of what would be pruned and only deletes files when
run in execute mode (default). Use ``--dry-run`` to inspect first.

Usage:
    python scripts/prune_reports.py --reports-dir reports/ --max-age-days 30 --keep-latest 50 --dry-run
    python scripts/prune_reports.py --reports-dir reports/ --max-age-days 30 --keep-latest 50 --min-keep 10
    python scripts/prune_reports.py --reports-dir reports/ --pattern "*.json" --max-age-days 7 --dry-run

Exit codes:
    0 - pruning summary printed (deletions performed unless --dry-run)
    1 - directory error
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple

DEFAULT_PATTERN = "*.json"
DEFAULT_MIN_KEEP = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rotate and prune historical validation log reports.")
    parser.add_argument(
        "--reports-dir",
        "-d",
        required=True,
        help="Directory containing validation report files.",
    )
    parser.add_argument(
        "--pattern",
        default=DEFAULT_PATTERN,
        help=f"Glob pattern for report files (default: {DEFAULT_PATTERN}).",
    )
    parser.add_argument(
        "--max-age-days",
        type=int,
        help="Prune files older than this many days (by modification time).",
    )
    parser.add_argument(
        "--keep-latest",
        type=int,
        help="Always keep this many most recent files, regardless of age.",
    )
    parser.add_argument(
        "--min-keep",
        type=int,
        default=DEFAULT_MIN_KEEP,
        help=f"Never prune below this many files (default: {DEFAULT_MIN_KEEP}).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List files that would be pruned without deleting them.",
    )
    return parser.parse_args()


def _list_report_files(reports_dir: Path, pattern: str) -> List[Path]:
    if not reports_dir.exists():
        print(f"Reports directory not found: {reports_dir}", file=sys.stderr)
        sys.exit(1)
    if not reports_dir.is_dir():
        print(f"Not a directory: {reports_dir}", file=sys.stderr)
        sys.exit(1)
    return sorted(reports_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)


def _select_prune_candidates(
    files: List[Path],
    max_age_days: int | None,
    keep_latest: int | None,
    min_keep: int,
) -> Tuple[List[Path], List[Path]]:
    """Return (prune, keep) lists.

    A file is pruned when it is older than max_age_days AND not among the
    keep_latest newest files, while never dropping below min_keep retained files.
    """
    now = time.time()
    age_limit = (max_age_days * 86400) if max_age_days else None

    newest = files[:keep_latest] if keep_latest else []
    newest_set = {id(p) for p in newest}

    prune: List[Path] = []
    keep: List[Path] = []

    for idx, path in enumerate(files):
        if idx < min_keep:
            keep.append(path)
            continue
        if id(path) in newest_set:
            keep.append(path)
            continue
        if age_limit is not None and (now - path.stat().st_mtime) <= age_limit:
            keep.append(path)
            continue
        prune.append(path)

    return prune, keep


def _format_size(path: Path) -> str:
    try:
        size = path.stat().st_size
    except OSError:
        return "unknown"
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.0f} {unit}"
        size /= 1024
    return f"{size:.0f} TB"


def _mtime_iso(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()


def main() -> int:
    args = parse_args()
    reports_dir = Path(args.reports_dir)
    files = _list_report_files(reports_dir, args.pattern)

    if not files:
        print(f"No report files matching '{args.pattern}' in {reports_dir}")
        return 0

    prune, keep = _select_prune_candidates(
        files,
        max_age_days=args.max_age_days,
        keep_latest=args.keep_latest,
        min_keep=max(0, args.min_keep),
    )

    print(f"Prune report rotation summary for {reports_dir}")
    print(f"Pattern: {args.pattern} | Total files: {len(files)}")
    if args.max_age_days:
        print(f"Max age: {args.max_age_days} day(s)")
    if args.keep_latest:
        print(f"Keep latest: {args.keep_latest} file(s)")
    print(f"Min keep: {args.min_keep} file(s)")
    print(f"Mode: {'DRY-RUN (no deletions)' if args.dry_run else 'EXECUTE (will delete)'}")
    print("-" * 70)

    if keep:
        print(f"Kept {len(keep)} file(s):")
        for path in keep:
            print(f"  [KEEP]  {path.name}  ({_format_size(path)})  mtime={_mtime_iso(path)}")

    if prune:
        verb = "Would prune" if args.dry_run else "Pruning"
        print(f"{verb} {len(prune)} file(s):")
        for path in prune:
            tag = "DRY-RUN" if args.dry_run else "PRUNE"
            print(f"  [{tag}]  {path.name}  ({_format_size(path)})  mtime={_mtime_iso(path)}")
            if not args.dry_run:
                try:
                    path.unlink()
                except OSError as exc:
                    print(f"        [ERROR] failed to delete {path.name}: {exc}", file=sys.stderr)
    else:
        print("No files selected for pruning.")

    print("-" * 70)
    print(f"Result: {len(keep)} kept, {len(prune)} {'would be pruned' if args.dry_run else 'pruned'}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
