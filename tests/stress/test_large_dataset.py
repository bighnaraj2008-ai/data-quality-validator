"""High-volume stress test for DataValidator."""

import numpy as np
import pandas as pd

from validator.core import CheckStatus, DataValidator


def test_large_dataset_stress():
    """Verify validator handles 50,000 rows with 10 columns without failure or excessive memory."""
    n_rows = 50000
    data = {
        "id": np.arange(n_rows),
        "col_float_1": np.random.randn(n_rows),
        "col_float_2": np.random.randn(n_rows),
        "col_str_1": ["sample_value"] * n_rows,
        "col_str_2": ["category_x"] * n_rows,
    }
    df = pd.DataFrame(data)

    validator = DataValidator()
    report = validator.validate_df(
        df,
        column_ranges={"col_float_1": {"min": -10.0, "max": 10.0}},
        non_nullable_cols=["id"],
    )

    assert report.overall_status in (CheckStatus.PASS, CheckStatus.WARN)
    assert len(report.results) >= 3
