from typer.testing import CliRunner
from skogcli import app

runner = CliRunner()

def test_config_show():
    """Test the config --show command"""
    result = runner.invoke(app, ["config", "--show"])
    assert result.exit_code == 0
    assert "Configuration" in result.stdout
    assert "api_url" in result.stdout
    assert "https://api.example.com" in result.stdout

def test_config_set():
    """Test the config --set command"""
    result = runner.invoke(app, ["config", "--set", "api_url", "--value", "https://new-api.example.com"])
    assert result.exit_code == 0
    assert "Setting api_url=https://new-api.example.com" in result.stdout

def test_config_reset():
    """Test the config --reset command"""
    result = runner.invoke(app, ["config", "--reset"])
    assert result.exit_code == 0
    assert "Configuration reset to defaults" in result.stdout

def test_config_no_args():
    """Test the config command with no arguments"""
    result = runner.invoke(app, ["config"])
    assert result.exit_code == 0
    assert "Use --show to view configuration" in result.stdout
