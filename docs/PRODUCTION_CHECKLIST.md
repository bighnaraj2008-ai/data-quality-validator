# Production Deployment Readiness Checklist

Verify each control below before promoting a `data-quality-validator` pipeline
into production scheduling.

---

## 1. Configuration & Credentials
- [ ] All secrets (`DQ_SLACK_WEBHOOK_URL`, warehouse credentials) injected via
  environment variables or cloud secret stores; zero `.env` files committed.
- [ ] `src/config/validator_config.yaml` thresholds match business SLA bounds.
- [ ] Database accounts restricted to strictly **READ-ONLY** permissions.

## 2. CI/CD & Quality Gates
- [ ] `./scripts/run_linter.sh` passes cleanly (`flake8`, `black --check`, `sqlfluff`).
- [ ] Full pytest suite passes across target Python versions (`3.9`-`3.12`).
- [ ] Baseline benchmarks pass minimum `> 10,000 rows/sec` throughput target.

## 3. Observability & Retention
- [ ] Failure reports exported regularly via [`scripts/export_reports.py`](../scripts/export_reports.py).
- [ ] Historical report rotation scheduled via [`scripts/prune_reports.py`](../scripts/prune_reports.py).
- [ ] Incident escalation playbooks accessible to on-call data engineers.
