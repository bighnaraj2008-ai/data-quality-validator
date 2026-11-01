# Frequently Asked Questions — CI/CD & Linter Automation

### Q: Why does `ci_validation.yml` run both `flake8` and `black --check`?
**A:** `black` enforces deterministic code formatting so pull requests remain
focused on logic changes rather than style debates, while `flake8` detects unused
imports, undefined names, and complexity issues.

---

### Q: How can I run the exact same checks locally before pushing?
**A:** Execute `./scripts/run_linter.sh` and `pytest tests/ -v`. Both mirror
the exact command flags executed by GitHub Actions runners.

---

### Q: Why does `.sqlfluff` use `templater = raw` with example identifiers?
**A:** Using ANSI raw parsing guarantees zero external template plugin failures
and fast static analysis inside CI runners, while our integration suite validates
end-to-end execution against SQLite.

---

### Q: How do I clean cached artifacts before running a release package build?
**A:** Run `python scripts/clean_cache.py` to remove `__pycache__/`, `.pytest_cache/`,
`build/`, and `dist/`.
