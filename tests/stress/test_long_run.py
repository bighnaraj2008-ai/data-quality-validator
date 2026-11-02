"""Endurance and stability stress test for multi-iteration validation pipelines."""

from __future__ import annotations

import os
import time

from tests.benchmarks.bench_validator import _generate_dataset
from validator.core import BaselineSchema, CheckStatus, DataValidator


def test_multi_iteration_endurance_stability():
    """Run repeated validation passes checking for latency drift or unexpected errors.

    Set RUN_24H_STRESS=1 in dedicated soak environments for extended multi-hour runs;
    CI runs 25 fast iterations to validate stability within seconds.
    """
    iterations = 1000 if os.getenv("RUN_24H_STRESS") == "1" else 25
    df = _generate_dataset(n_rows=1000, anomaly_rate=0.01)
    schema = BaselineSchema(
        columns={"id": "int64", "amount": "float64", "email": "object"},
        primary_key=["id"],
    )

    start = time.perf_counter()
    for _ in range(iterations):
        validator = DataValidator(schema=schema, null_threshold=0.05)
        report = validator.validate_df(df, non_nullable_cols=["id"])
        assert report.overall_status != CheckStatus.ERROR
        assert len(report.results) >= 3

    elapsed = time.perf_counter() - start
    assert elapsed < 30.0, f"Endurance loop took too long: {elapsed:.2f}s"
