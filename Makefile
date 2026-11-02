.PHONY: help install test lint format lint-sql benchmark health smoke clean

help:
	@echo "Available targets:"
	@echo "  install    Install dependencies and package in editable mode"
	@echo "  test       Run unit and integration tests with pytest"
	@echo "  lint       Lint Python source files with flake8 and black --check"
	@echo "  format     Auto-format Python and SQL files"
	@echo "  lint-sql   Lint SQL check templates with sqlfluff"
	@echo "  benchmark  Run throughput and memory benchmark harnesses"
	@echo "  health     Verify local runtime environment and warehouse templates"
	@echo "  smoke      Execute pre-flight smoke test script"
	@echo "  clean      Remove cache files and build artifacts"

install:
	python -m pip install --upgrade pip
	pip install -e ".[dev]"
	pip install pytest pyyaml flake8 black sqlfluff

test:
	pytest tests/ -v

lint:
	flake8 src tests scripts --count --max-line-length=120 --statistics
	black --check src tests scripts

format:
	bash scripts/format_code.sh

lint-sql:
	sqlfluff lint sql/checks/ --dialect ansi

benchmark:
	bash scripts/run_benchmarks.sh

health:
	python scripts/health_check.py
	python scripts/validate_warehouse.py

smoke:
	bash scripts/smoke_test.sh

clean:
	python scripts/clean_cache.py
