"""Utility script to clean test outputs, report artifacts, and pytest caches."""

from pathlib import Path
import shutil

REPO_ROOT = Path(__file__).resolve().parent.parent

TARGET_DIRS = [
    ".pytest_cache",
    ".ruff_cache",
    ".coverage",
    "htmlcov",
    "__pycache__",
]

TARGET_FILES = [
    "smoke_sample.csv",
    "smoke_report.json",
    ".coverage",
    "test_run_report.md",
]


def clean():
    print("Cleaning test and build artifacts...")
    for target in TARGET_DIRS:
        for p in REPO_ROOT.rglob(target):
            if "venv" in p.parts or ".git" in p.parts:
                continue
            if p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
                print(f"  Removed directory: {p.relative_to(REPO_ROOT)}")

    for fname in TARGET_FILES:
        for p in REPO_ROOT.rglob(fname):
            if "venv" in p.parts or ".git" in p.parts:
                continue
            if p.is_file():
                p.unlink(missing_ok=True)
                print(f"  Removed file: {p.relative_to(REPO_ROOT)}")

    print("Test artifact cleanup complete.")


if __name__ == "__main__":
    clean()
