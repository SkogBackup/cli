import pytest
from typer.testing import CliRunner
from src.skogcli import app

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
