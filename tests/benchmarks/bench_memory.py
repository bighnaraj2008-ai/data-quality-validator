#!/usr/bin/env python3
"""Memory allocation footprint benchmarking utility for Data Quality Validator."""

from __future__ import annotations

import argparse
import sys
import tracemalloc
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from tests.benchmarks.bench_validator import ALL_COLUMNS, NUMERIC_COLUMNS, _generate_dataset  # noqa: E402
from validator.core import BaselineSchema, DataValidator  # noqa: E402


def measure_memory_footprint(n_rows: int = 10_000, anomaly_rate: float = 0.02) -> Dict[str, float]:
    """Measure peak Python heap allocation during multi-check dataset validation."""
    df = _generate_dataset(n_rows, anomaly_rate=anomaly_rate)
    schema = BaselineSchema(
        columns={
            col: ("int64" if col == "id" else ("float64" if col in NUMERIC_COLUMNS else "object"))
            for col in ALL_COLUMNS
        },
        primary_key=["id"],
    )
    ranges = {col: {"min": 0.0, "max": 1_000_000.0} for col in NUMERIC_COLUMNS}

    tracemalloc.start()
    validator = DataValidator(schema=schema, null_threshold=0.0, strict_schema=False)
    validator.validate_df(df, dataset_path="memory_benchmark", column_ranges=ranges, non_nullable_cols=["id"])
    current_bytes, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "n_rows": float(n_rows),
        "current_mb": round(current_bytes / (1024 * 1024), 4),
        "peak_mb": round(peak_bytes / (1024 * 1024), 4),
    }


def run_memory_suite(sizes: List[int]) -> List[Dict[str, float]]:
    """Run memory profiling across multiple dataset scales."""
    return [measure_memory_footprint(n_rows=s) for s in sizes]


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark peak memory usage of Data Quality Validator.")
    parser.add_argument("--rows", type=int, nargs="+", default=[1000, 10000, 50000])
    args = parser.parse_args()

    print("Data Quality Validator - Memory Allocation Profile")
    print("=" * 60)
    for res in run_memory_suite(args.rows):
        rows_cnt = int(res["n_rows"])
        print(f"Rows: {rows_cnt:,} | Peak Heap: {res['peak_mb']:.3f} MB | Current: {res['current_mb']:.3f} MB")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
