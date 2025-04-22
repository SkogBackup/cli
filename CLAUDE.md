# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

- SkogCLI: A Typer-based CLI tool for the SkogAI project
- Uses Python 3.12+ with Typer for CLI interface
- Package management: UV (uv add, uv lock, uv sync) instead of pip
- Run CLI: `uv run skogcli`

## Build/Test Commands

- Run all tests: `pytest` or `uv run pytest tests/`
- Run a specific test: `pytest tests/test_file.py::test_name`
- Run tests with verbose output: `pytest -v`
- Install dependencies: `uv add <package> && uv lock && uv sync`

## Features

- Configuration management (`config` command)
- Memory module for knowledge management

## Code Style Guidelines

- Use Python type hints consistently
- Follow PEP 8 naming conventions (snake_case for functions/variables)
- Import organization: standard lib → third-party → local
- Error handling: use appropriate exception types and provide context
- Documentation: docstrings for public functions/classes
- Use f-strings for string formatting
- Include appropriate tests for new functionality
- Empty calls to commands should show help (use no_args_is_help=True)
