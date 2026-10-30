#!/usr/bin/env bash
# Automated Unit Test Suite Runner for Data Quality Validator

set -euo pipefail

echo "=========================================="
echo " Running Data Quality Validator Test Suite"
echo "=========================================="

PYTHON_BIN="${PYTHON:-python}"
FIXTURES_DIR="tests/fixtures"

# Pre-execution fixture ingestion and verification
echo "--- Ingesting & Verifying Test Fixtures ---"
for fix in "clean_dataset.csv" "drifted_dataset.csv" "null_anomaly.json" "duplicate_keys.csv"; do
    if [[ -f "$FIXTURES_DIR/$fix" ]]; then
        rows=$(wc -l < "$FIXTURES_DIR/$fix" || echo "0")
        echo "  [OK] $fix verified ($rows lines)"
    else
        echo "  [ERROR] Fixture $fix missing from $FIXTURES_DIR"
        exit 1
    fi
done

echo "--- Executing Pytest Suites ---"
"$PYTHON_BIN" -m pytest tests --tb=short -v

echo "=========================================="
echo " All Tests and Fixture Checks Passed"
echo "=========================================="
