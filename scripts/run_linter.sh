#!/usr/bin/env bash
#
# run_linter.sh - Run all linters for the Data Quality Validator project.
#
# Mirrors the CI lint stages (flake8, black, sqlfluff) so developers can
# verify Python and SQL style locally before committing.
#
# Usage:
#   ./scripts/run_linter.sh
#
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "==> flake8: Python style (src, tests, scripts)"
python -m flake8 src tests scripts --count --max-line-length=120 --statistics

echo "==> black: Python formatting check (src, tests, scripts)"
python -m black --check src tests scripts

echo "==> sqlfluff: SQL check templates (sql/checks/)"
python -m sqlfluff lint sql/checks/ --dialect ansi

echo "==> All linters passed"
