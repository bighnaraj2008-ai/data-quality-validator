"""Automated local verification tests for CI workflow matrices and configs."""

from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def test_ci_validation_matrix_covers_supported_pythons():
    """Verify ci_validation.yml tests Python 3.9 through 3.12."""
    wf_path = REPO_ROOT / ".github" / "workflows" / "ci_validation.yml"
    assert wf_path.exists(), "ci_validation.yml workflow missing"
    data = yaml.safe_load(wf_path.read_text(encoding="utf-8"))
    matrix_versions = data["jobs"]["validate"]["strategy"]["matrix"]["python-version"]
    for expected in ["3.9", "3.10", "3.11", "3.12"]:
        assert expected in matrix_versions, f"Python {expected} missing from CI matrix"


def test_required_ci_workflows_parse_cleanly():
    """Verify all GitHub Actions YAML workflows parse without errors."""
    wf_dir = REPO_ROOT / ".github" / "workflows"
    expected_workflows = [
        "ci_validation.yml",
        "sql_lint.yml",
        "release_package.yml",
        "security_scan.yml",
        "code_ql.yml",
        "dependency_check.yml",
        "docs_check.yml",
    ]
    for name in expected_workflows:
        wf = wf_dir / name
        assert wf.exists(), f"Missing CI workflow: {name}"
        parsed = yaml.safe_load(wf.read_text(encoding="utf-8"))
        assert "jobs" in parsed and parsed["jobs"], f"Workflow {name} defines no jobs"
