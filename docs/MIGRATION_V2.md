# Version Migration Guide — Upgrading to Rule Schema v2.0

This guide assists engineering teams in migrating legacy `1.0` validation
rule files and check configurations to the modern `2.0` schema.

---

## 1. Schema Evolution Overview

| Feature | Schema v1.0 | Schema v2.0 |
|:--------|:------------|:------------|
| Null thresholds | `default_null_threshold: 0.05` | Nested under `thresholds.null_limits` |
| Duplicate keys | `uniqueness.primary_key: [col]` | `uniqueness.keys: [[col1], [col2, col3]]` |
| Webhook alerts | `alerting.webhooks[].url` | Secret references: `secret_ref: DQ_WEBHOOK` |
| SQL Templates | Standalone `.sql` files | Unified catalog with warehouse dialect targets |

---

## 2. Breaking Changes & Deprecations

1. **Top-Level `strict_schema` Deprecation:** In v2.0, `strict_schema` is moved
   under `rules.schema_drift.strict: true`.
2. **Environment Variable Naming:** Deprecated `DQ_CHECKS__NULL_CHECK__THRESHOLDS__*`
   in favor of standard `DQ_NULL_THRESHOLD` and `DQ_COLUMN_NULL_<COL>`.
3. **Report Status `ERROR`:** Check failures due to missing data now explicitly emit
   `CheckStatus.ERROR` rather than collapsing into `CheckStatus.FAIL`.

---

## 3. Automated Migration Script

An automated schema migration utility can upgrade your YAML configs:

```bash
python scripts/generate_schema_docs.py --migrate src/config/validator_config.yaml
```
