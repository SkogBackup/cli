# Design Patterns and Guidelines

## SkogAI-Specific Patterns
- **Memory Module**: Wrapper around basic-memory subprocess calls
- **Configuration Management**: JSON-based with environment variable overrides
- **CLI Structure**: Modular subcommands using Typer
- **Rich Integration**: Enhanced terminal output throughout

## Key Design Principles
- **Test-Driven Development (TDD)**: Tests first, then implementation
- **Documentation-Driven Design (DDD)**: Documentation guides implementation
- **No Forgiving Code**: Use preconditions, let exceptions propagate
- **Functional Approach**: Prefer pure functions and immutable data
- **Semantic Clarity**: Meaningful names over generic labels

## CLI Command Patterns
- Use `no_args_is_help=True` for empty command help
- Subcommands organized by domain (memory, config, script, agent)
- Consistent help and documentation across commands
- Support for `--helpall` comprehensive documentation

## Error Handling Patterns
- Use appropriate exception types with context
- Don't add defensive try/catch blocks unnecessarily
- Let exceptions propagate to user level
- Decorators for common error handling patterns

## Memory Module Integration
- Subprocess calls to basic-memory with proper error handling
- Rich markdown processing for display
- Pagination support for large datasets
- Environment variable configuration

## Testing Patterns
- Use `SKOGAI_TEST_*` prefix for test environment variables
- Separate test configuration from production
- Test CLI commands using Typer's CliRunner
- Strict assertions over partial matches

## Data Flow Architecture
- Configuration → Environment Variables → JSON defaults
- CLI Commands → Module Functions → External Tools (basic-memory)
- Rich Processing → Console Output
