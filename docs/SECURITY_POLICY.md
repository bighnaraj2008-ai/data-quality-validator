# Security Reporting & Vulnerability Disclosure Policy

We take the security of `data-quality-validator` and its users' data pipelines
seriously.

---

## 1. Supported Versions

| Version | Supported | Security Updates |
|:--------|:---------:|:----------------:|
| `1.x` / `0.5.x` | Yes | Automated scans + patches |
| `< 0.3.0` | No | Upgrade to latest release |

---

## 2. Automated Security Controls

Our CI pipeline continuously enforces:
- **Bandit Static Analysis**: Scans Python modules under `src/` and `scripts/`
  via [`.github/workflows/security_scan.yml`](../.github/workflows/security_scan.yml).
- **GitHub CodeQL**: Semantic data-flow vulnerability scanning via
  [`.github/workflows/code_ql.yml`](../.github/workflows/code_ql.yml).
- **Secret Prevention**: Regex scanning and strict `.gitignore` enforcement
  preventing accidental `.env` or token commits.

---

## 3. Reporting a Vulnerability

If you discover a security vulnerability, please **do not** open a public issue.
Instead:
1. Review [`SECURITY.md`](../SECURITY.md) for private disclosure contacts.
2. Provide reproduction steps, affected version, and potential impact.
3. Expect acknowledgment within 48 hours and a remediation timeline once triaged.
