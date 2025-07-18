# Makefile for skogcli project
.PHONY: help install dev-install pre-commit format lint type-check security all-checks test test-cov test-fast build clean check ci

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Tool availability checks
CHECK_UV := $(shell command -v uv 2> /dev/null)
CHECK_BLACK := $(shell uv run black --version 2> /dev/null)
CHECK_MYPY := $(shell uv run mypy --version 2> /dev/null)
CHECK_RUFF := $(shell uv run ruff --version 2> /dev/null)
CHECK_BANDIT := $(shell uv run bandit --version 2> /dev/null)

define check_tool
	@if [ -z "$(1)" ]; then \
		echo "$(RED)Error: $(2) not found. Run 'make dev-install' first.$(NC)"; \
		exit 1; \
	fi
endef

help: ## Show this help message
	@echo "$(GREEN)Available commands:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install dependencies
	@echo "$(GREEN)Installing dependencies...$(NC)"
	uv sync

dev-install: ## Install development dependencies
	@echo "$(GREEN)Installing development dependencies...$(NC)"
	uv sync --group dev

pre-commit: ## Run pre-commit hooks
	@echo "$(GREEN)Running pre-commit hooks...$(NC)"
	uv run pre-commit run --all-files

format: ## Format code
	@echo "$(GREEN)Formatting code...$(NC)"
	$(call check_tool,$(CHECK_BLACK),black)
	uv run black src/ tests/

lint: ## Run linting
	@echo "$(GREEN)Running linting...$(NC)"
	$(call check_tool,$(CHECK_BLACK),black)
	uv run black --check src/ tests/
	@if [ -n "$(CHECK_RUFF)" ]; then \
		echo "$(GREEN)Running ruff...$(NC)"; \
		uv run ruff check src/ tests/ || echo "$(YELLOW)Ruff found issues$(NC)"; \
	else \
		echo "$(YELLOW)Ruff not available, skipping...$(NC)"; \
	fi

type-check: ## Run type checking
	@echo "$(GREEN)Running type checking...$(NC)"
	@if [ -n "$(CHECK_MYPY)" ]; then \
		echo "$(GREEN)Running mypy...$(NC)"; \
		uv run mypy src/ --ignore-missing-imports --no-error-summary || echo "$(YELLOW)Type checking found issues$(NC)"; \
	else \
		echo "$(YELLOW)MyPy not available, run 'make dev-install' first$(NC)"; \
	fi

security: ## Run security checks
	@echo "$(GREEN)Running security checks...$(NC)"
	@if [ -n "$(CHECK_BANDIT)" ]; then \
		echo "$(GREEN)Running bandit...$(NC)"; \
		uv run bandit -r src/ -f json -o bandit-report.json || echo "$(YELLOW)Security scan found issues$(NC)"; \
	else \
		echo "$(YELLOW)Bandit not available, run 'make dev-install' first$(NC)"; \
	fi

all-checks: lint type-check security ## Run all checks
	@echo "$(GREEN)All checks completed!$(NC)"

test: ## Run tests
	@echo "$(GREEN)Running tests...$(NC)"
	uv run pytest tests/ -v

test-cov: ## Run tests with coverage
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	uv run pytest tests/ --cov=skogcli --cov-report=html --cov-report=term-missing

test-fast: ## Run fast tests (stop on first failure)
	@echo "$(GREEN)Running fast tests...$(NC)"
	uv run pytest tests/ -x

build: ## Build the package
	@echo "$(GREEN)Building package...$(NC)"
	uv build

clean: ## Clean build artifacts and cache
	@echo "$(GREEN)Cleaning build artifacts...$(NC)"
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf bandit-report.json
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete

check: pre-commit ## Run pre-commit checks
	@echo "$(GREEN)Pre-commit checks completed!$(NC)"

ci: all-checks test ## Simulate CI pipeline
	@echo "$(GREEN)CI pipeline simulation completed!$(NC)"
