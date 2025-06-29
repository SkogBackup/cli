# SkogCLI Development Makefile

.PHONY: help install dev-install test lint format type-check security clean build pre-commit all-checks team-setup onboard docs-serve docs-build docs-deploy

# Default target
help:
	@echo "SkogCLI Development Commands:"
	@echo ""
	@echo "Setup:"
	@echo "  install        Install production dependencies"
	@echo "  dev-install    Install development dependencies"
	@echo "  pre-commit     Install pre-commit hooks"
	@echo ""
	@echo "Code Quality:"
	@echo "  format         Format code with Black"
	@echo "  lint           Lint code with Ruff"
	@echo "  type-check     Type check with MyPy"
	@echo "  security       Security scan with Bandit"
	@echo "  all-checks     Run all quality checks"
	@echo ""
	@echo "Testing:"
	@echo "  test           Run tests"
	@echo "  test-cov       Run tests with coverage"
	@echo "  test-fast      Run tests in parallel"
	@echo ""
	@echo "Build:"
	@echo "  build          Build package"
	@echo "  clean          Clean build artifacts"
	@echo ""
	@echo "Development:"
	@echo "  dev            Install + setup development environment"
	@echo "  check          Run all checks before commit"
	@echo ""
	@echo "Team/Documentation:"
	@echo "  team-setup     Set up team development tools"
	@echo "  onboard        Complete team onboarding setup"
	@echo "  docs-serve     Serve documentation locally"
	@echo "  docs-build     Build documentation"
	@echo "  docs-deploy    Deploy documentation to GitHub Pages"

# Setup commands
install:
	uv pip install -e .

dev-install:
	uv venv --seed
	source .venv/bin/activate && uv pip install -e ".[dev,monitoring]"

pre-commit:
	pre-commit install

dev: dev-install pre-commit
	@echo "Development environment ready!"
	@echo "Activate with: source .venv/bin/activate"

# Code quality
format:
	black .
	ruff check . --fix

lint:
	ruff check .

type-check:
	mypy src/

security:
	bandit -r src/
	safety check

all-checks: format lint type-check security
	@echo "All quality checks passed!"

# Testing
test:
	pytest

test-cov:
	pytest --cov=skogcli --cov-report=term-missing --cov-report=html

test-fast:
	pytest -n auto

# Build
build:
	python -m build

clean:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	rm -rf htmlcov/
	rm -f .coverage

# Comprehensive check before commit
check: all-checks test
	@echo "Ready to commit! 🚀"

# CI simulation
ci: clean dev-install all-checks test-cov
	@echo "CI checks complete! ✅"

# Team development commands
team-setup: dev-install
	@echo "Setting up team development environment..."
	pre-commit install
	@echo "Team setup complete! 🚀"

onboard: team-setup
	@echo "🎉 Welcome to the SkogCLI team!"
	@echo ""
	@echo "✅ Development environment ready"
	@echo "✅ Pre-commit hooks installed"
	@echo "✅ Documentation available at: http://localhost:8000"
	@echo ""
	@echo "Next steps:"
	@echo "1. Read ONBOARDING.md for detailed getting started guide"
	@echo "2. Read TEAM_STANDARDS.md for coding standards"
	@echo "3. Run 'make test' to verify everything works"
	@echo "4. Start mkdocs server: 'make docs-serve'"
	@echo ""
	@echo "Need help? Ask in team chat or create an issue!"

docs-serve:
	mkdocs serve

docs-build:
	mkdocs build

docs-deploy:
	mkdocs gh-deploy --force