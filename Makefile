# Makefile for Google Photos Manager

# Virtual environment path
VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
RUFF = $(VENV)/bin/ruff
BLACK = $(VENV)/bin/black
MYPY = $(VENV)/bin/mypy
PYTEST = $(VENV)/bin/pytest
PRECOMMIT = $(VENV)/bin/pre-commit

.PHONY: help install install-dev test test-cov lint format type-check clean docs serve-docs build publish

# Default target
help:
	@echo "Available targets:"
	@echo "  install      Install the package in development mode"
	@echo "  install-dev  Install with development dependencies"
	@echo "  test         Run tests"
	@echo "  test-cov     Run tests with coverage report"
	@echo "  lint         Run linting checks"
	@echo "  format       Format code with black and ruff"
	@echo "  pre-commit   Run pre-commit hooks"
	@echo "  clean        Clean build artifacts"
	@echo "  docs         Build documentation"
	@echo "  serve-docs   Serve documentation locally"
	@echo "  build        Build package"
	@echo "  publish      Publish to PyPI"

# Installation targets
install:
	$(PIP) install -e .

install-dev:
	$(PIP) install -e ".[dev]"

# Testing targets
test:
	$(PYTEST) tests/

test-cov:
	$(PYTEST) tests/ --cov=photo_manager --cov-report=html --cov-report=term-missing

# Code quality targets
lint:
	$(RUFF) check photo_manager/ tests/
	$(BLACK) --check photo_manager/ tests/

format:
	$(BLACK) photo_manager/ tests/
	$(RUFF) check --fix photo_manager/ tests/

pre-commit:
	$(PRECOMMIT) run --all-files

# Maintenance targets
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Documentation targets
docs:
	mkdocs build

serve-docs:
	mkdocs serve

# Build and publish targets
build: clean
	$(PYTHON) -m build

publish: build
	twine upload dist/*

# Development setup
setup-dev: install-dev
	$(PRECOMMIT) install
	$(PRECOMMIT) autoupdate
