# Coding Style and Conventions

## General Python Style
- Python 3.12+ required
- Use type hints consistently 
- Follow PEP 8 naming conventions (snake_case for functions/variables)
- Import organization: standard lib → third-party → local
- Use f-strings for string formatting
- No abbreviations or acronyms (use `number` instead of `num`)
- Don't write forgiving code - use preconditions and let exceptions propagate
- Unicode characters and emoji welcome (especially in comments, commit messages, docs)

## Typer CLI Patterns
- Use `typer.Typer(no_args_is_help=True)` for empty command help
- Use docstrings for command descriptions
- Use `help` parameter in Arguments and Options for detailed help
- Use `Annotated` for type hints with metadata
- Create subcommands with `typer.Typer()` and `app.add_typer()`
- Use Enum classes for choice options
- Set `context_settings` for consistent help behavior

## Rich Integration
- Use Rich for enhanced terminal output
- Create tables with `rich.table.Table` for structured data display
- Use `console.print()` for styled output
- Format command output consistently across the application

## Documentation
- Use docstrings for public functions/classes
- Error handling: use appropriate exception types and provide context
- Don't create documentation files unless explicitly requested

## Testing Patterns
- Test names should not include the word "test"
- Test assertions should be strict (prefer exact matches over partial)
- Use mocking as last resort - prefer fakes over mocks
- Use `SKOGAI_TEST_*` environment variables for test isolation
- Test Typer CLI apps with `CliRunner` from `typer.testing`

## Memory Module Specifics
- Wrapper around basic-memory subprocess calls
- Use `subprocess.run()` with `capture_output=True, text=True`
- Process markdown with Rich's Markdown for display