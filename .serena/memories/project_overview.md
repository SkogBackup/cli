# SkogCLI Project Overview

## Purpose
SkogCLI is a Typer-based CLI tool for the SkogAI project that provides:
- Knowledge management capabilities through a memory module
- Configuration management 
- Script management and execution
- AI agent management
- Test-driven development (TDD) and Documentation-driven design (DDD) approach

## Tech Stack
- **Language**: Python 3.12+
- **CLI Framework**: Typer with Rich for enhanced terminal output
- **Package Management**: UV (instead of pip)
- **Testing**: pytest with coverage support
- **Code Quality**: black (formatting), ruff (linting), mypy (type checking), bandit (security)
- **Pre-commit**: Automated code quality checks
- **Dependencies**: LiteLLM, Click, Tiktoken, SmolaAgents

## Entry Points
The CLI provides multiple entry points:
- `skogcli` - Main command
- `skog` - Short alias
- `s` - Shortest alias

## Main Commands
- `memory` - Knowledge management (create, read, search, list, sync, status)
- `config` - Configuration management 
- `script` - Script management and execution
- `agent` - AI agent management
- `version` - Show version information