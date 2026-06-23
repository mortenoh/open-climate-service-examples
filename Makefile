.PHONY: help install install-e2e lint test test-e2e clean

# ==============================================================================
# Venv
# ==============================================================================

UV := $(shell command -v uv 2> /dev/null)
VENV_DIR?=.venv
PYTHON := $(VENV_DIR)/bin/python

# ==============================================================================
# Targets
# ==============================================================================

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  install      Install dependencies (all extras)"
	@echo "  install-e2e  Install the e2e group (full server stack)"
	@echo "  lint         Run linter and type checker"
	@echo "  test         Run tests (excludes e2e)"
	@echo "  test-e2e     Run end-to-end tests (boots a server, downloads data)"
	@echo "  clean        Clean up temporary files"
	@echo ""
	@echo "Run an individual example with:"
	@echo "  uv run python examples/01_discovery/list_datasets.py"

install:
	@echo ">>> Installing dependencies"
	@$(UV) sync --all-extras

install-e2e:
	@echo ">>> Installing e2e group (full server stack)"
	@$(UV) sync --all-extras --group e2e

lint:
	@echo ">>> Running linter"
	@$(UV) run ruff format .
	@$(UV) run ruff check . --fix
	@echo ">>> Running type checker"
	@$(UV) run mypy --explicit-package-bases src tests examples
	@$(UV) run pyright

test:
	@echo ">>> Running tests (excluding e2e)"
	@$(UV) run pytest -q -m "not e2e"

test-e2e:
	@echo ">>> Running end-to-end tests (boots a server and downloads data)"
	@$(UV) run pytest -v -m e2e

clean:
	@echo ">>> Cleaning up"
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf dist build *.egg-info .pyright

# ==============================================================================
# Default
# ==============================================================================

.DEFAULT_GOAL := help
