from typer.testing import CliRunner
from src.skogcli import app
import json
import os
from pathlib import Path

runner = CliRunner()

def test_config_show():
    """Test the config --show command."""
    result = runner.invoke(app, ["config", "--show"])
    assert result.exit_code == 0
    assert "Configuration" in result.stdout
    assert "api_url" in result.stdout
    assert "timeout" in result.stdout
    assert "debug" in result.stdout
    assert "theme" in result.stdout
    assert "output_format" in result.stdout

def test_config_list_keys():
    """Test the config --list-keys command."""
    result = runner.invoke(app, ["config", "--list-keys"])
    assert result.exit_code == 0
    assert "Available Configuration Keys" in result.stdout
    assert "Default Value" in result.stdout
    assert "api_url" in result.stdout

def test_config_set():
    """Test the config --set command."""
    # Set a value
    result = runner.invoke(app, ["config", "--set", "theme", "--value", "test_theme"])
    assert result.exit_code == 0
    assert "Setting theme=test_theme" in result.stdout
    
    # Verify the value was set
    result = runner.invoke(app, ["config", "--show"])
    assert "test_theme" in result.stdout
    
    # Reset at the end
    runner.invoke(app, ["config", "--reset"])

def test_config_reset():
    """Test the config --reset command."""
    # First change a value
    runner.invoke(app, ["config", "--set", "theme", "--value", "test_theme"])
    
    # Then reset
    result = runner.invoke(app, ["config", "--reset"])
    assert result.exit_code == 0
    assert "Configuration reset to defaults" in result.stdout
    
    # Verify the value was reset
    result = runner.invoke(app, ["config", "--show"])
    assert "dark" in result.stdout  # Default theme value