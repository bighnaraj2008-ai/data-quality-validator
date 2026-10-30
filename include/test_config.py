"""Test suite configuration constants and path definitions."""

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
TESTS_DIR = ROOT_DIR / "tests"
FIXTURES_DIR = TESTS_DIR / "fixtures"

# Execution limits & timeouts
DEFAULT_TIMEOUT_SEC = 30.0
PERF_MIN_THROUGHPUT_ROWS_PER_SEC = 10000.0
MAX_PEAK_MEMORY_MB = 100.0

# Supported SQL Dialects
SUPPORTED_DIALECTS = ["ansi", "sqlite", "postgres", "snowflake", "bigquery"]

# Fixture Paths
CLEAN_DATASET_CSV = FIXTURES_DIR / "clean_dataset.csv"
DRIFTED_DATASET_CSV = FIXTURES_DIR / "drifted_dataset.csv"
NULL_ANOMALY_JSON = FIXTURES_DIR / "null_anomaly.json"
DUPLICATE_KEYS_CSV = FIXTURES_DIR / "duplicate_keys.csv"
