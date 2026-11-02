#!/usr/bin/env bash
# End-to-end batch validation, failure archival, and log rotation demo.
set -euo pipefail

mkdir -p reports archives

echo "==> Step 1: Validate fixture datasets"
python scripts/run_validation.py --data tests/fixtures/clean_dataset.csv --config src/config/validator_config.yaml || true
python scripts/generate_report.py --input tests/fixtures/drifted_dataset.csv --output reports/drifted_report.json --format json || true

echo "==> Step 2: Export failure telemetry to CSV"
python scripts/export_reports.py --input reports/ --output archives/failures.csv --format csv

echo "==> Step 3: Dry-run historical report pruning"
python scripts/prune_reports.py --reports-dir reports/ --max-age-days 30 --keep-latest 10 --dry-run

rm -rf reports archives
echo "==> Batch CLI demonstration finished cleanly"
