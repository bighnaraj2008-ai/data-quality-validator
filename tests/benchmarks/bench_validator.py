#!/usr/bin/env python3
"""Throughput & latency benchmarking harness for Data Quality Validator."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from validator.core import BaselineSchema, DataValidator  # noqa: E402

NUMERIC_COLUMNS = ["amount", "score", "temperature", "pressure", "rating", "count"]
STRING_COLUMNS = ["category", "region", "email"]
ALL_COLUMNS = ["id"] + NUMERIC_COLUMNS + STRING_COLUMNS


def generate_dataset(n_rows: int, anomaly_rate: float = 0.02, seed: int = 42) -> pd.DataFrame:
    """Create a synthetic multi-column DataFrame for validation benchmarking."""
    rng = np.random.default_rng(seed)
    n_rows = max(1, n_rows)
    return pd.DataFrame(
        {
            "id": np.arange(1, n_rows + 1),
            "amount": rng.uniform(10.0, 10_000.0, size=n_rows),
            "score": rng.uniform(0.0, 100.0, size=n_rows),
            "temperature": rng.uniform(-20.0, 50.0, size=n_rows),
            "pressure": rng.uniform(900.0, 1_100.0, size=n_rows),
            "rating": rng.uniform(1.0, 5.0, size=n_rows),
            "count": rng.integers(1, 100, size=n_rows),
            "category": rng.choice(["A", "B", "C", "D"], size=n_rows),
            "region": rng.choice(["NA", "EMEA", "APAC"], size=n_rows),
            "email": [f"user_{i}@example.com" for i in range(n_rows)],
        }
    )


def run_single_pass(n_rows: int = 1000) -> float:
    """Execute one validation pass and return duration in milliseconds."""
    schema = BaselineSchema(
        columns={
            col: ("int64" if col == "id" else ("float64" if col in NUMERIC_COLUMNS else "object"))
            for col in ALL_COLUMNS
        },
        primary_key=["id"],
    )
    column_ranges: Dict[str, Dict[str, float]] = {col: {"min": 0.0, "max": 1_000_000.0} for col in NUMERIC_COLUMNS}
    non_nullable_cols: List[str] = ["id"]
    df = generate_dataset(n_rows)
    validator = DataValidator(schema=schema, null_threshold=0.0, strict_schema=False)
    report = validator.validate_df(
        df,
        dataset_path="benchmark_dataset",
        column_ranges=column_ranges,
        non_nullable_cols=non_nullable_cols,
    )
    return report.duration_ms


if __name__ == "__main__":
    elapsed = run_single_pass(1000)
    print(f"Base harness pass (1,000 rows): {elapsed:.2f} ms")
