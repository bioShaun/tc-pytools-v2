.PHONY: help install test lint format type-check ci clean

help:  ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies with uv
	uv sync

test:  ## Run tests
	uv run pytest -v

test-cov:  ## Run tests with coverage
	uv run pytest --cov=gtf --cov-report=term-missing --cov-report=html

lint:  ## Run linter
	uv run ruff check .

lint-fix:  ## Run linter and fix issues
	uv run ruff check --fix .

format:  ## Format code
	uv run ruff format .

format-check:  ## Check code formatting
	uv run ruff format --check .

type-check:  ## Run type checker
	uv run mypy gtf --ignore-missing-imports

ci:  ## Run local CI checks
	./ci.sh

pre-commit-install:  ## Install pre-commit hooks
	uv run pre-commit install

pre-commit-run:  ## Run pre-commit on all files
	uv run pre-commit run --all-files

clean:  ## Clean build artifacts and cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build package
	uv build

run:  ## Run the main script (example usage)
	@echo "Usage: uv run rename-ngdc-genome-id -f <fasta> -o <output> [-g <gff> -og <output_gff>]"
