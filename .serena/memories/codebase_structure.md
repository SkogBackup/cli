# Codebase Structure

## Project Root
- `pyproject.toml` - Project configuration, dependencies, build system
- `Makefile` - Development commands and workflows
- `uv.lock` - Dependency lock file
- `README.md` - Project documentation
- `CLAUDE.md` - Claude-specific instructions and context

## Source Code (`src/skogcli/`)
- `__init__.py` - Main CLI app, entry point, subcommand registration
- `memory.py` - Memory module (knowledge management, basic-memory wrapper)
- `settings.py` - Configuration management (config command)
- `script.py` - Script management and execution
- `agent.py` - AI agent management
- `decorators.py` - Utility decorators (error handling, explanations)
- `completion.py` - CLI completion functionality
- `default_settings.py` - Default configuration handling

## Data and Templates (`src/skogcli/data/`)
- `default_settings.json` - Default configuration
- `default_settings_test.json` - Test configuration
- `templates/` - Code templates for script generation
  - `python/` - Python script templates
  - `shell/` - Shell script templates

## Testing (`tests/`)
- `run_tests.sh` - Test runner with environment setup
- `conftest.py` - pytest configuration
- Various test files organized by functionality
- `functional/`, `integration/`, `unit/` - Test organization

## Development Support
- `.skogai/` - SkogAI project folder with context and documentation
- `notes/features/` - Feature development notes
- `tmp/` - Temporary files and evaluation notes
- `todo` - Task tracking
