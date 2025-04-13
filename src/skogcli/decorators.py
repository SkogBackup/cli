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
            # Simply store the explanation as an attribute
            # No need to access the context here
            return f(*args, **kwargs)
        
        # Store the explanation directly on the function for access outside of execution
        wrapper.__explanation__ = explanation
        return wrapper
    
    return decorator
