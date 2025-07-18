# 🤖 SkogCLI

A demonstration Typer-based CLI tool for the SkogAI project.

## 🚀 Installation

```bash
# 📦 Install dependencies
make install

# 🛠️ Install development dependencies
make dev-install

# ▶️ Run the CLI
uv run skogcli
```

## ✨ Features

### 🎯 Commands

- `hello`: 👋 A simple greeting command
- `version`: 📊 Display the current version
- `config`: ⚙️ Manage application settings
- `examples`: 📚 Various example commands showcasing Typer features

### ⚙️ Configuration Management

The `config` command allows you to manage application settings:

```bash
# 👁️ Show current configuration
skogcli config --show

# 📋 List available configuration keys and their default values
skogcli config --list-keys

# 🔧 Set a configuration value
skogcli config --set theme --value dark

# 🔄 Reset configuration to defaults
skogcli config --reset
```

📁 Configuration is stored in `~/.config/skogcli/config.json`.

## 🛠️ Development

### 🎯 Available Make Commands

```bash
# 📖 View all available commands
make help

# 🔧 Development workflow
make dev-install          # 📦 Install development dependencies
make format              # 🎨 Format code with black
make lint                # 🔍 Run linting (black + ruff)
make type-check          # 🔬 Run type checking with mypy
make security            # 🔒 Run security checks with bandit
make all-checks          # ✅ Run all code quality checks

# 🧪 Testing
make test                # 🧪 Run all tests
make test-cov            # 📊 Run tests with coverage
make test-fast           # ⚡ Run tests (stop on first failure)

# 🚀 Build & deployment
make build               # 📦 Build the package
make clean               # 🧹 Clean build artifacts
make ci                  # 🤖 Simulate CI pipeline

# 🔍 Pre-commit
make pre-commit          # 🔧 Run pre-commit hooks
make check               # ✅ Run pre-commit checks
```

### 🧪 Running Tests

```bash
# 🎯 Using make (recommended)
make test
make test-cov

# 🔧 Direct uv commands
uv run pytest tests/
uv run pytest tests/test_config.py
uv run pytest tests/ -v
```

## 💡 Best Practices

- Use docstrings for command descriptions
- Use `help` parameter in Arguments and Options for detailed help
- Use `typer.Typer()` with `no_args_is_help=True` for automatic help display
- Create subcommands with `typer.Typer()` and `app.add_typer()`