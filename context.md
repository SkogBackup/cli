run skogcli via "uv run skogcli"

use "uv add <package> && uv lock && uv sync" instead of "pip install"

empty calls to a command should always return help - use the no_args_is_help=True parameter in typer.Typer() to enable this behavior

# Typer Best Practices
- Use docstrings for command descriptions
- Use help parameter in Arguments and Options for detailed help
- Use Annotated for type hints with metadata
- Create subcommands with typer.Typer() and app.add_typer()
- Use Enum classes for choice options
- Set context_settings for consistent help behavior

# Testing with pytest
- Run tests with `uv run pytest tests/`
- Run specific test files with `uv run pytest tests/test_examples.py`
- Run specific test functions with `uv run pytest tests/test_examples.py::test_examples_basic`
- Use verbose output with `-v` flag: `uv run pytest tests/ -v`
- Use the test runner script: `./tests/run_tests.sh [options]`
- Test Typer CLI apps with `CliRunner` from `typer.testing`
- Verify exit codes and stdout content in assertions
