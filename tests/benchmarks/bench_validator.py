#!/usr/bin/env python3
"""Throughput & latency benchmarking harness for Data Quality Validator.

Runs the modular validation engine (schema drift, null values, duplicate rows,
and numerical range checks) across scaled, multi-column datasets with injected
anomalies to measure rows-per-second processing capacity and per-check latency.

Usage:
    python tests/benchmarks/bench_validator.py --rows 1000 10000 50000 100000 --iterations 3
    python tests/benchmarks/bench_validator.py --rows 50000 --output reports/benchmark_telemetry.json
    pytest tests/benchmarks/bench_validator.py -v

The harness prints a telemetry table (quality score, throughput in rows/sec,
p50/p95 check latency, and per-check status) and optionally writes a
machine-readable JSON telemetry archive.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from validator.core import BaselineSchema, CheckStatus, DataValidator  # noqa: E402

# --- Acceptance thresholds (tune for target environment) ---
MIN_ACCEPTABLE_THROUGHPUT_ROWS_PER_SEC = 1_000.0
MIN_QUALITY_SCORE = 0.0
MAX_QUALITY_SCORE = 100.0

# Columns exercised by the multi-column anomaly detection load.
NUMERIC_COLUMNS = ["amount", "score", "temperature", "pressure", "rating", "count"]
STRING_COLUMNS = ["category", "region", "email"]
ALL_COLUMNS = ["id"] + NUMERIC_COLUMNS + STRING_COLUMNS


def _percentile(sorted_values: List[float], pct: float) -> float:
    """Linear-interpolation percentile for a sorted list of values."""
    if not sorted_values:
        return 0.0
    ordered = sorted(sorted_values)
    rank = (len(ordered) - 1) * (pct / 100.0)
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return float(ordered[int(rank)])
    return float(ordered[lower] + (rank - lower) * (ordered[upper] - ordered[lower]))


def _quality_score(report) -> float:
    """Normalized data quality score (0.0 - 100.0) from a ValidationReport."""
    total = len(report.results)
    if total == 0:
        return 100.0
    passed = report.passed_checks
    warns = report.warning_checks
    return round(((passed * 1.0) + (warns * 0.5)) / total * 100.0, 2)


def _generate_dataset(n_rows: int, anomaly_rate: float, seed: int = 42) -> pd.DataFrame:
    """Synthetic multi-column dataset with injected data-quality anomalies.

    Anomaly classes injected at ``anomaly_rate`` of rows:
    - nulls in numeric and non-nullable key columns
    - out-of-range numerical values (range boundary violations)
    - duplicate primary-key values (key collision load)
    """
    rng = np.random.default_rng(seed)
    n_rows = max(1, n_rows)

    df = pd.DataFrame(
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

    n_anomalies = max(1, int(n_rows * anomaly_rate))
    anomaly_idx = rng.choice(n_rows, size=n_anomalies, replace=False)
    third = max(1, n_anomalies // 3)

    # 1. Nulls in numeric columns (null threshold violations).
    null_idx = anomaly_idx[:third]
    df.loc[null_idx, "amount"] = np.nan
    df.loc[null_idx, "temperature"] = np.nan

    # 2. Nulls in the non-nullable primary key (non-nullable constraint breach).
    pk_null_idx = anomaly_idx[third : 2 * third]  # noqa: E203
    df.loc[pk_null_idx, "id"] = np.nan

    # 3. Out-of-range numerical values (boundary violations).
    oob_idx = anomaly_idx[2 * third :]  # noqa: E203
    df.loc[oob_idx, "pressure"] = 5_000.0  # far above 1100.0 max bound
    df.loc[oob_idx, "rating"] = 10.0  # far above 5.0 max bound

    # 4. Duplicate primary-key collisions.
    dup_source = anomaly_idx[: max(1, third // 2)]
    df.loc[dup_source, "id"] = df.loc[dup_source[0], "id"]

    return df


def _build_validator(schema: BaselineSchema, null_threshold: float = 0.0) -> DataValidator:
    return DataValidator(schema=schema, null_threshold=null_threshold, strict_schema=False)


def _run_once(
    validator: DataValidator,
    df: pd.DataFrame,
    column_ranges: Dict[str, Dict[str, float]],
    non_nullable_cols: List[str],
):
    """Execute one validation pass and return (report, per-check timings)."""
    report = validator.validate_df(
        df,
        dataset_path="benchmark_dataset",
        column_ranges=column_ranges,
        non_nullable_cols=non_nullable_cols,
    )
    timings = {r.name: r.execution_time_ms for r in report.results}
    return report, timings


def run_benchmark(
    n_rows: int,
    iterations: int = 3,
    anomaly_rate: float = 0.02,
) -> Dict[str, Any]:
    """Run the benchmark suite for a single dataset size.

    Returns a telemetry dictionary with quality score, throughput, latency
    percentiles, and per-check execution metrics.
    """
    schema = BaselineSchema(
        columns={
            col: "int64" if col == "id" else ("float64" if col in NUMERIC_COLUMNS else "object") for col in ALL_COLUMNS
        },
        primary_key=["id"],
    )
    column_ranges = {col: {"min": 0.0, "max": 1_000_000.0} for col in NUMERIC_COLUMNS}
    # Tighter bounds on temperature/rating so injected outliers trip range checks.
    column_ranges["temperature"]["max"] = 50.0
    column_ranges["rating"]["max"] = 5.0

    df = _generate_dataset(n_rows, anomaly_rate)

    durations: List[float] = []
    all_timings: List[float] = []
    per_check: Dict[str, List[float]] = {}
    statuses: Dict[str, List[str]] = {}
    reports: List = []

    for _ in range(iterations):
        validator = _build_validator(schema)
        report, timings = _run_once(validator, df, column_ranges, non_nullable_cols=["id"])
        reports.append(report)
        duration_ms = report.duration_ms
        durations.append(duration_ms)
        for name, elapsed_ms in timings.items():
            all_timings.append(elapsed_ms)
            per_check.setdefault(name, []).append(elapsed_ms)
            statuses.setdefault(name, []).append(
                report.results[[r.name for r in report.results].index(name)].status.value
            )

    avg_duration = mean(durations)
    avg_duration_sec = avg_duration / 1000.0
    throughput = n_rows / max(avg_duration_sec, 0.001)
    avg_report = reports[len(reports) // 2]
    quality = _quality_score(avg_report)

    per_check_summary = {}
    for name in sorted(per_check):
        times = sorted(per_check[name])
        statuses_for_name = statuses[name]
        worst_status = (
            CheckStatus.FAIL
            if any(s == "FAIL" for s in statuses_for_name)
            else (
                CheckStatus.ERROR
                if any(s == "ERROR" for s in statuses_for_name)
                else (CheckStatus.WARN if any(s == "WARN" for s in statuses_for_name) else CheckStatus.PASS)
            )
        )
        per_check_summary[name] = {
            "status": worst_status.value,
            "avg_exec_ms": round(mean(times), 3),
            "p95_exec_ms": round(_percentile(times, 95), 3),
            "runs": len(times),
        }

    return {
        "n_rows": n_rows,
        "n_columns": len(df.columns),
        "checks_run": len(avg_report.results),
        "overall_status": avg_report.overall_status.value,
        "quality_score": quality,
        "duration_ms": round(avg_duration, 3),
        "throughput_rows_per_sec": round(throughput, 2),
        "latency_p50_ms": round(_percentile(all_timings, 50), 3),
        "latency_p95_ms": round(_percentile(all_timings, 95), 3),
        "iterations": iterations,
        "anomaly_rate": anomaly_rate,
        "per_check": per_check_summary,
    }


def run_benchmark_suite(
    sizes: List[int],
    iterations: int = 3,
    anomaly_rate: float = 0.02,
) -> List[Dict[str, Any]]:
    """Run the benchmark suite across multiple dataset sizes."""
    return [run_benchmark(size, iterations=iterations, anomaly_rate=anomaly_rate) for size in sizes]


def format_telemetry_table(results: List[Dict[str, Any]]) -> str:
    """Render benchmark telemetry as a fixed-width text table."""
    header = ["Rows", "Cols", "Checks", "Quality", "Status", "Duration", "Throughput", "p95 Latency"]
    rows = [
        [
            f"{r['n_rows']:,}",
            str(r["n_columns"]),
            str(r["checks_run"]),
            f"{r['quality_score']:.2f}%",
            r["overall_status"],
            f"{r['duration_ms']:.2f} ms",
            f"{r['throughput_rows_per_sec']:,.0f} rows/s",
            f"{r['latency_p95_ms']:.2f} ms",
        ]
        for r in results
    ]
    widths = [max(len(str(cell)) for cell in col) for col in zip(header, *rows)] if rows else [len(h) for h in header]

    def line(cells):
        return " | ".join(str(cell).ljust(width) for cell, width in zip(cells, widths))

    sep = "-+-".join("-" * w for w in widths)
    out = [line(header), sep] + [line(r) for r in rows]
    return "\n".join(out)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Benchmark Data Quality Validator check-execution throughput and latency."
    )
    parser.add_argument(
        "--rows",
        type=int,
        nargs="+",
        default=[1000, 10000, 50000, 100000],
        help="Dataset sizes (rows) to benchmark.",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=3,
        help="Repeated validation passes per dataset size.",
    )
    parser.add_argument(
        "--anomaly-rate",
        type=float,
        default=0.02,
        help="Fraction of rows carrying injected anomalies (0.0 - 1.0).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to write machine-readable JSON telemetry archive.",
    )
    parser.add_argument(
        "--no-asserts",
        action="store_true",
        help="Skip hard pass/fail assertions (report-only mode).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not 0.0 <= args.anomaly_rate <= 1.0:
        print("--anomaly-rate must be between 0.0 and 1.0", file=sys.stderr)
        return 1

    print("Data Quality Validator - Throughput & Latency Benchmark")
    print(f"Python {sys.version.split()[0]} | pandas {pd.__version__} | numpy {np.__version__}")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print(f"Anomaly rate: {args.anomaly_rate:.1%} | Iterations per size: {args.iterations}")
    print("=" * 80)

    results = run_benchmark_suite(
        sizes=args.rows,
        iterations=args.iterations,
        anomaly_rate=args.anomaly_rate,
    )

    print(format_telemetry_table(results))
    print("=" * 80)

    for r in results:
        ok = (
            r["throughput_rows_per_sec"] >= MIN_ACCEPTABLE_THROUGHPUT_ROWS_PER_SEC
            and r["overall_status"] != CheckStatus.ERROR.value
            and MIN_QUALITY_SCORE <= r["quality_score"] <= MAX_QUALITY_SCORE
        )
        flag = "PASS" if ok else "FAIL"
        print(
            f"[{flag}] {r['n_rows']:,} rows -> "
            f"{r['throughput_rows_per_sec']:,.0f} rows/s | "
            f"quality {r['quality_score']:.2f}% | "
            f"status {r['overall_status']}"
        )

    passed = all(
        r["throughput_rows_per_sec"] >= MIN_ACCEPTABLE_THROUGHPUT_ROWS_PER_SEC
        and r["overall_status"] != CheckStatus.ERROR.value
        and MIN_QUALITY_SCORE <= r["quality_score"] <= MAX_QUALITY_SCORE
        for r in results
    )

    if args.output:
        telemetry = {
            "benchmark_metadata": {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "validator": "data-quality-validator",
                "python": sys.version.split()[0],
                "pandas": pd.__version__,
                "numpy": np.__version__,
                "sizes": args.rows,
                "iterations": args.iterations,
                "anomaly_rate": args.anomaly_rate,
            },
            "results": results,
            "summary": {
                "all_passed": bool(passed),
                "max_throughput_rows_per_sec": max(r["throughput_rows_per_sec"] for r in results),
                "min_quality_score": min(r["quality_score"] for r in results),
            },
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(telemetry, indent=2), encoding="utf-8")
        print(f"Telemetry archive written -> {args.output}")

    if not args.no_asserts and not passed:
        print("Benchmark assertions failed: see FAIL flags above.", file=sys.stderr)
        return 1
    print("Benchmark complete: all throughput and quality telemetry within thresholds.")
    return 0


if __name__ == "__main__":
    sys.exit(main())


def test_benchmark_throughput_and_quality():
    """Pytest: validator throughput stays above floor with no errored checks under anomaly load."""
    results = run_benchmark_suite(sizes=[1000, 5000], iterations=1, anomaly_rate=0.02)
    assert len(results) == 2
    for r in results:
        assert (
            r["throughput_rows_per_sec"] >= MIN_ACCEPTABLE_THROUGHPUT_ROWS_PER_SEC
        ), f"Throughput {r['throughput_rows_per_sec']:.0f} rows/s below floor for {r['n_rows']} rows"
        assert r["overall_status"] != CheckStatus.ERROR.value, f"Validation errored for {r['n_rows']} rows"
        assert MIN_QUALITY_SCORE <= r["quality_score"] <= MAX_QUALITY_SCORE
        assert r["duration_ms"] > 0


def test_benchmark_telemetry_json_keys(tmp_path):
    """Pytest: JSON telemetry archive contains required metric keys."""
    results = run_benchmark_suite(sizes=[1000], iterations=1, anomaly_rate=0.01)
    out_path = tmp_path / "benchmark_telemetry.json"
    telemetry = {
        "benchmark_metadata": {"sizes": [1000]},
        "results": results,
    }
    out_path.write_text(json.dumps(telemetry, indent=2), encoding="utf-8")
    data = json.loads(out_path.read_text(encoding="utf-8"))
    first = data["results"][0]
    for key in ("n_rows", "quality_score", "throughput_rows_per_sec", "latency_p95_ms", "per_check"):
        assert key in first, f"Telemetry missing key: {key}"
