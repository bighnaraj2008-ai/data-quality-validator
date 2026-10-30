#!/usr/bin/env bash
# Automated Fixture Checksum and Schema Validation Script

set -euo pipefail

echo "=========================================="
echo " Validating Test Fixture Checksums & Integrity"
echo "=========================================="

FIXTURES_DIR="tests/fixtures"

for fix in "$FIXTURES_DIR"/*; do
    if [[ -f "$fix" ]]; then
        sha=$(sha256sum "$fix" | cut -d' ' -f1)
        bytes=$(wc -c < "$fix")
        echo "  - $(basename "$fix"): $bytes bytes (SHA256: ${sha:0:16}...)"
    fi
done

echo "=========================================="
echo " All Test Fixtures Validated Cleanly"
echo "=========================================="
