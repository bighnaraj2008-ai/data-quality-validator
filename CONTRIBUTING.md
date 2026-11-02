# Contributing to Data Quality Validator

Thank you for your interest in improving `data-quality-validator`! We welcome contributions
covering new validation checks, pure SQL check templates, bug fixes, and documentation improvements.

---

## 1. Development Environment Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/bighnaraj2008-ai/data-quality-validator.git
   cd data-quality-validator
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Or .\venv\Scripts\Activate.ps1 on Windows
   pip install -e .
   pip install pytest pyyaml flake8 sqlfluff
   ```

---

## 2. Code Quality & Testing Standards

- **Python Code**: Format according to PEP 8. Verify using `flake8 src tests scripts`.
- **Unit Tests**: Every new checker must include unit tests under `tests/` with at least 90% coverage.
  Run `pytest tests/ -v`.
- **SQL Templates**: Pure SQL checks added to `sql/checks/` must adhere to ANSI SQL syntax.
  Lint using `sqlfluff lint sql/checks/`.
- **Zero Credentials / Private Data**: Never commit `.env`, sensitive credentials, or real customer data.

---

## 3. Pull Request Guidelines

1. Create a descriptive feature branch (`git checkout -b feature/new-check-name`).
2. Write unit tests validating your changes.
3. Run the smoke test: `bash scripts/smoke_test.sh`.
4. Submit a Pull Request targeting the `main` branch with a clear description of the enhancement.

---

## 4. Benchmarking & Release Readiness (`v1.0.0`)

- Run `./scripts/run_linter.sh` (`flake8`, `black --check`, `sqlfluff`) before committing.
- Run `./scripts/run_benchmarks.sh` to verify zero throughput regression.
- Ensure all Markdown guides pass `python scripts/validate_docs.py`.
