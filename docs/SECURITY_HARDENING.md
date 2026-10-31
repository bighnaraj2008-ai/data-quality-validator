# Database Credential & Connection Security Hardening Guide

This document establishes security requirements and best practices for
deploying `data-quality-validator` in enterprise environments.

---

## 1. Credential Management & Zero Secrets in Source

1. **Never commit credentials:** Database passwords, tokens, API keys, and webhook
   URLs must never be written to Git repositories or committed YAML files.
2. **Environment Variable Injection:** Use `DQ_*` environment variables to inject
   connection strings and secrets at container startup:
   ```bash
   export DQ_DATABASE_URL="postgresql://dq_runner:${DB_PASSWORD}@warehouse.internal:5432/analytics"
   ```
3. **Secret Stores:** Fetch credentials from cloud secret managers (AWS Secrets
   Manager, HashiCorp Vault, Azure Key Vault) at container launch.

---

## 2. Principle of Least Privilege (Database Roles)

The SQL check engine requires strictly **READ-ONLY** database permissions. Never
run validation jobs under administrative or DDL-capable roles.

### PostgreSQL Read-Only Role Definition:
```sql
CREATE ROLE dq_inspector WITH LOGIN PASSWORD 'strong_random_password';

-- Grant connection and schema read access
GRANT CONNECT ON DATABASE analytics TO dq_inspector;
GRANT USAGE ON SCHEMA public TO dq_inspector;

-- Grant select-only access to audited tables
GRANT SELECT ON ALL TABLES IN SCHEMA public TO dq_inspector;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO dq_inspector;
```

---

## 3. SQL Injection Prevention

All pure SQL checks under `sql/checks/` use parameterized binding:
- Bind variables (`:param_name`) isolate untrusted values.
- Table and column identifiers must be sanitized through an allowlist mapping
  before query template interpolation.

```python
# Safe identifier verification against metadata catalog
def sanitize_identifier(name: str, allowed_columns: set[str]) -> str:
    clean_name = name.strip()
    if clean_name not in allowed_columns:
        raise ValueError(f"Unauthorized table/column identifier: {clean_name}")
    return clean_name
```

---

## 4. Encryption in Transit (TLS)

Enforce TLS 1.3 encryption for all database connections and webhook deliveries:
- Append `?sslmode=verify-full` to PostgreSQL URLs.
- Append `?ssl=true` for Snowflake / BigQuery connections.
- Ensure alert webhooks use HTTPS with valid certificates.
