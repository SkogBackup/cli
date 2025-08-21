# Suggested Commands for SkogCLI Development

## Running the CLI
- `uv run skogcli` - Run the CLI application
- `uv run skogcli --help` - Show help
- `uv run skogcli version` - Show version

## Package Management
- `uv sync` - Install dependencies
- `uv sync --group dev` - Install development dependencies
- `uv add <package> && uv lock && uv sync` - Add new package (instead of pip install)

## Development Commands (via Makefile)
- `make help` - Show all available commands
- `make install` - Install dependencies
- `make dev-install` - Install development dependencies

## Code Quality
- `make format` - Format code with black
- `make lint` - Run linting (black check + ruff)
- `make type-check` - Run type checking with mypy
- `make security` - Run security checks with bandit
- `make all-checks` - Run all quality checks
- `make pre-commit` - Run pre-commit hooks

## Testing
- `make test` - Run tests via ./tests/run_tests.sh -v
- `make test-cov` - Run tests with coverage
- `make test-fast` - Run tests stopping on first failure
- `./tests/run_tests.sh` - Run tests with environment variables
- `uv run pytest tests/` - Run tests directly
- `uv run pytest tests/ -v` - Run tests with verbose output
- `uv run pytest tests/test_file.py::test_name` - Run specific test

## Build and Deploy
- `make build` - Build the package
- `make clean` - Clean build artifacts and cache
- `make ci` - Simulate CI pipeline (all-checks + test)

## System Commands (Linux)
- Standard Linux commands: `git`, `ls`, `grep`, `find`, etc.
- Use `rg` (ripgrep) instead of grep when available
