.PHONY: help install test lint lint-sql smoke clean

help:
	@echo "Available targets:"
	@echo "  install    Install dependencies and package in editable mode"
	@echo "  test       Run unit tests with pytest"
	@echo "  lint       Lint Python source files with flake8"
	@echo "  lint-sql   Lint SQL check templates with sqlfluff"
	@echo "  smoke      Execute pre-flight smoke test script"
	@echo "  clean      Remove cache files and build artifacts"

install:
	pip install --upgrade pip
	pip install -e .
	pip install pytest pyyaml flake8 sqlfluff

test:
	pytest tests/ -v

lint:
	flake8 src tests scripts --count --max-line-length=120 --statistics

lint-sql:
	sqlfluff lint sql/checks/ --dialect ansi

smoke:
	bash scripts/smoke_test.sh

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf *.egg-info build dist
