#!/usr/bin/env bash
# Smoke test script for Data Quality Validator

set -euo pipefail

echo "=========================================="
echo " Starting Data Quality Validator Smoke Test"
echo "=========================================="

PYTHON_BIN="${PYTHON:-python}"
TEMP_DATA="smoke_sample.csv"
TEMP_REPORT="smoke_report.json"

# 1. Create temporary sample CSV
cat << 'EOF' > "$TEMP_DATA"
id,email,age,income
1,alice@example.com,28,65000.00
2,bob@example.com,35,82000.50
3,carol@example.com,42,95000.00
4,david@example.com,22,48000.00
5,emma@example.com,31,73500.25
EOF

echo "✓ Created synthetic dataset: $TEMP_DATA"

# 2. Execute CLI validation runner
"$PYTHON_BIN" scripts/run_validation.py --data "$TEMP_DATA" --config src/config/validator_config.yaml
echo "✓ Validation pipeline runner passed successfully"

# 3. Generate JSON report
"$PYTHON_BIN" scripts/generate_report.py --input "$TEMP_DATA" --output "$TEMP_REPORT" --format json
if [[ -f "$TEMP_REPORT" ]]; then
    echo "✓ Telemetry report generated successfully at $TEMP_REPORT"
else
    echo "✗ Failed to generate telemetry report"
    exit 1
fi

# 4. Clean up temporary files
rm -f "$TEMP_DATA" "$TEMP_REPORT"
echo "✓ Temporary test artifacts cleaned up"

echo "=========================================="
echo " All Smoke Tests Passed Successfully!"
echo "=========================================="
