import pytest
from typer.testing import CliRunner
from src.skogcli import app, Format

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
    assert "Debug info" in result.stdout
    
    # Test with no files
    result = runner.invoke(app, ["examples", "callback"])
    assert result.exit_code == 0
    assert "No files to process" in result.stdout
