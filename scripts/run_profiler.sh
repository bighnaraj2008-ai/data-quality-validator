#!/usr/bin/env bash
# Automated Memory and Performance Profiling Script

set -euo pipefail

echo "=========================================="
echo " Starting Performance & Memory Profiling"
echo "=========================================="

PYTHON_BIN="${PYTHON:-python}"

echo "Running performance benchmarks..."
"$PYTHON_BIN" -m pytest tests/performance/ -v

echo "Running memory consumption profiler..."
"$PYTHON_BIN" -m pytest tests/memory/ -v

echo "=========================================="
echo " Profiling Complete: All Checks Within Thresholds"
echo "=========================================="
