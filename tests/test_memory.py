"""Test the memory module functionality."""

import pytest
from typer.testing import CliRunner
from src.skogcli import app
from unittest.mock import patch, MagicMock

# Create a test runner
runner = CliRunner()

def test_memory_command_exists():
    """Test that the memory command exists and returns help info."""
    result = runner.invoke(app, ["memory", "--help"])
    assert result.exit_code == 0
    assert "Local-first personal knowledge management" in result.stdout

def test_memory_create_command():
    """Test the create command returns the expected output."""
    # Test basic invocation
    result = runner.invoke(app, ["memory", "create", "Test Note", "test"])
    assert result.exit_code == 0
    assert "Not implemented yet" in result.stdout
    
    # Test with help flag
    result = runner.invoke(app, ["memory", "create", "--help"])
    assert result.exit_code == 0
    assert "Create or update a note in your knowledge base." in result.stdout
    
    # Test with content option
    result = runner.invoke(app, ["memory", "create", "Test Note", "test", "--content", "Test content"])
    assert result.exit_code == 0
    assert "Not implemented yet" in result.stdout
    
    # Test with tags option
    result = runner.invoke(app, ["memory", "create", "Test Note", "test", "--tags", "tag1,tag2"])
    assert result.exit_code == 0
    assert "Not implemented yet" in result.stdout

def test_memory_read_command():
    """Test the read command returns the expected output."""
    # Test basic invocation
    result = runner.invoke(app, ["memory", "read", "test-note"])
    assert result.exit_code == 0
    assert "Not implemented yet" in result.stdout
    
    # Test with help flag
    result = runner.invoke(app, ["memory", "read", "--help"])
    assert result.exit_code == 0
    assert "Read a note from your knowledge base." in result.stdout
    
    # Test with pagination options
    result = runner.invoke(app, ["memory", "read", "test-note", "--page", "2", "--page-size", "20"])
    assert result.exit_code == 0
    assert "Not implemented yet" in result.stdout
    
    # Test with raw option
    result = runner.invoke(app, ["memory", "read", "test-note", "--raw"])
    assert result.exit_code == 0
    assert "Not implemented yet" in result.stdout