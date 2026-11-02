# Quality Report Archiving & Retention Policy

This policy governs the export, compression, rotation, and long-term retention of
`data-quality-validator` telemetry payloads.

---

## 1. Failure Extraction & Archival
Use [`scripts/export_reports.py`](../scripts/export_reports.py) after each batch run
to extract failing checks (`FAIL`, `ERROR`) into structured CSV/JSON archives while
relocating raw execution files to a processed staging directory.

```bash
python scripts/export_reports.py \
    --input reports/ \
    --output archives/daily_failures.json \
    --format json \
    --archive-dir reports/processed
```

---

## 2. Log Rotation & Retention Tiers

| Tier | Retention Window | Enforcement Utility |
|:-----|:-----------------|:--------------------|
| Hot Telemetry (`reports/`) | 30 days / min 10 latest | `scripts/prune_reports.py` |
| Failure Archives (`archives/`) | 365 days (cold object store) | S3 / GCS Lifecycle Rules |

Always execute `scripts/prune_reports.py --dry-run` before modifying production
retention schedules.
