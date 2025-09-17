#!/usr/bin/env bash

set -e

# @describe SkogCLI src commands
# @meta version 1.0.0
# @meta dotenv .env

# @cmd
# @arg args~  Capture all remaining args
run() {
  uv run skogcli "${argc_args[@]}"
}

# @cmd Install dependencies
# @flag --dev install development dependencies
install() {
  if [[ -n "$argc_dev" ]]; then
    uv sync --group dev
  else
    uv sync
  fi
}

# @cmd Build the package
build() {
  uv build
}

# @cmd Clean build artifacts and cache
clean() {
  echo "todo"
  # rm -rf dist/ build/ *.egg-info/ .pytest_cache/ htmlcov/ .coverage .mypy_cache/ .ruff_cache/ bandit-report.json
  # find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
  # find . -name "*.pyc" -delete
}

# @cmd Run tests
test() {
  uv run pytest tests/ --cov=skogcli --cov-report=html --cov-report=term-missing --ignore=tests/integration
}

# @cmd Format code
format() {
  :
}

# @cmd Run ruff checks
format::ruff() {
  uv run ruff check src tests
}

# @cmd Run black checks
format::black() {
  uv run black src tests
}

# @cmd Run type checking with mypy
format::mypy() {
  uv run mypy src tests
}

# @cmd Run pre-commit hooks
pre-commit() {
  uv run pre-commit
}

eval "$(argc --argc-eval "$0" "$@")"
