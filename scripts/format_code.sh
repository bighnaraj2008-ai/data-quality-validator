#!/usr/bin/env bash
#
# format_code.sh - Auto-format Python source files and SQL check templates.
#
# Applies black formatting across src, tests, and scripts, then runs
# sqlfluff fix across sql/checks/.
#
# Usage:
#   ./scripts/format_code.sh
#
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "==> black: formatting Python code (src, tests, scripts)"
python -m black src tests scripts

echo "==> sqlfluff: fixing SQL check templates (sql/checks/)"
python -m sqlfluff fix sql/checks/ --dialect ansi --force

echo "==> Formatting complete; run ./scripts/run_linter.sh to verify"
