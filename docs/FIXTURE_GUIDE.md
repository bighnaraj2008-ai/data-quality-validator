# Authoring Custom Test Fixtures Guide

## 1. Overview
Test fixtures provide reproducible datasets with known distributions, edge cases, and anomalies.

## 2. Fixture Design Principles
1. **Deterministic Seeds**: Synthetic generators should produce deterministic sequences when parameterized.
2. **Targeted Anomalies**: Each fixture should focus on an explicit anomaly (e.g., duplicate PKs, null spike, schema mutation).
3. **Compact Footprint**: Keep unit and integration fixtures under 100 rows for fast CI execution. Use performance suites for high-volume stress testing.

## 3. Generating Custom Fixtures with Python
Use the provided script under `examples/custom_fixture_generator.py`:

```bash
# Generate a CSV with 15% null values
python examples/custom_fixture_generator.py --rows 100 --null-rate 0.15 --out-csv tests/fixtures/my_fixture.csv

# Generate a JSON fixture
python examples/custom_fixture_generator.py --rows 50 --null-rate 0.05 --out-json tests/fixtures/my_fixture.json
```
