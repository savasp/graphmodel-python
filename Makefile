.PHONY: help install dev test lint format clean build publish

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install the project dependencies
	uv sync

dev: ## Install development dependencies and project in editable mode
	uv sync --all-extras --dev

test: ## Run tests
	uv run pytest

test-cov: ## Run tests with coverage
	uv run pytest --cov=graph_model --cov-report=html --cov-report=term

lint: ## Run linting
	uv run ruff check .
	uv run mypy graph_model

format: ## Format code
	uv run black .
	uv run isort .
	uv run ruff check --fix .

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: ## Build the package
	uv build

publish: build ## Publish to PyPI
	uv publish

publish-test: build ## Publish to TestPyPI
	uv publish --publish-url https://test.pypi.org/legacy/

lock: ## Update the lock file
	uv lock

upgrade: ## Upgrade all dependencies
	uv lock --upgrade

run-example: ## Run a basic example
	uv run python examples/basic_usage.py

shell: ## Open a shell with the project environment
	uv run python

add: ## Add a new dependency (usage: make add PACKAGE=package_name)
	uv add $(PACKAGE)

add-dev: ## Add a new dev dependency (usage: make add-dev PACKAGE=package_name)
	uv add --dev $(PACKAGE)

remove: ## Remove a dependency (usage: make remove PACKAGE=package_name)
	uv remove $(PACKAGE)

info: ## Show project info
	uv tree
