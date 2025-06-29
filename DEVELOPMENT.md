# SkogCLI Development Guide

## Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd cli

# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv pip install -e ".[dev,monitoring]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Start developing!
```

## Development Environment

This project uses a comprehensive development setup with:

- **Python 3.12** as the target version
- **UV** for fast dependency management
- **Ruff** for linting and import sorting  
- **Black** for code formatting
- **MyPy** for type checking
- **Pytest** for testing with coverage
- **Pre-commit** for automated quality checks
- **GitHub Actions** for CI/CD

## Code Quality Tools

### Formatting and Linting

```bash
# Format code
black .

# Lint and fix issues
ruff check . --fix

# Type checking
mypy src/

# Security scanning
bandit -r src/

# Run all pre-commit hooks
pre-commit run --all-files
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=skogcli --cov-report=html

# Run specific test file
pytest tests/test_specific.py -v

# Run tests in parallel
pytest -n auto
```

## Project Structure

```
├── src/skogcli/           # Main package
│   ├── __init__.py
│   ├── monitoring.py      # Logging and metrics
│   └── ...
├── tests/                 # Test files
├── .github/workflows/     # CI/CD pipelines
├── .vscode/              # VS Code configuration
├── docs/                 # Documentation
├── pyproject.toml        # Project configuration
└── .pre-commit-config.yaml
```

## Development Workflow

### 1. Feature Development

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes
# ... code changes ...

# Run quality checks
pre-commit run --all-files

# Run tests
pytest

# Commit changes (pre-commit hooks run automatically)
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/your-feature-name
```

### 2. Code Review Process

- All changes require PR review
- CI checks must pass (linting, tests, security)
- Code coverage should not decrease
- Documentation should be updated

### 3. Release Process

```bash
# Update version in pyproject.toml
# Create release tag
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions will automatically:
# - Run all tests
# - Build package
# - Create GitHub release
# - Publish to PyPI (if configured)
```

## Configuration Files

### pyproject.toml
- Project metadata and dependencies
- Tool configurations (black, mypy, ruff, pytest)
- Build system setup

### .pre-commit-config.yaml
- Automated code quality checks
- Runs on every commit
- Includes formatting, linting, and testing

### .github/workflows/
- **ci.yml**: Main CI pipeline (lint, test, security)
- **release.yml**: Automated releases and PyPI publishing

## Monitoring and Logging

The project includes structured logging and monitoring:

```python
from skogcli.monitoring import MetricsContext, log_command_execution

# Track command metrics
with MetricsContext("my_command"):
    # Your command logic here
    pass

# Structured logging
log_command_execution("command_name", {"arg1": "value1"})
```

### Environment Variables

```bash
# Copy monitoring configuration
cp monitoring.env.example .env

# Configure as needed
LOG_LEVEL=INFO
SENTRY_DSN=your-sentry-dsn
ENABLE_METRICS=true
```

## VS Code Integration

The project includes comprehensive VS Code configuration:

- **Python debugging** with multiple launch configurations
- **Integrated testing** with pytest
- **Code formatting** on save
- **Recommended extensions** for Python development
- **Task runner** for common operations

### Useful VS Code Tasks

- `Ctrl+Shift+P` → "Tasks: Run Task"
- Install Dependencies
- Run Tests  
- Format Code
- Lint Code
- Type Check
- Security Scan

## Troubleshooting

### Common Issues

**Import errors:**
```bash
# Ensure PYTHONPATH includes src/
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"
```

**Pre-commit failures:**
```bash
# Update hooks
pre-commit autoupdate

# Run manually
pre-commit run --all-files
```

**Test failures:**
```bash
# Run with verbose output
pytest -v -s

# Debug specific test
pytest tests/test_file.py::test_function -v -s
```

### Performance

**Slow tests:**
```bash
# Run tests in parallel
pytest -n auto

# Profile test execution
pytest --durations=10
```

**Slow linting:**
```bash
# Use ruff instead of flake8 (already configured)
ruff check .
```

## Contributing Guidelines

1. **Follow code style** - Black formatting, type hints required
2. **Write tests** - Aim for >90% coverage
3. **Update docs** - Keep documentation current
4. **Security first** - Never commit secrets, use bandit scanning
5. **Performance aware** - Profile changes, use appropriate algorithms

## Resources

- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [Black Code Style](https://black.readthedocs.io/)
- [Ruff Linter](https://docs.astral.sh/ruff/)
- [MyPy Type Checking](https://mypy.readthedocs.io/)

## Getting Help

- Check existing tests for examples
- Review CI logs for detailed error information
- Use VS Code debugging for step-through debugging
- Check the monitoring logs for runtime issues