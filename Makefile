.PHONY: help install install-dev test test-cov lint format type-check clean build upload pre-commit run debug

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package
	pip install -e .

install-dev:  ## Install development dependencies
	pip install -e ".[dev]"
	pre-commit install

test:  ## Run tests
	pytest

test-cov:  ## Run tests with coverage
	pytest --cov=common_tool_mcp_server --cov-report=html --cov-report=term-missing

lint:  ## Run all linting tools
	flake8 common_tool_mcp_server tests
	black --check common_tool_mcp_server tests
	isort --check-only common_tool_mcp_server tests

format:  ## Format code
	black common_tool_mcp_server tests
	isort common_tool_mcp_server tests

type-check:  ## Run type checking
	mypy common_tool_mcp_server

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build distribution packages
	python -m build

upload:  ## Upload to PyPI (requires proper credentials)
	python -m twine upload dist/*

pre-commit:  ## Run pre-commit hooks on all files
	pre-commit run --all-files

run:  ## Run the MCP server
	python -m common_tool_mcp_server.main

debug:  ## Run the MCP server with debug logging
	python -m common_tool_mcp_server.main --log-level DEBUG

check: lint type-check test  ## Run all checks

all: clean install-dev check  ## Run full development setup 