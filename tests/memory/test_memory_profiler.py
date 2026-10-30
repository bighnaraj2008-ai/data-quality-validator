"""Memory consumption profile check harness for DataValidator."""

import tracemalloc
import numpy as np
import pandas as pd

from validator.core import CheckStatus, DataValidator


def test_memory_consumption_within_bounds():
    """Assert peak memory overhead during validation of 25,000 rows is below 60MB."""
    tracemalloc.start()
    try:
        n_rows = 25000
        df = pd.DataFrame({
            "id": np.arange(n_rows),
            "val_a": np.random.rand(n_rows),
            "val_b": np.random.rand(n_rows),
            "label": ["test_label"] * n_rows,
        })
        validator = DataValidator()
        report = validator.validate_df(
            df,
            column_ranges={"val_a": {"min": 0.0, "max": 1.0}},
            non_nullable_cols=["id"],
        )
        assert report.overall_status == CheckStatus.PASS
        current, peak = tracemalloc.get_traced_memory()
        peak_mb = peak / (1024 * 1024)
        assert peak_mb < 60.0, f"Peak memory {peak_mb:.2f} MB exceeded 60 MB limit"
    finally:
        tracemalloc.stop()
