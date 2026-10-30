#!/usr/bin/env bash
# Automated Unit Test Suite Runner for Data Quality Validator

set -euo pipefail

echo "=========================================="
echo " Running Data Quality Validator Test Suite"
echo "=========================================="

PYTHON_BIN="${PYTHON:-python}"

echo "Executing pytest..."
"$PYTHON_BIN" -m pytest tests --tb=short -v

echo "=========================================="
echo " Test Suite Finished Successfully"
echo "=========================================="
