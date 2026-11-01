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

## Build Matrix Configuration

`ci_validation.yml` uses a `fail-fast: false` matrix:

```yaml
python-version: ["3.9", "3.10", "3.11", "3.12"]
runs-on: ubuntu-latest
```

Each matrix job:

1. Checks out the repository.
2. Sets up Python (with pip caching).
3. Installs the package in editable mode with dev extras (`pip install -e ".[dev]"`), plus `flake8`, `black`, `sqlfluff`, `pytest`, `pytest-cov`.
4. Lints Python with flake8.
5. Checks Python formatting with black (`--check`).
6. Lints SQL check templates with sqlfluff.
7. Runs the pytest suite (JUnit XML + coverage).
8. Uploads test results and coverage as artifacts.

`pyproject.toml` declares `requires-python = ">=3.9"` to match the matrix.

## Release Process

1. Bump the version (e.g. in `pyproject.toml`) and update `CHANGELOG.md`.
2. Create and push an annotated tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

3. `release_package.yml` runs:
   - Pre-release gate: flake8, black --check, sqlfluff, pytest.
   - `python -m build` → `dist/*.whl` + `dist/*.tar.gz`.
   - A validation bundle (`validation-bundle.zip`) containing `sql/checks/`, `README.md`, `LICENSE` and a test report.
   - Uploads `dist/` and the bundle as workflow artifacts.
   - Publishes to PyPI only when the `PYPI_API_TOKEN` repository secret is set (guarded so PRs/forks cannot deploy).
   - Creates a GitHub Release attaching the wheels/sdist and the validation bundle.

## Local Developer Workflow

```bash
# 1. Create / activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# 2. Install the package and dev dependencies
pip install -e ".[dev]"
pip install flake8 black sqlfluff pytest

# 3. Run the full local lint + test check
./scripts/run_linter.sh
pytest tests/ -v

# 4. (Optional) Preview formatting changes without enforcing
./scripts/check_formatting.sh
```

## Repository Hygiene

The following must never be committed or tracked (enforced by `.gitignore`):

- Build artifacts: `build/`, `dist/`, `*.egg-info/`, `*.egg`, `sdist/`, `wheels/`
- Virtual environments: `venv/`, `.venv/`, `env/`
- Cache files: `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.coverage`, `htmlcov/`
- Local logs: `*.log`, `reports/`, `output/`
- Editor / IDE configs: `.vscode/`, `.idea/`, `.antigravity/`, `.cursor/`, `.claude/`

## CI Artifacts

- `test-results-py<version>` — JUnit XML per Python version.
- `coverage-py<version>` — coverage XML per Python version.
- `release-dist` — wheel + sdist from `python -m build`.
- `validation-bundle.zip` — SQL check templates + docs + test report for release auditing.
