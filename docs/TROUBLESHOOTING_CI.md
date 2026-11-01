# Troubleshooting Guide — CI/CD Validation Builds

This guide covers common failures encountered in GitHub Actions CI workflows
and how to diagnose and resolve them locally.

---

## 1. Black Formatting Failures (`black --check`)

**Symptom:** `ci_validation.yml` fails during `Check Python Formatting with Black`
with `would reformat <file>`.

**Resolution:**

```bash
python -m black src tests scripts
```

Or execute `./scripts/format_code.sh` and commit the reformatted files.

---

## 2. Flake8 Style Violations

**Symptom:** `flake8` reports `F401 imported but unused` or `E501 line too long`.

**Resolution:**

```bash
python -m flake8 src tests scripts --count --max-line-length=120 --statistics
```

Remove unused imports or break lines longer than 120 characters.

---

## 3. SQLFluff Lint Errors

**Symptom:** `sql_lint.yml` fails on a modified query under `sql/checks/`.

**Resolution:**

```bash
python -m sqlfluff lint sql/checks/ --dialect ansi
python -m sqlfluff fix sql/checks/ --dialect ansi
```

Ensure keywords are `UPPER`, identifiers are `lower`, and trailing commas are used.

---

## 4. Python 3.9 Compatibility Errors

**Symptom:** `TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'`
on Python 3.9 matrix jobs.

**Resolution:** Add `from __future__ import annotations` at the top of any module
using PEP 585/604 union syntax or generic collections.
