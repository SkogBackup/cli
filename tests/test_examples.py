import pytest
import typer
from typer.testing import CliRunner
from src.skogcli import app, Format
from src.skogcli.decorators import with_explanation

runner = CliRunner()

def test_examples_basic():
    """Test the examples basic command with different parameters."""
    # Test with default count (1)
    result = runner.invoke(app, ["examples", "basic", "skogix"])
    assert result.exit_code == 0
    assert "Hello, skogix!" in result.stdout
    
    # Test with count=2
    result = runner.invoke(app, ["examples", "basic", "--count", "2", "skogix"])
    assert result.exit_code == 0
    assert result.stdout.count("Hello, skogix!") == 2
    
    # Test with formal flag
    result = runner.invoke(app, ["examples", "basic", "--formal", "skogix"])
    assert result.exit_code == 0
    assert "Greetings, skogix!" in result.stdout
    
    # Test with both count and formal
    result = runner.invoke(app, ["examples", "basic", "--count", "2", "--formal", "skogix"])
    assert result.exit_code == 0
    assert result.stdout.count("Greetings, skogix!") == 2

def test_examples_choices():
    """Test the examples choices command with different formats."""
    # Test with default format (TEXT)
    result = runner.invoke(app, ["examples", "choices", "item1", "item2"])
    assert result.exit_code == 0
    assert "item1" in result.stdout
    assert "item2" in result.stdout
    
    # Test with TEXT format explicitly
    result = runner.invoke(app, ["examples", "choices", "--format", "text", "item1", "item2"])
    assert result.exit_code == 0
    assert "item1" in result.stdout
    assert "item2" in result.stdout
    
    # Test with JSON format
    result = runner.invoke(app, ["examples", "choices", "--format", "json", "item1", "item2"])
    assert result.exit_code == 0
    assert "items" in result.stdout
    assert "item1" in result.stdout
    assert "item2" in result.stdout
    
    # Test with case insensitive format
    result = runner.invoke(app, ["examples", "choices", "--format", "JSON", "item1", "item2"])
    assert result.exit_code == 0
    assert "items" in result.stdout

def test_examples_callback():
    """Test the examples callback command with different parameters."""
    # Test without verbose flag
    result = runner.invoke(app, ["examples", "callback", "file1.txt", "file2.txt"])
    assert result.exit_code == 0
    assert "Processing 2 files:" in result.stdout
    assert "file1.txt" in result.stdout
    assert "file2.txt" in result.stdout
    assert "Debug info" not in result.stdout
    
    # Test with verbose flag
    result = runner.invoke(app, ["examples", "callback", "--verbose", "file1.txt", "file2.txt"])
    assert result.exit_code == 0
    assert "Processing 2 files:" in result.stdout
    assert "file1.txt" in result.stdout
    assert "file2.txt" in result.stdout
    assert "Verbose mode enabled" in result.stdout
    
    # Test with no files
    result = runner.invoke(app, ["examples", "callback"])
    assert result.exit_code == 0
    assert "No files provided" in result.stdout

def test_with_explanation_decorator():
    """Test the with_explanation decorator functionality."""
    # Create a mock command with the decorator
    @with_explanation("This is a test explanation for the command.")
    def mock_command():
        typer.echo("Command executed")
    
    # Create a test app with the decorated command
    test_app = typer.Typer(no_args_is_help=True)
    
    # Add callback to handle explanations
    @test_app.callback()
    def test_callback(ctx: typer.Context):
        if ctx.invoked_subcommand is None and hasattr(ctx.command, "callback"):
            callback = ctx.command.callback
            if hasattr(callback, "_explanation") and not ctx.args:
                typer.echo(callback._explanation)
                typer.echo("\nCommand help:")
                ctx.invoke(ctx.command.get_help)
                raise typer.Exit()
    
    # Add the command to the app
    test_app.command()(mock_command)
    
    # Test with no arguments (should show explanation and help)
    result = runner.invoke(test_app, ["mock-command"])
    assert result.exit_code == 0
    assert "This is a test explanation for the command." in result.stdout
    assert "Command help:" in result.stdout
    
    # Test with arguments (should execute normally)
    result = runner.invoke(test_app, ["mock-command", "--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout
    assert "This is a test explanation" not in result.stdout

def test_app_commands_with_explanation():
    """Test that the main app commands with explanations work correctly."""
    # Test hello command with no args (should show explanation)
    result = runner.invoke(app, ["hello"])
    assert result.exit_code == 0
    assert "A simple greeting command" in result.stdout
    assert "Command help:" in result.stdout
    
    # Test hello command with args (should execute normally)
    result = runner.invoke(app, ["hello", "Skogix"])
    assert result.exit_code == 0
    assert "Hello Skogix!" in result.stdout
    assert "A simple greeting command" not in result.stdout
    
    # Test config command with no args (should show explanation)
    result = runner.invoke(app, ["config"])
    assert result.exit_code == 0
    assert "Configure application settings" in result.stdout
    assert "Command help:" in result.stdout
    
    # Test examples basic command with no args (should show explanation)
    result = runner.invoke(app, ["examples", "basic"])
    assert result.exit_code == 0
    assert "A basic example showing how to use arguments" in result.stdout
    assert "Command help:" in result.stdout
