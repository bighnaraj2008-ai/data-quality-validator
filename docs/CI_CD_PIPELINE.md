# CI/CD Pipeline — Data Quality Validator

This document describes the automated CI/CD pipeline, linting standards, and
build matrix configuration for the `data-quality-validator` project.

## Pipeline Overview

The pipeline is defined by GitHub Actions workflows in `.github/workflows/`:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci_validation.yml` | push / PR to `main` | Build + test matrix across Python 3.9–3.12; runs flake8, black, sqlfluff and pytest |
| `sql_lint.yml` | push / PR to `main` | Standalone SQLFluff linting of `sql/checks/` on every pull request |
| `release_package.yml` | push tag `v*` | Builds wheel + sdist, runs pre-release gate, publishes to PyPI (when `PYPI_API_TOKEN` is set) and creates a GitHub Release with a validation bundle |

A typical PR flow is:

```
push / pull request
    │
    ├── ci_validation.yml  (build + test matrix)
    └── sql_lint.yml       (SQLFluff lint gate)
```

On a tagged commit (`git tag v0.1.0 && git push --tags`):

```
release_package.yml  (lint+test gate → build → PyPI publish → GitHub Release)
```

## Linting Standards

### Python — flake8 + black

Configuration lives in `pyproject.toml` under `[tool.flake8]` and `[tool.black]`.

- **black**: `line-length = 120`, targets py39–py312, applied to `src`, `tests`, `scripts`.
- **flake8**: `max-line-length = 120`, `extend-ignore = E203, W503` (compatible with black), `tests/*` ignores `E501`.
- Excluded from both: `venv`, `.venv`, `__pycache__`, `.pytest_cache`, `build`, `dist`, `.git`, `.eggs`.

Run locally:

```bash
./scripts/run_linter.sh        # flake8 + black --check + sqlfluff
./scripts/check_formatting.sh  # preview formatting changes
```

Or via the Makefile:

```bash
make lint      # flake8
make lint-sql  # sqlfluff
```

### SQL — SQLFluff

Configuration lives in `.sqlfluff`.

- Dialect: `ansi`, templater: `raw`, `max_line_length = 100`, 4-space indentation, trailing commas, keywords `UPPER` / identifiers `lower` / functions `UPPER`.
- Strict rules enforced: layout (`LT*`), core (`L*`), aliasing (`AL*`), join structure (`ST*`), terminators (`CV*`).
- `RF02` (qualification), `ST06` (column order), `AM03` (order-by direction) and `RF04` (keyword identifiers) are excluded because they impose semantic requirements impractical for parameterised check templates.

The SQL check templates in `sql/checks/` use example identifier values so they parse as valid ANSI SQL; runtime parameter substitution is applied outside of sqlfluff.

Run locally:

```bash
sqlfluff lint sql/checks/ --dialect ansi
```
