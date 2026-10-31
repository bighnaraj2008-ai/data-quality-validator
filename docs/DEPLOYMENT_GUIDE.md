# Production Deployment & Scheduling Runbook

This runbook outlines deployment patterns, containerization strategies, and
orchestration patterns for `data-quality-validator` across enterprise data
engineering pipelines.

---

## 1. Containerization (Docker)

A containerized deployment encapsulates all dependencies, configuration templates,
and Python runtime:

```dockerfile
FROM python:3.11-slim-bullseye

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY sql/ ./sql/
COPY scripts/ ./scripts/
COPY pyproject.toml .

ENTRYPOINT ["python", "scripts/run_validation.py"]
CMD ["--help"]
```

Build and test locally:

```bash
docker build -t data-quality-validator:latest .
docker run --rm -v $(pwd)/data:/data data-quality-validator:latest \
    --data /data/ingest.csv \
    --config /app/src/config/validator_config.yaml
```

---

## 2. Kubernetes CronJob Manifest

Run periodic validation on batch ingestion landed in object storage:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: dq-validator-nightly
  namespace: data-platform
spec:
  schedule: "0 2 * * *"  # Daily at 02:00 UTC
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 5
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: validator
              image: data-quality-validator:latest
              command:
                - python
                - scripts/run_validation.py
                - --data
                - /mnt/storage/landing/orders.csv
                - --config
                - /app/src/config/validator_config.yaml
              env:
                - name: DQ_NULL_THRESHOLD
                  value: "0.02"
                - name: DQ_SLACK_WEBHOOK_URL
                  valueFrom:
                    secretKeyRef:
                      name: dq-secrets
                      key: slack-webhook-url
              resources:
                requests:
                  memory: "512Mi"
                  cpu: "500m"
                limits:
                  memory: "2Gi"
                  cpu: "2000m"
```

---

## 3. Apache Airflow DAG Integration

Integrate validation as an upstream quality gate before downstream transformation:

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "data-engineering",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="orders_ingest_and_validate",
    start_date=datetime(2026, 10, 1),
    schedule_interval="@hourly",
    catchup=False,
    default_args=default_args,
) as dag:

    validate_gate = BashOperator(
        task_id="run_data_quality_gate",
        bash_command="""
        python /opt/dq/scripts/run_validation.py \
            --data /data/landing/orders_{{ ds_nodash }}.csv \
            --config /opt/dq/src/config/validator_config.yaml
        """,
    )

    transform = BashOperator(
        task_id="dbt_run_orders",
        bash_command="dbt run --select orders",
    )

    validate_gate >> transform
```

---

## 4. Resource Sizing Recommendations

| Dataset Volume | Recommended RAM | CPU Allocation | Ingestion Mode |
|:---------------|:----------------|:---------------|:---------------|
| < 100K rows    | 512 MB          | 0.5 vCPU       | In-Memory Pandas |
| 100K - 1M rows | 2 GB            | 2.0 vCPU       | In-Memory PyArrow |
| > 1M rows      | 1 GB (client)   | 1.0 vCPU       | In-Warehouse Pure SQL |
