# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**SkogCLI** is a professional-grade Typer-based CLI tool for the SkogAI project, built with Python 3.12+ and following modern development practices.

- **Architecture**: Modular CLI with subcommands (`memory`, `config`, `script`, `agent`)
- **CLI Entry Points**: `skogcli`, `skog`, `s` (all equivalent)
- **Package Management**: UV (use `uv add <package> && uv lock && uv sync`)
- **Run CLI**: `uv run skogcli`

## Build/Test Commands

### Development Setup
- **Complete setup**: `make dev` (installs dependencies, virtual env, pre-commit hooks)
- **Install dependencies**: `uv add <package> && uv lock && uv sync`
- **Development install**: `make dev-install`

### Testing
- **Run all tests**: `pytest` or `make test`
- **Run specific test**: `pytest tests/test_file.py::test_name`
- **Run with coverage**: `make test-cov`
- **Run tests parallel**: `make test-fast`
- **Verbose output**: `pytest -v`

### Code Quality
- **Format code**: `make format` (Black + Ruff)
- **Lint code**: `make lint` (Ruff)
- **Type check**: `make type-check` (MyPy)
- **Security scan**: `make security` (Bandit + Safety)
- **All checks**: `make all-checks`
- **Pre-commit check**: `make check`

### Documentation
- **Serve docs**: `make docs-serve` (MkDocs at localhost:8000)
- **Build docs**: `make docs-build`
- **Deploy docs**: `make docs-deploy`

## Architecture Overview

### CLI Structure
```
skogcli/
├── __init__.py          # Main app with command registration
├── memory.py            # Knowledge management (wraps basic-memory)
├── settings.py          # Configuration management
├── script.py            # Script generation and templates
├── agent.py             # Agent interaction commands
├── decorators.py        # Custom decorators (@with_explanation)
├── completion.py        # Shell completion functionality
├── monitoring.py        # Optional telemetry/monitoring
└── data/                # Templates and default settings
    ├── default_settings.json
    └── templates/       # Python/shell script templates
```

### Key Commands
- **`memory`**: Knowledge management (`create`, `read`, `search`, `list`, `sync`, `status`)
- **`config`**: Configuration management (`show`, `get`, `set`, `reset`, `list`, `edit`)
- **`script`**: Script generation with templates
- **`agent`**: Agent interaction commands
- **`version`**: Version information

### Configuration System
- **Location**: `~/.config/skogcli/config.json`
- **Sensitive data**: Separate `credentials.json` 
- **Features**: Dot notation, backups, environment variable overrides
- **Environment**: `SKOGAI_CONFIG_DIR`, `SKOGAI_SCRIPTS_DIR`, `SKOGAI_TEMPLATES_DIR`

### Testing Architecture
- **Structure**: `tests/unit/`, `tests/integration/`, `tests/functional/`
- **Framework**: pytest with comprehensive fixtures in `conftest.py`
- **CLI Testing**: Uses `typer.testing.CliRunner`
- **Coverage**: Configured with HTML/XML reports
- **Markers**: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`

## Features

### Core Functionality
- **Memory Module**: Wraps `basic-memory` with enhanced UX (Rich output, pagination)
- **Configuration**: JSON-based with dot notation support
- **Script Templates**: Python/shell script generation
- **Agent Integration**: Command interface for SkogAI agents
- **Shell Completion**: Built-in autocompletion support
- **Help System**: `--helpall` for comprehensive documentation

## Code Style Guidelines

- Use Python type hints consistently
- Follow PEP 8 naming conventions (snake_case for functions/variables)
- Import organization: standard lib → third-party → local
- Error handling: use appropriate exception types and provide context
- Documentation: docstrings for public functions/classes
- Use f-strings for string formatting
- Include appropriate tests for new functionality
- Empty calls to commands should show help (use no_args_is_help=True)

---

# Development Methodology: TDD/DDD

This project follows Test-Driven Development (TDD) and Documentation-Driven Design (DDD) principles. Here are the key guidelines:

1. ALWAYS START BY WRITING TESTS FIRST - This is non-negotiable. No implementation should be written before its corresponding tests.
2. DO NOT MODIFY OR EVEN TOUCH SOURCE CODE without proper test coverage and documentation first.
3. Tests serve as executable specifications and should validate the documented behaviors precisely.
4. Documentation guides the design and implementation - follow the documentation to understand requirements.
5. Any new functionality must be properly documented before implementation begins.

## Development Workflow

1. Document the feature requirements (already done in this file)
2. Write tests that validate the desired behavior (YOU MUST START HERE)
3. Run tests to confirm they fail (red phase)
4. Only then implement the minimal code needed to make tests pass
5. Refactor while maintaining passing tests
6. Repeat for each feature

## Important Notes

- Source code should NOT be modified without corresponding tests
- Documentation is the primary source of truth for requirements
- Tests must match the documented behavior precisely

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

# Rich Integration

- Use Rich for enhanced terminal output
- Create tables with rich.table.Table for structured data display
- Use console.print() for styled output
- Format command output consistently across the application

# Configuration Management

- Implement a config command for managing application settings
- Use --show to display current configuration
- Use --set and --value for modifying configuration
- Include a --reset option to restore defaults
- Store configuration in a standard location (e.g., ~/.config/skogcli/config.json)

# Testing with pytest

- Run tests with `uv run pytest tests/`
- Run specific test files with `uv run pytest tests/test_examples.py`
- Run specific test functions with `uv run pytest tests/test_examples.py::test_examples_basic`
- Use verbose output with `-v` flag: `uv run pytest tests/ -v`
- Use the test runner script: `./tests/run_tests.sh [options]`
- Test Typer CLI apps with `CliRunner` from `typer.testing`
- Verify exit codes and stdout content in assertions
- Tests MUST be written BEFORE any implementation code
- All tests should verify behavior described in documentation

# Memory Module Implementation

## Current Status

The memory module has been implemented with placeholder functionality ("Not implemented yet") for the following commands:

- `create`: Create or update a note in a knowledge base
- `read`: Read a note from the knowledge base
- `search`: Search across the knowledge base
- `list`: List recent activity
- `sync`: Synchronize knowledge files with database
- `status`: Show sync status between files and database

## Implementation Details

The memory module is planned as a wrapper around basic-memory with the following components:

### Command Mapping

| SkogCLI Command | basic-memory Equivalent | Description |
|-----------------|-------------------------|-------------|
| `memory create` | `tool write-note` | Create or update a note with title and folder |
| `memory read` | `tool read-note` | Read a note by identifier with pagination |
| `memory search` | `tool search-notes` | Search across all content with filters |
| `memory list` | `tool recent-activity` | List recent notes/activity with timeframe |
| `memory sync` | `sync` | Sync knowledge files with database |
| `memory status` | `status` | Show sync status |

### Helper Functions

The implementation requires helper functions to interact with basic-memory:

```python
def run_basic_memory(args: List[str]) -> subprocess.CompletedProcess:
    """Run basic-memory with the given arguments."""
    cmd = ["basic-memory"] + args
    return subprocess.run(cmd, capture_output=True, text=True)

