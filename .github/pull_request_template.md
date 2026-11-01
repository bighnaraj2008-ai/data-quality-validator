# Pull Request Summary

Describe the changes included in this pull request and reference related issues.

## Type of Change
- [ ] Bug fix (non-breaking change addressing an issue)
- [ ] New validation rule or SQL check template
- [ ] CI/CD or linter automation improvement
- [ ] Documentation update

## Pre-Merge Verification Checklist
- [ ] Executed `./scripts/run_linter.sh` (`flake8`, `black --check`, `sqlfluff`)
- [ ] Executed `pytest tests/ -v` with 100% pass rate
- [ ] Verified Markdown links with `python scripts/validate_docs.py`
- [ ] Updated `CHANGELOG.md` if user-facing behavior changed
