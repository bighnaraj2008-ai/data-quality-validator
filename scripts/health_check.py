"""CI environment diagnostic health check script."""

import importlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_MODULES = ["pandas", "yaml", "pydantic", "sqlalchemy", "pytest", "flake8"]
REQUIRED_FILES = [
    ".sqlfluff",
    "pyproject.toml",
    ".gitignore",
    "src/config/validator_config.yaml",
    ".github/workflows/ci_validation.yml",
    ".github/workflows/sql_lint.yml",
]


def run_health_check() -> int:
    """Inspect runtime dependencies and repository configuration artifacts."""
    print(f"Python version: {sys.version.split()[0]}")
    failures = 0

    for mod in REQUIRED_MODULES:
        try:
            importlib.import_module(mod)
            print(f"[OK] module: {mod}")
        except ImportError:
            print(f"[MISSING] module: {mod}")
            failures += 1

    for rel in REQUIRED_FILES:
        path = REPO_ROOT / rel
        if path.exists():
            print(f"[OK] file: {rel}")
        else:
            print(f"[MISSING] file: {rel}")
            failures += 1

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(run_health_check())
