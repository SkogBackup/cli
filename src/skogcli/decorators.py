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
        # Store the explanation as an attribute on the function
        setattr(f, "_explanation", explanation)
        
        # The original function remains unchanged
        return f
    return decorator
