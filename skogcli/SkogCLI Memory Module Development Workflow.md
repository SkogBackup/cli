---
title: SkogCLI Memory Module Development Workflow
type: note
permalink: projects/skogcli/skog-cli-memory-module-development-workflow
tags:
- '#skogcli #workflow #test-driven-development #memory-module'
---

# SkogCLI Memory Module Development Workflow

This document outlines the workflow we've developed for implementing the skogcli memory module through test-driven development (TDD).

## Current Implementation Status

The memory module has been set up with a basic structure and several placeholder commands. Each command currently returns "Not implemented yet" but has proper CLI argument handling and help text based on the basic-memory tool.

Commands implemented as placeholders:
- `create` - Create or update a note
- `read` - Read a note from the knowledge base
- `search` - Search across your knowledge base 
- `list` - List recent activity
- `sync` - Synchronize knowledge files with database
- `status` - Show sync status

## Test-Driven Development Workflow

We've established an effective workflow for incrementally building out the memory module:

1. **Write tests first**: For each command, we write tests that define the expected behavior
2. **Run tests to confirm they fail**: Ensure tests correctly identify missing functionality
3. **Implement placeholder command**: Add the command structure with arguments, options, and help text
4. **Run tests to verify command structure**: Ensure the placeholder passes tests
5. **Repeat for each command**: Incrementally add new commands
6. **Implement actual functionality later**: Replace "Not implemented yet" with real implementations

### Test Structure

Each command test follows a similar pattern:

```python
def test_memory_command_name():
    """Test the command_name returns the expected output."""
    # Test basic invocation
    result = runner.invoke(app, ["memory", "command_name", "arg1", "arg2"])
    assert result.exit_code == 0
    assert "Not implemented yet" in result.stdout
    
    # Test with help flag
    result = runner.invoke(app, ["memory", "command_name", "--help"])
    assert result.exit_code == 0
    assert "Command description text" in result.stdout
    
    # Test with specific options
    result = runner.invoke(app, ["memory", "command_name", "arg1", "--option1", "value1"])
    assert result.exit_code == 0
    assert "Not implemented yet" in result.stdout
```

### Implementation Template for Commands

Each command follows this implementation pattern:

```python
@memory_app.command("command_name")
@with_explanation("Brief description of the command purpose.")
def command_function(
    arg1: str = typer.Argument(..., help="Description of arg1"),
    arg2: str = typer.Argument(..., help="Description of arg2"),
    option1: Optional[str] = typer.Option(None, "--option1", "-o", help="Description of option1"),
):
    """
    Detailed description of the command.
    
    Additional context about how and when to use it.
    
    Examples:
    
    Basic example:
      skogcli memory command_name "arg1" arg2
      
    With options:
      skogcli memory command_name "arg1" arg2 --option1 value1
    """
    typer.echo("Not implemented yet")
```

## Future Full Implementation Plan

When implementing the actual functionality (replacing "Not implemented yet"), we'll:

1. **Update one test at a time**: Modify tests to expect actual outputs
2. **Use subprocess to call basic-memory**: Implement by passing commands to basic-memory
3. **Handle formatting and errors**: Properly format outputs and handle errors
4. **Run tests to verify**: Ensure functionality works as expected

### Actual Implementation Template

```python
@memory_app.command("command_name")
@with_explanation("Brief description of the command purpose.")
def command_function(
    arg1: str = typer.Argument(..., help="Description of arg1"),
    arg2: str = typer.Argument(..., help="Description of arg2"),
    option1: Optional[str] = typer.Option(None, "--option1", "-o", help="Description of option1"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Specific project to use"),
):
    """Command docstring with examples..."""
    
    # Construct basic-memory command
    cmd = ["tool", "equivalent-command", arg1, arg2]
    
    # Add options if provided
    if option1:
        cmd.extend(["--option1", option1])
    
    # Add project if specified
    if project:
        cmd = ["--project", project] + cmd
    
    # Run the command through basic-memory
    result = run_basic_memory(cmd)
    
    # Handle the result
    if result.returncode == 0:
        # Format and display output
        output = process_output(result.stdout)
        console.print(output)
    else:
        # Handle errors
        typer.echo(f"Error: {result.stderr}")
        raise typer.Exit(code=1)
```

## Helper Functions Needed

For the full implementation, we'll need these helper functions:

```python
def run_basic_memory(args: List[str]) -> subprocess.CompletedProcess:
    """Run basic-memory with the given arguments."""
    cmd = ["basic-memory"] + args
    return subprocess.run(cmd, capture_output=True, text=True)

def process_output(output: str) -> Union[str, Markdown]:
    """Process output from basic-memory into appropriate format."""
    # Default implementation just returns the string
    # Could be enhanced to format as Markdown, tables, etc.
    return output
```

## Lessons Learned

1. **Test first approach works well**: Writing tests before implementation helps clarify the interface
2. **Incremental development is efficient**: Adding one command at a time with tests keeps the process manageable
3. **Consistent patterns are important**: Using the same pattern for all commands makes the code more maintainable
4. **Help text and examples matter**: Comprehensive help text and examples make the CLI more usable

## Next Steps

1. Complete placeholder implementation for all commands from basic-memory
2. Add tests for error conditions (missing arguments, invalid options)
3. Begin implementing actual functionality for each command
4. Add integration tests that verify interaction with basic-memory
5. Document the completed module with usage examples