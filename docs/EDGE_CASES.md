# Edge-Case Handling & Anomaly Triage Playbook

## 1. Edge-Case Classification & Taxonomy

Data quality pipelines encounter unexpected upstream anomalies. The framework categorizes them into four severity tiers:

| Severity | Category | Examples | Default Action |
| :--- | :--- | :--- | :--- |
| **P1 - Critical** | Fatal Data Corruption | Missing primary key, unparseable binary format, schema mismatch | Immediate pipeline rejection; alert oncall |
| **P2 - Error** | Threshold Breach | Null spikes above threshold, primary key duplicates | Mark run as `FAIL`; prevent downstream load |
| **P3 - Warning** | Silent Drift | Upstream added optional column, minor latency | Mark run as `WARN`; log metric for review |
| **P4 - Info** | Boundary Fluctuation | Row count within acceptable ±5% standard deviation | Record in audit logs |

## 2. Failure Recovery Runbooks

### Playbook 1: Schema Drift Detected
1. **Identify Missing Columns**: Inspect the `missing` array in the `schema_drift` check result.
2. **Review Upstream Migrations**: Check whether an upstream schema change was deployed without synchronizing `BaselineSchema`.
3. **Remediation**:
   - If the column was deprecated, update `BaselineSchema` columns.
   - If upstream bug dropped the column, re-trigger the ingestion pipeline.

### Playbook 2: Null Rate Surge
1. **Isolate Affected Columns**: Inspect `null_fractions` in the `null_distribution` check result.
2. **Determine Scope**: Is the surge localized to a single supplier or ETL source partition?
3. **Remediation**:
   - Quarantine anomalous partition to staging dead-letter queue.
   - Notify source engineering team with offended record samples.

### Playbook 3: Primary Key Collisions
1. **Retrieve Collision Sample**: Review `offending_sample` in `duplicate_keys` result.
2. **Root Cause Analysis**: Check whether upstream CDC (Change Data Capture) produced un-deduplicated replay streams.
3. **Remediation**: Run deduplication pass utilizing most recent `created_at` timestamp.
