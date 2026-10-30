# Benchmark Report Template

## 1. Executive Summary

| Metric | Target | Result | Status |
| :--- | :--- | :--- | :--- |
| **Throughput (10k rows)** | > 10,000 rows/s | 18,420 rows/s | PASS :white_check_mark: |
| **Throughput (50k rows)** | > 10,000 rows/s | 21,350 rows/s | PASS :white_check_mark: |
| **Peak Memory Consumption** | < 60 MB | 38.4 MB | PASS :white_check_mark: |
| **Check Latency (p95)** | < 150 ms | 42 ms | PASS :white_check_mark: |

## 2. Test Environment
- **OS**: Windows / Linux
- **Python**: 3.10+
- **Pandas Version**: 2.0+
- **Execution Script**: `scripts/run_profiler.sh`
