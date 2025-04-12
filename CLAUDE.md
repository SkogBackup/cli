# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Test Commands
- Run all tests: `pytest`
- Run a specific test: `pytest tests/test_file.py::test_name`
- Run tests with verbose output: `pytest -v`

## Code Style Guidelines
- Use Python type hints consistently
- Follow PEP 8 naming conventions (snake_case for functions/variables)
- Import organization: standard lib → third-party → local
- Error handling: use appropriate exception types and provide context
- Documentation: docstrings for public functions/classes
- Use f-strings for string formatting
- Include appropriate tests for new functionality
