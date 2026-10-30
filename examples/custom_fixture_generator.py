"""Utility script to generate custom synthetic CSV and JSON test fixtures."""

from __future__ import annotations

import argparse
import random
import pandas as pd


def generate_synthetic_dataset(
    num_rows: int = 100,
    null_ratio: float = 0.05,
    duplicate_ratio: float = 0.02,
) -> pd.DataFrame:
    """Generate synthetic DataFrame with configurable null and duplicate rates."""
    data = []
    for i in range(1, num_rows + 1):
        name = None if random.random() < null_ratio else f"User_{i}"
        email = None if random.random() < null_ratio else f"user_{i}@example.com"
        age = None if random.random() < null_ratio else random.randint(18, 75)
        income = None if random.random() < null_ratio else round(random.uniform(30000, 150000), 2)
        data.append({"id": i, "name": name, "email": email, "age": age, "income": income})

    df = pd.DataFrame(data)

    if duplicate_ratio > 0 and num_rows > 5:
        num_dups = int(num_rows * duplicate_ratio)
        dup_rows = df.sample(n=num_dups, replace=True)
        df = pd.concat([df, dup_rows], ignore_index=True)

    return df


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic data quality test fixtures.")
    parser.add_argument("--rows", "-r", type=int, default=50, help="Number of rows to generate.")
    parser.add_argument("--null-rate", type=float, default=0.10, help="Null rate injection ratio.")
    parser.add_argument("--out-csv", type=str, default=None, help="Output CSV file path.")
    parser.add_argument("--out-json", type=str, default=None, help="Output JSON file path.")
    args = parser.parse_args()

    df = generate_synthetic_dataset(num_rows=args.rows, null_ratio=args.null_rate)

    if args.out_csv:
        df.to_csv(args.out_csv, index=False)
        print(f"Generated CSV fixture at {args.out_csv}")
    if args.out_json:
        df.to_json(args.out_json, orient="records", indent=2)
        print(f"Generated JSON fixture at {args.out_json}")


if __name__ == "__main__":
    main()
