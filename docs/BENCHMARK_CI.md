# CI Runner Performance Benchmark Tracking Guide

Monitoring workflow duration keeps developer feedback cycles fast across the
multi-version matrix.

---

## 1. Workflow Execution Targets

| Workflow | Runner OS | Target Duration | Notes |
|:---------|:----------|:---------------:|:------|
| `ci_validation.yml` | `ubuntu-latest` | `< 60s` per matrix job | Uses `cache: "pip"` for fast setup |
| `sql_lint.yml` | `ubuntu-latest` | `< 25s` | Lightweight SQLFluff install only |
| `docs_check.yml` | `ubuntu-latest` | `< 20s` | Stdlib Python link verification |
| `security_scan.yml` | `ubuntu-latest` | `< 45s` | Bandit + pip-audit + secret grep |
| `dependency_check.yml` | `ubuntu-latest` | `< 30s` | Dependency tree validation (`pip check`) |

---

## 2. Tracking Regression in Pull Requests

Compare `pytest tests/ --durations=10` logs in CI job output whenever new
stress or performance fixtures are added to ensure suite runtime remains bounded.
