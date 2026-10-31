# Data Quality Diagnostics & Troubleshooting Playbook

This playbook provides step-by-step diagnostic procedures for investigating,
isolating, and resolving data quality check failures and pipeline alerts.

---

## 1. Incident Diagnosis Flowchart

```text
[Pipeline Alert (WARN/FAIL)]
           │
           ▼
[Check JSON Execution Report (reports/validation_report.json)]
           │
     ┌─────┴──────────────────┐
     ▼                        ▼
[Null Check Breach]      [Duplicate Key Collision]
     │                        │
     ▼                        ▼
Query Offending Rows     Identify Colliding Key Values
(COUNT(*) WHERE col IS NULL) (GROUP BY pk HAVING COUNT(*) > 1)
     │                        │
     ▼                        ▼
Classify Source Root Cause: Producer Bug / Extract Filter / Network Drop
```

---

## 2. Step-by-Step Diagnostic Procedures

### Step 1: Inspect the Failure Report

Review the generated JSON report to identify which check failed:

```bash
cat reports/validation_report.json | jq '.failed_checks[]'
```

Key attributes to inspect:
- `check_name`: The failing validation unit (e.g. `null_checks`).
- `message`: Diagnostic description including violating counts and percentages.
- `metrics`: Raw numerical counts of inspected rows and observed violations.

---

### Step 2: Reproduce the Failure Locally

Run the validation CLI with verbose debug logging:

```bash
python scripts/run_validation.py \
    --data tests/fixtures/null_anomaly.json \
    --config src/config/validator_config.yaml \
    -v
```

---

### Step 3: SQL Forensics

For in-warehouse check failures, execute direct diagnostic queries:

#### Isolating Null Value Spikes:
```sql
SELECT
    COUNT(*) AS total_rows,
    SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END) AS null_emails,
    ROUND(1.0 * SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END) / COUNT(*), 4) AS null_fraction
FROM landing_customers;
```

#### Extracting Colliding Duplicate Primary Keys:
```sql
SELECT order_id, COUNT(*) AS duplicate_count
FROM raw_orders
GROUP BY order_id
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC
LIMIT 10;
```

---

## 3. Common Failure Scenarios & Solutions

| Failure Symptom | Likely Cause | Resolution |
|:----------------|:-------------|:-----------|
| Non-nullable column contains nulls | Upstream API returned optional field as null | Verify API schema or adjust non_nullable rule in YAML |
| Primary key collision | Source retry logic duplicated message batch | Apply deduplication window in ingestion worker |
| Schema drift: column missing | Producer renamed column (e.g. `cust_id` -> `customer_id`) | Update mapping alias or rollback producer schema |
| Memory exhaustion during validation | Large dataset loaded entirely into memory | Switch to pure SQL check engine (`sql/checks/`) |
