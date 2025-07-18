"""Decorators for the skogcli application."""
from functools import wraps
from typing import Any, Callable, TypeVar, cast

import typer

F = TypeVar('F', bound=Callable[..., Any])

def with_explanation(explanation: str) -> Callable[[F], F]:
    """Add an explanation to a command's help text.
    
    Args:
        explanation: The explanation text to add to the command's help.
        
    Returns:
        A decorator that adds the explanation to the command's help text.
    """
    def decorator(func: F) -> F:
        # Add the explanation to the function's docstring
        if func.__doc__ is None:
            func.__doc__ = explanation
        else:
            func.__doc__ = f"{func.__doc__}\n\n{explanation}"
            
        # Add the explanation as an attribute
        func.__explanation__ = explanation
            
        # Preserve the original function's attributes
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)
            
        # Copy the explanation attribute to the wrapper
        wrapper.__explanation__ = explanation
            
        return cast(F, wrapper)
    return decorator

def handle_errors(func: F) -> F:
    """Handle common errors in command functions.
    
    This decorator catches common exceptions and displays them to the user
    in a user-friendly way.
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            typer.echo(f"Error: File or directory not found - {e}", err=True)
            raise typer.Exit(1)
        except PermissionError as e:
            typer.echo(f"Error: Permission denied - {e}", err=True)
            raise typer.Exit(1)
        except ValueError as e:
            typer.echo(f"Error: Invalid value - {e}", err=True)
            raise typer.Exit(1)
        except Exception as e:
            typer.echo(f"Unexpected error: {e}", err=True)
            raise typer.Exit(1)
    return cast(F, wrapper)
