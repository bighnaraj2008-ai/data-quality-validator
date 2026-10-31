# Rule Authoring Guide — Custom YAML Validation Rules

`data-quality-validator` uses declarative YAML rule files to define which data
quality checks run against a dataset, the thresholds each check applies, the
severity assigned to violations, and where alerts are delivered.

The default rule file is `src/config/validator_config.yaml`. Additional rule
sets can be passed at runtime via `--config` on `scripts/run_validation.py`.

---

## 1. YAML Rule Syntax

A rule file is a nested mapping with the following top-level sections:

| Section | Required | Description |
|:--------|:--------:|:------------|
| `version` | yes | Rule schema version (currently `"1.0"`). |
| `environment` | no | Deployment label, e.g. `development`, `staging`, `production`. |
| `database` | no | Connection metadata for the audit store / SQL engine. |
| `thresholds` | yes | Global numeric thresholds applied across checks. |
| `rules` | yes | Check-specific rule definitions (nulls, ranges, uniqueness, drift). |
| `severity` | no | Severity mapping for warning vs. error escalation. |
| `alerting` | no | Alert webhook and notification targets. |

### Minimal Example

```yaml
version: "1.0"
environment: "production"

thresholds:
  default_null_threshold: 0.05
  strict_schema: true
  allow_duplicates: false

rules:
  null_checks:
    non_nullable:
      - id
      - email
    column_thresholds:
      phone_number: 0.20
      address: 0.15
  ranges:
    age:
      min: 0
      max: 120
```

### Section Reference

#### `database`

```yaml
database:
  backend: "sqlite"      # sqlite | postgresql | duckdb | snowflake | bigquery
  path: "dq_audit.db"    # local file path for file-based backends
  echo: false            # enable SQL statement logging (debug)
```

#### `thresholds`

| Key | Type | Default | Meaning |
|:----|:----:|:-------:|:--------|
| `default_null_threshold` | float | `0.0` | Maximum allowed null fraction per column (0.0-1.0). |
| `strict_schema` | bool | `false` | Treat unexpected columns as failures instead of warnings. |
| `allow_duplicates` | bool | `false` | Permit duplicate rows / keys without failing. |

#### `rules.null_checks`

| Key | Type | Description |
|:----|:----:|:------------|
| `non_nullable` | list[str] | Columns that must contain zero nulls. Any null -> **FAIL**. |
| `column_thresholds` | dict[str, float] | Per-column max null fraction overrides. |

#### `rules.ranges`

Per-column numerical boundary checks:

```yaml
rules:
  ranges:
    age:
      min: 0
      max: 120
    income:
      min: 0.0
      max: 500000.0
```

#### `rules.uniqueness` (duplicate detection)

```yaml
rules:
  uniqueness:
    primary_key: [id]            # composite keys: [order_id, line_no]
    allow_duplicates: false
```

#### `rules.schema_drift`

```yaml
rules:
  schema_drift:
    allow_unexpected_columns: false  # strict: added columns fail; non-strict warns
```

---

## 2. Threshold Parameters

Thresholds are resolved in the following precedence order (highest wins):

1. CLI flag (e.g. `--null-threshold`).
2. `DQ_*` environment variable override (see §4).
3. Per-column threshold in `rules.<check>.column_thresholds`.
4. Global default in `thresholds.default_null_threshold`.
5. Hard-coded engine default (`0.0` for nulls).

All fractional thresholds must be in the range `[0.0, 1.0]`. Values outside that
range cause `ConfigLoader.load()` to raise `ValueError`.

### Example: Per-Column Override

```yaml
thresholds:
  default_null_threshold: 0.05

rules:
  null_checks:
    column_thresholds:
      phone_number: 0.20   # allow up to 20% nulls
      address: 0.15        # allow up to 15% nulls
```

---

## 3. Severity Levels (Warning vs. Error)

Every check returns one of four statuses, modeled on `CheckStatus` in
`src/validator/core.py`:

| Status | Meaning | Pipeline Effect |
|:-------|:--------|:----------------|
| `PASS` | Check passed within thresholds. | No action. |
| `WARN` | Check degraded but acceptable (e.g. extra non-strict columns, null rate near threshold). | Pipeline continues; reported as warning. |
| `FAIL` | Check violated a hard threshold (non-nullable null, duplicate key, drift). | Pipeline continues; overall status `FAIL`; exit code `1`. |
| `ERROR` | Check crashed or input unreadable (file missing, parse error). | Treated as failure; error trace captured in report. |

### Severity Mapping in YAML

The `severity` block lets you promote or demote individual checks:

```yaml
severity:
  null_checks: "error"        # default FAIL
  schema_drift: "warning"     # downgrade drift violations to WARN
  duplicate_rows: "error"
  range_boundaries: "warning"
```

Valid values: `error`, `warning`. When a check is mapped to `warning`, a
violation that would normally emit `FAIL` is reported as `WARN` and does not
flip the overall report to `FAIL` on its own.

### Overall Report Status

`ValidationReport.overall_status` resolves as:

1. `FAIL` if any check is `FAIL` or `ERROR`.
2. `WARN` if any check is `WARN`.
3. `PASS` otherwise.

The CLI exits `0` for `PASS`/`WARN` and `1` for `FAIL`.

---

## 4. Environment Variable Overrides

Thresholds can be overridden at runtime without editing YAML using the `DQ_`
prefix. The loader performs a case-insensitive boolean parse and float
validation:

| Environment Variable | Config Path | Type | Example |
|:---------------------|:------------|:-----:|:--------|
| `DQ_NULL_THRESHOLD` | `thresholds.default_null_threshold` | float | `DQ_NULL_THRESHOLD=0.10` |
| `DQ_STRICT_SCHEMA` | `thresholds.strict_schema` | bool | `DQ_STRICT_SCHEMA=true` |
| `DQ_DB_PATH` | `database.path` | string | `DQ_DB_PATH=/tmp/dq_audit.db` |

```bash
export DQ_NULL_THRESHOLD=0.10
export DQ_STRICT_SCHEMA=true
python scripts/run_validation.py --data sample_data.csv --config src/config/validator_config.yaml
```

> **Security Note:** Never commit secrets (credentials, webhook URLs containing
> tokens) to `validator_config.yaml`. Inject them through environment variables
> or a secrets manager instead.
