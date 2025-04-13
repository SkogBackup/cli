import typer
from functools import wraps
from typing import Callable, Optional

def with_explanation(explanation: str) -> Callable:
    """
    A decorator that adds an explanation to a command.
    
    This decorator stores the explanation text in the command's callback context
    for later retrieval and display.
    
    Args:
        explanation: The explanation text to associate with the command
        
    Returns:
        A decorator function that wraps the command
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Store the explanation in the current context if available
            ctx = typer.Context.get_current()
            if ctx:
                ctx.obj = ctx.obj or {}
                ctx.obj["explanation"] = explanation
            return f(*args, **kwargs)
        
        # Store the explanation directly on the function for access outside of execution
        wrapper.__explanation__ = explanation
        return wrapper
    
    return decorator
