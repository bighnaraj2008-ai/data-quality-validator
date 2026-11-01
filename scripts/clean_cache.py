"""Utility script to clean workflow caches, Python bytecode, and build objects."""

import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

TARGET_DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
    "build",
    "dist",
    "htmlcov",
    "bundle",
}


def clean_caches(root: Path = REPO_ROOT) -> int:
    """Remove generated build and cache directories cleanly."""
    removed = 0
    for path in list(root.rglob("*")):
        if not path.exists():
            continue
        if any(part in {".git", "venv", ".venv"} for part in path.parts):
            continue
        if path.is_dir() and (path.name in TARGET_DIR_NAMES or path.name.endswith(".egg-info")):
            shutil.rmtree(path, ignore_errors=True)
            removed += 1
        elif path.is_file() and path.suffix in {".pyc", ".pyo", ".coverage"}:
            path.unlink(missing_ok=True)
            removed += 1
    return removed


if __name__ == "__main__":
    count = clean_caches()
    print(f"Cleaned {count} cache/build artifacts from {REPO_ROOT}")
