---
title: SkogCLI Development Guidelines
type: note
permalink: skogcli/skog-cli-development-guidelines
tags:
- '#development'
- '#guidelines'
- '#typer'
- '#pytest'
- '#rich'
- '#configuration'
---

# SkogCLI Development Guidelines

## Running and Package Management
- Run skogcli via `uv run skogcli`
- Use `uv add <package> && uv lock && uv sync` instead of `pip install`
- Empty calls to a command should always return help - use the `no_args_is_help=True` parameter in `typer.Typer()` to enable this behavior

## Typer Best Practices
- Use docstrings for command descriptions
- Use help parameter in Arguments and Options for detailed help
- Use Annotated for type hints with metadata
- Create subcommands with typer.Typer() and app.add_typer()
- Use Enum classes for choice options
- Set context_settings for consistent help behavior

## Rich Integration
- Use Rich for enhanced terminal output
- Create tables with rich.table.Table for structured data display
- Use console.print() for styled output
- Format command output consistently across the application

## Configuration Management
- Implement a config command for managing application settings
- Use --show to display current configuration
- Use --set and --value for modifying configuration
- Include a --reset option to restore defaults
- Store configuration in a standard location (e.g., ~/.config/skogcli/config.json)

## Testing with pytest
- Run tests with `uv run pytest tests/`
- Run specific test files with `uv run pytest tests/test_examples.py`
- Run specific test functions with `uv run pytest tests/test_examples.py::test_examples_basic`
- Use verbose output with `-v` flag: `uv run pytest tests/ -v`
- Use the test runner script: `./tests/run_tests.sh [options]`
- Test Typer CLI apps with `CliRunner` from `typer.testing`
- Verify exit codes and stdout content in assertions