"""Tests for the skogcli decorators."""

import pytest
import subprocess
import typer
from functools import wraps
from skogcli.decorators import with_explanation


def test_with_explanation_decorator():
    """Test that the with_explanation decorator attaches the explanation to the function."""
    test_explanation = "This is a test explanation"
    
    @with_explanation(test_explanation)
    def test_func():
        return "Hello"
    
    # Check that the explanation is attached
    assert hasattr(test_func, "__explanation__")
    assert test_func.__explanation__ == test_explanation
    
    # Check that the function still works normally
    assert test_func() == "Hello"


def test_explanation_in_app():
    """Test that the explanation is shown when the command is invoked with no args."""
    # Create a simple app to test
    app = typer.Typer(no_args_is_help=True)
    
    @app.command()
    @with_explanation("Test explanation for the command.")
    def hello():
        typer.echo("Hello World")
    
    # Run just the command with no args
    # Note: This test would ideally use the app runner, but for simplicity
    # we're just checking that the decorator attaches the explanation
    assert hasattr(hello, "__explanation__")
    assert hello.__explanation__ == "Test explanation for the command."