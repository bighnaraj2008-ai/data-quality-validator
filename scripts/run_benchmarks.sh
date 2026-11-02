#!/usr/bin/env bash
#
# run_benchmarks.sh - Execute throughput and memory benchmark suites locally.
#
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "==> Running Throughput & Latency Benchmark Harness"
python tests/benchmarks/bench_validator.py --rows 1000 10000 50000 --iterations 2

echo "==> Running Memory Allocation Footprint Benchmark"
python tests/benchmarks/bench_memory.py --rows 1000 10000 50000

echo "==> All benchmark suites completed cleanly"
