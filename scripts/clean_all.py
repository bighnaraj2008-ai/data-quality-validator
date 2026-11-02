#!/usr/bin/env python3
"""Master workspace cleaning and reset utility script."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.clean_cache import clean_caches  # noqa: E402


def clean_workspace(root: Path = REPO_ROOT) -> int:
    """Clean caches, build objects, and transient report/archive scratch folders."""
    removed = clean_caches(root)
    for transient in ("reports", "archives", ".coverage"):
        target = root / transient
        if target.is_dir():
            shutil.rmtree(target, ignore_errors=True)
            removed += 1
        elif target.is_file():
            target.unlink(missing_ok=True)
            removed += 1
    return removed


if __name__ == "__main__":
    count = clean_workspace()
    print(f"Master clean complete: removed {count} cache/transient artifact(s).")