def process_markdown(markdown_str: str, raw: bool = False) -> Union[str, Markdown]:
    """Process markdown string for display."""
    if raw:
        return markdown_str
    return Markdown(markdown_str)
```

### Implementation Process

1. Write tests for each command based on documentation (START HERE)
2. Verify tests fail as expected (since only placeholders exist)
3. Implement helper functions with proper test coverage
4. Implement each command with corresponding test validation:
   - `create` command for creating notes with title, folder, content, and optional tags
   - `read` command with support for pagination and raw/formatted display
   - `search` command with filtering options
   - `list` command for recent activity
   - `sync` and `status` commands for database maintenance
5. Update tests as needed to verify actual functionality instead of placeholders

## Dependencies and Integration

### Core Dependencies
- **Typer**: CLI framework with Rich integration
- **Rich**: Terminal formatting and styling
- **Click**: Foundation for Typer (version pinned <8.2.0)
- **LiteLLM**: LLM integration for agent functionality
- **SmoLAgents**: Agent framework integration
- **Tiktoken**: Token counting for LLM operations

### External Tool Integration
- **basic-memory**: Knowledge management backend (called via `uvx basic-memory`)
- **MkDocs**: Documentation site generation
- **Pre-commit**: Code quality automation
- **UV**: Fast Python package management

### Development Dependencies
- **Testing**: pytest, pytest-cov, pytest-xdist, pytest-mock, hypothesis
- **Code Quality**: black, ruff, mypy, bandit, safety
- **Documentation**: mkdocs-material, mkdocstrings
- **Team Tools**: commitizen, semantic-release

## Key Implementation Patterns

### Command Structure
- All commands use `no_args_is_help=True` for consistent help behavior
- Subcommands registered via `app.add_typer()` pattern
- Rich output with `console.print()` and `Table` components
- Custom `--helpall` option for comprehensive documentation

### Error Handling
- Use appropriate exception types with context
- Graceful degradation for missing external tools
- Rich error formatting for user-friendly messages

### Configuration Management
- JSON-based with automatic backup/restore
- Dot notation for nested settings (e.g., `api.key`)
- Environment variable overrides
- Credential separation for security

### Testing Strategy
- Three-tier testing: unit, integration, functional
- Mock external dependencies (basic-memory, file system)
- CLI testing with `typer.testing.CliRunner`
- Property-based testing with Hypothesis for configuration

## Development Workflow Integration

### Pre-commit Hooks
- Code formatting (Black + Ruff)
- Type checking (MyPy)
- Security scanning (Bandit)
- Test execution on changed files

### CI/CD Pipeline
- Quality gates: formatting, linting, type checking, security
- Test execution across test types
- Documentation building and deployment
- Semantic versioning with automated releases

### Team Development
- MkDocs documentation with Material theme
- Structured onboarding process (`make onboard`)
- Team standards and playbooks in dedicated directories
- Comprehensive development tooling via Makefile
