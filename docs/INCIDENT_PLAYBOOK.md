# Silent Schema Drift & Quality Alert Incident Playbook

This playbook establishes operational protocols and escalation procedures for
triaging data quality alerts, schema drift breaches, and pipeline circuit breaks.

---

## 1. Incident Severity Classification

| Level | Impact | Description | Response SLA |
|:------|:-------|:------------|:-------------|
| **Sev-1** | Critical | Primary key collision or corrupted financial metrics in production table | < 15 minutes |
| **Sev-2** | Major | Non-nullable constraint failure blocking ETL batch pipeline | < 1 hour |
| **Sev-3** | Moderate | Silent schema drift (new unmapped columns) or moderate null rate spike | < 4 hours |
| **Sev-4** | Minor | Warning threshold reached on non-critical historical column | Next business day |

---

## 2. Immediate Containment Checklist

When an alert fires via Slack or Teams:

1. **Acknowledge Alert:** Post acknowledgment in incident channel `#data-incidents`.
2. **Verify Circuit Breaker:** Confirm downstream transformation tasks were halted
   by the validator's non-zero exit code (`exit 1`).
3. **Capture Audit Payload:** Preserve `reports/validation_report.json` for post-mortem forensics.
4. **Isolate Raw Files:** Quarantine failed landing files to prevent downstream reprocessing:
   ```bash
   aws s3 mv s3://data-lake/landing/orders_20261031.csv s3://data-lake/quarantine/
   ```

---

## 3. Root Cause Investigation

- **Upstream Producer Inspection:** Did producer deploy a breaking schema change?
- **Network / Extract Truncation:** Was the file transferred partially (leading to missing columns or row count anomaly)?
- **Data Type Shifts:** Did an upstream float column begin sending string values?

---

## 4. Remediation & Backfill

1. Fix upstream producer or adjust validation rule thresholds if drift is intentional.
2. Re-run validation against quarantined file:
   ```bash
   python scripts/run_validation.py --data /quarantine/orders_20261031.csv --config src/config/validator_config.yaml
   ```
3. Resume downstream pipeline upon clean `PASS` result.
