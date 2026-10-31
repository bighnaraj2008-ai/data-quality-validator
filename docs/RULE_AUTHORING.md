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
