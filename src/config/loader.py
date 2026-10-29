"""Configuration loader with environment overrides for Data Quality Validator.

Parses YAML and JSON configurations, validates boundary rules,
and supports dynamic runtime overrides via environment variables.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
import yaml


class ConfigLoader:
    """Loads and validates Data Quality Validator configuration."""

    DEFAULT_CONFIG = {
        "version": "1.0",
        "environment": "development",
        "database": {
            "backend": "sqlite",
            "path": "dq_audit.db",
            "echo": False,
        },
        "thresholds": {
            "default_null_threshold": 0.0,
            "allow_duplicates": False,
            "strict_schema": False,
        },
        "rules": {
            "null_checks": {"non_nullable": [], "column_thresholds": {}},
            "ranges": {},
        },
    }

    @classmethod
    def load(cls, config_path: Optional[str | Path] = None) -> Dict[str, Any]:
        config: Dict[str, Any] = json.loads(json.dumps(cls.DEFAULT_CONFIG))

        if config_path:
            path = Path(config_path)
            if not path.exists():
                raise FileNotFoundError(f"Configuration file not found: {path}")

            content = path.read_text(encoding="utf-8")
            if path.suffix.lower() in (".yaml", ".yml"):
                loaded = yaml.safe_load(content) or {}
            else:
                loaded = json.loads(content) or {}

            # Deep merge dictionary
            for key, val in loaded.items():
                if isinstance(val, dict) and key in config and isinstance(config[key], dict):
                    config[key].update(val)
                else:
                    config[key] = val

        # Environment variable overrides
        if "DQ_DB_PATH" in os.environ:
            config["database"]["path"] = os.environ["DQ_DB_PATH"]

        if "DQ_NULL_THRESHOLD" in os.environ:
            try:
                config["thresholds"]["default_null_threshold"] = float(os.environ["DQ_NULL_THRESHOLD"])
            except ValueError:
                pass

        if "DQ_STRICT_SCHEMA" in os.environ:
            config["thresholds"]["strict_schema"] = os.environ["DQ_STRICT_SCHEMA"].lower() in ("1", "true", "yes")

        # Validate thresholds
        null_th = config["thresholds"].get("default_null_threshold", 0.0)
        if not (0.0 <= null_th <= 1.0):
            raise ValueError(f"default_null_threshold must be between 0.0 and 1.0, got: {null_th}")

        return config

    load_config = load
