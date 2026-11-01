#!/usr/bin/env bash
#
# check_formatting.sh - Preview Python/SQL formatting without enforcing.
#
# Shows what black would change and summarizes flake8/sqlfluff findings.
# Useful as a pre-commit sanity check that does not fail on style drift.
#
# Usage:
#   ./scripts/check_formatting.sh
#
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "==> black: preview formatting changes (--diff --check)"
python -m black --diff --check src tests scripts

echo "==> flake8: statistics summary"
python -m flake8 src tests scripts --statistics

echo "==> sqlfluff: SQL check templates"
python -m sqlfluff lint sql/checks/ --dialect ansi

echo "==> Formatting checks complete"
