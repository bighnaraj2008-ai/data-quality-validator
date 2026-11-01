# Version Release & Tagging Runbook

This document defines the release workflow for publishing tagged builds of
`data-quality-validator` using GitHub Actions.

---

## 1. Pre-Release Checklist

1. Run local static analysis and formatting checks:
   ```bash
   ./scripts/run_linter.sh
   ```
2. Run full test and documentation checks:
   ```bash
   pytest tests/ -v
   python scripts/validate_docs.py
   ```
3. Verify repository hygiene (`git ls-files` contains zero hidden/cache files).

---

## 2. Bumping Version & Changelog

1. Bump the package version cleanly in [`pyproject.toml`](../pyproject.toml):
   ```bash
   ./scripts/bump_version.sh 0.2.0
   ```
2. Move `[Unreleased]` entries in [`CHANGELOG.md`](../CHANGELOG.md) under the new
   version header with ISO date `YYYY-MM-DD`.
3. Commit the release preparation changes cleanly.

---

## 3. Tagging & Automated Publishing

Create and push an annotated Git tag matching `v*`:

```bash
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0
```

Pushing a `v*` tag automatically triggers [`.github/workflows/release_package.yml`](../.github/workflows/release_package.yml),
which runs the pre-release lint + pytest gate, builds wheel/sdist artifacts,
packages the SQL check bundle, and publishes a GitHub Release.
