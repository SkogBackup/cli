#!/usr/bin/env bash

set -e

# @describe SkogCLI src commands
# @meta version 1.0.0
# @meta dotenv .env
# @env LLM_OUTPUT=/dev/stdout The output path

# @cmd
# @arg args~  Capture all remaining args
run() {
  uv run skogcli "${argc_args[@]}"
}

# @cmd Install dependencies
install() {
  uv sync
}

# @cmd Install development dependencies
install::dev() {
  uv sync --group dev
}

# @cmd Build the package
build() {
  uv build
}

# @cmd Clean build artifacts and cache
clean() {
  rm -rf dist/ build/ *.egg-info/ .pytest_cache/ htmlcov/ .coverage .mypy_cache/ .ruff_cache/ bandit-report.json
  find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
  find . -name "*.pyc" -delete
}

# @cmd Format code with black
format() {
  uv run black src/ tests/
}

# @cmd Run linting checks
format::lint() {
  uv run black --check src/ tests/
  uv run ruff check src/ tests/
}

# @cmd Run type checking with mypy
format::mypy() {
  uv run mypy src/ --ignore-missing-imports --no-error-summary
}

# @cmd Run pre-commit hooks
pre-commit() {
  uv run pre-commit run --all-files
}

eval "$(argc --argc-eval "$0" "$@")"
