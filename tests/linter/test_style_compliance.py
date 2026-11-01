"""Automated Python style and linter compliance test suite."""

import subprocess
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def test_flake8_zero_violations():
    """Verify flake8 reports zero errors across src, tests, and scripts."""
    pytest.importorskip("flake8")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "flake8",
            "src",
            "tests",
            "scripts",
            "--count",
            "--max-line-length=120",
            "--statistics",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Flake8 violations found:\n{result.stdout}\n{result.stderr}"


def test_pyproject_linter_sections_present():
    """Verify pyproject.toml declares black and flake8 tool rules."""
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "[tool.black]" in pyproject
    assert "[tool.flake8]" in pyproject
    assert "[tool.pytest.ini_options]" in pyproject
