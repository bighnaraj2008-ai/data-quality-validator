#!/usr/bin/env bash
# Smoke test script for Data Quality Validator

set -euo pipefail

echo "=========================================="
echo " Starting Data Quality Validator Smoke Test"
echo "=========================================="

PYTHON_BIN="${PYTHON:-python}"
TEMP_DATA="smoke_sample.csv"
TEMP_REPORT="smoke_report.json"

# 1. Verify test fixtures exist
echo "Checking core test fixtures..."
for f in "tests/fixtures/clean_dataset.csv" "tests/fixtures/drifted_dataset.csv"; do
    if [[ ! -f "$f" ]]; then
        echo "Missing fixture $f"
        exit 1
    fi
done
echo "Test fixtures verified"

# 2. Validate documentation integrity
echo "Validating documentation links and syntax..."
"$PYTHON_BIN" scripts/validate_docs.py
echo "Documentation links verified successfully"

# 3. Verify CI linter gates (flake8, sqlfluff, optional black)
echo "Running CI static analysis smoke gates..."
"$PYTHON_BIN" -m flake8 src tests scripts --count --max-line-length=120 --statistics
"$PYTHON_BIN" -m sqlfluff lint sql/checks/ --dialect ansi
if "$PYTHON_BIN" -m black --version >/dev/null 2>&1; then
    "$PYTHON_BIN" -m black --check src tests scripts
fi
echo "CI static analysis smoke gates passed"

# 4. Create temporary sample CSV
cat << 'EOF' > "$TEMP_DATA"
id,email,age,income
1,alice@example.com,28,65000.00
2,bob@example.com,35,82000.50
3,carol@example.com,42,95000.00
4,david@example.com,22,48000.00
5,emma@example.com,31,73500.25
EOF

echo "Created synthetic dataset: $TEMP_DATA"

# 5. Execute CLI validation runner
"$PYTHON_BIN" scripts/run_validation.py --data "$TEMP_DATA" --config src/config/validator_config.yaml
echo "Validation pipeline runner passed successfully"

# 6. Generate JSON report
"$PYTHON_BIN" scripts/generate_report.py --input "$TEMP_DATA" --output "$TEMP_REPORT" --format json
if [[ -f "$TEMP_REPORT" ]]; then
    echo "Telemetry report generated successfully at $TEMP_REPORT"
else
    echo "Failed to generate telemetry report"
    exit 1
fi

# 7. Verify benchmark harness and report utilities
echo "Verifying benchmark harness & report utility CLIs..."
"$PYTHON_BIN" tests/benchmarks/bench_validator.py --rows 1000 --iterations 1 --no-asserts
"$PYTHON_BIN" scripts/export_reports.py --help >/dev/null
"$PYTHON_BIN" scripts/prune_reports.py --help >/dev/null
"$PYTHON_BIN" scripts/health_check.py
"$PYTHON_BIN" scripts/validate_warehouse.py
echo "Benchmark harness, health check & report utilities verified"

# 8. Clean up temporary files
rm -f "$TEMP_DATA" "$TEMP_REPORT"
echo "Temporary test artifacts cleaned up"

echo "=========================================="
echo " All Smoke Tests Passed Successfully!"
echo "=========================================="
