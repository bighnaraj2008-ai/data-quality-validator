# Data Governance & Compliance Reporting Guide

This guide establishes compliance protocols, data lineage tracking, and audit
trail requirements for `data-quality-validator`.

---

## 1. Compliance Framework Support

- **GDPR / CCPA:** PII masking in validation error messages and telemetry.
- **SOX / BCBS 239:** Immutable audit logging of all quality evaluations.
- **HIPAA:** Ensuring zero patient identifiers leak into alert webhook payloads.

---

## 2. Audit Trail Retention Policy

Every validation run outputs an immutable JSON telemetry record containing:
- Execution timestamp (UTC)
- Dataset SHA256 checksum
- Rule configuration version
- Total passed, warning, and failed assertions

Retain audit logs in an encrypted S3 bucket or audit table for a minimum of
**365 days** to satisfy external audit requirements.
