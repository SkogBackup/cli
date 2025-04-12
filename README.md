# SkogCLI

A demonstration Typer-based CLI tool for the SkogAI project.

## Installation

```bash
# Install development dependencies
uv add pytest && uv lock && uv sync

# Run the CLI
uv run skogcli
```

## Features

### Commands

- `hello`: A simple greeting command
- `version`: Display the current version
- `config`: Manage application settings
- `examples`: Various example commands showcasing Typer features

### Configuration Management

The `config` command allows you to manage application settings:

```bash
# Show current configuration
skogcli config --show

# List available configuration keys and their default values
skogcli config --list-keys

# Set a configuration value
skogcli config --set theme --value dark

# Reset configuration to defaults
skogcli config --reset
```

Configuration is stored in `~/.config/skogcli/config.json`.

## Development

### Running Tests

```bash
# Run all tests
uv run pytest tests/

# Run specific test file
uv run pytest tests/test_config.py

# Run with verbose output
uv run pytest tests/ -v
```

## Best Practices

- Use docstrings for command descriptions
- Use `help` parameter in Arguments and Options for detailed help
- Use `typer.Typer()` with `no_args_is_help=True` for automatic help display
- Create subcommands with `typer.Typer()` and `app.add_typer()`