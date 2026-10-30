"""Metadata validation check for test suite components and templates."""

from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_config_yaml_is_valid():
    """Verify default validator configuration YAML is syntactically valid."""
    config_path = REPO_ROOT / "src" / "config" / "validator_config.yaml"
    assert config_path.exists()
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert "version" in data
    assert "thresholds" in data
    assert "rules" in data
    assert "null_checks" in data["rules"]


def test_fixtures_directory_completeness():
    """Verify all required test fixture files exist and are non-empty."""
    fixtures_dir = REPO_ROOT / "tests" / "fixtures"
    required = [
        "clean_dataset.csv",
        "drifted_dataset.csv",
        "null_anomaly.json",
        "duplicate_keys.csv",
    ]
    for filename in required:
        file_path = fixtures_dir / filename
        assert file_path.exists(), f"Fixture {filename} missing"
        assert file_path.stat().st_size > 0, f"Fixture {filename} is empty"


def test_sql_checks_directory_completeness():
    """Verify SQL checks exist and contain dialect declarations."""
    sql_dir = REPO_ROOT / "sql" / "checks"
    assert sql_dir.exists()
    for sql_file in sql_dir.glob("*.sql"):
        content = sql_file.read_text(encoding="utf-8")
        assert len(content.strip()) > 0
