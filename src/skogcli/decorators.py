import functools
import typer
from typing import Callable, Optional, Any

def with_explanation(explanation: str):
    """
    Decorator that adds a custom explanation to a command.
    
    When the command is invoked without arguments, it shows both
    the custom explanation and the standard help.
    
    Args:
        explanation: The explanation text to display
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Check if no arguments were provided
            ctx = typer.Context.get_current()
            if ctx and not ctx.invoked_subcommand and not ctx.args:
                typer.echo(explanation)
                typer.echo("\nCommand help:")
                ctx.invoke(ctx.command.get_help)
                return None
            return f(*args, **kwargs)
        return wrapper
    return decorator
