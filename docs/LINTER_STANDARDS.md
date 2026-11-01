# Python & SQL Coding Standards and Linter Rule Guide

All source code, test suites, automation scripts, and SQL validation templates in
`data-quality-validator` must pass automated static analysis before merging.

---

## 1. Python Standards (`black` + `flake8`)

Configuration is defined centrally in [`pyproject.toml`](../pyproject.toml).

| Tool | Setting | Value | Rationale |
|:-----|:--------|:------|:----------|
| `black` | `line-length` | `120` | Accommodates descriptive check assertions without awkward wrapping |
| `black` | `target-version` | `py39..py312` | Ensures syntax compatibility across the CI build matrix |
| `flake8` | `max-line-length` | `120` | Matches Black line width |
| `flake8` | `extend-ignore` | `E203, W503` | Avoids whitespace-before-colon conflicts with Black slicing |
| `flake8` | `per-file-ignores` | `tests/*: E501` | Permits long string literals in fixture assertions |

### Running Python Linters Locally

```bash
python -m flake8 src tests scripts --count --max-line-length=120 --statistics
python -m black --check src tests scripts
```

To automatically format code:

```bash
./scripts/format_code.sh
```

---

## 2. SQL Standards (`SQLFluff`)

Configuration is maintained in [`.sqlfluff`](../.sqlfluff).

- **Dialect**: `ansi` (compatible with PostgreSQL, Snowflake, DuckDB, SQLite)
- **Templater**: `raw`
- **Indentation**: 4 spaces, trailing commas (`line_position = trailing`)
- **Capitalisation**: Keywords `UPPER`, identifiers `lower`, functions `UPPER`
- **Excluded Rules**: `RF02`, `ST06`, `AM03`, `RF04` (excluded where parameterised
  templates use standalone identifiers)

### Running SQLFluff Locally

```bash
python -m sqlfluff lint sql/checks/ --dialect ansi
```
