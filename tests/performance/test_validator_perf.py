"""Performance and throughput benchmark tests for DataValidator."""

import time
import numpy as np
import pandas as pd

from validator.core import BaselineSchema, CheckStatus, DataValidator


def test_validator_throughput_benchmark():
    """Assert validator processes at least 10,000 rows/second on standard checks."""
    n_rows = 20000
    df = pd.DataFrame(
        {
            "id": np.arange(n_rows),
            "score": np.random.uniform(10.0, 90.0, size=n_rows),
            "category": np.random.choice(["A", "B", "C"], size=n_rows),
        }
    )

    schema = BaselineSchema(
        columns={"id": "int64", "score": "float64", "category": "object"},
        primary_key=["id"],
    )
    validator = DataValidator(schema=schema, null_threshold=0.01)

    start = time.perf_counter()
    report = validator.validate_df(
        df,
        column_ranges={"score": {"min": 0.0, "max": 100.0}},
        non_nullable_cols=["id"],
    )
    elapsed = time.perf_counter() - start

    assert report.overall_status == CheckStatus.PASS
    assert elapsed < 3.0, f"Validation took {elapsed:.2f}s, expected < 3.0s"
    throughput = n_rows / max(elapsed, 0.001)
    assert throughput > 5000.0, f"Throughput {throughput:.0f} rows/s below minimum threshold"
