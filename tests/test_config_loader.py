"""Unit tests for ConfigLoader module."""

from pathlib import Path
import pytest

from config.loader import ConfigLoader


def test_default_config_loading():
    config = ConfigLoader.load()
    assert config["version"] == "1.0"
    assert config["thresholds"]["default_null_threshold"] == 0.0
    assert config["database"]["backend"] == "sqlite"


def test_yaml_config_loading(tmp_path: Path):
    yaml_file = tmp_path / "custom.yaml"
    yaml_file.write_text(
        """
database:
  path: "custom.db"
thresholds:
  default_null_threshold: 0.15
  strict_schema: true
""",
        encoding="utf-8",
    )
    config = ConfigLoader.load(yaml_file)
    assert config["database"]["path"] == "custom.db"
    assert config["thresholds"]["default_null_threshold"] == 0.15
    assert config["thresholds"]["strict_schema"] is True


def test_environment_variable_overrides(monkeypatch):
    monkeypatch.setenv("DQ_DB_PATH", "env_override.db")
    monkeypatch.setenv("DQ_NULL_THRESHOLD", "0.25")
    monkeypatch.setenv("DQ_STRICT_SCHEMA", "true")

    config = ConfigLoader.load()
    assert config["database"]["path"] == "env_override.db"
    assert config["thresholds"]["default_null_threshold"] == 0.25
    assert config["thresholds"]["strict_schema"] is True


def test_invalid_null_threshold_raises_value_error(monkeypatch):
    monkeypatch.setenv("DQ_NULL_THRESHOLD", "1.5")
    with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
        ConfigLoader.load()
