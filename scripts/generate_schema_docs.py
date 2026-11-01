#!/usr/bin/env python3
"""
Automated Schema Documentation Generator
Inspects validator configuration YAML structure and outputs markdown reference tables.
"""

import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "src" / "config" / "validator_config.yaml"


def generate_markdown_docs():
    if not CONFIG_PATH.exists():
        print(f"Error: {CONFIG_PATH} not found.")
        return

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    lines = [
        "# Automated Configuration Schema Reference",
        "",
        "This table is automatically generated from `src/config/validator_config.yaml`.",
        "",
        "| Section | Key | Type | Default Value |",
        "|:--------|:----|:-----|:--------------|",
    ]

    for section, values in data.items():
        if isinstance(values, dict):
            for k, v in values.items():
                val_type = type(v).__name__
                lines.append(f"| `{section}` | `{k}` | `{val_type}` | `{v}` |")
        else:
            val_type = type(values).__name__
            lines.append(f"| Root | `{section}` | `{val_type}` | `{values}` |")

    output_path = REPO_ROOT / "docs" / "SCHEMA_REFERENCE.md"
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Schema documentation generated at {output_path}")


if __name__ == "__main__":
    generate_markdown_docs()
