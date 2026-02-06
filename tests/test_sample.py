"""Sample Python file for testing LSP-MCP server."""

import os
from typing import List, Optional


def greet(name: str) -> str:
    """Greet a person by name.
    
    Args:
        name: The person's name
        
    Returns:
        A greeting message
    """
    return f"Hello, {name}!"


class Calculator:
    """A simple calculator class."""
    
    def __init__(self):
        self.history: List[float] = []
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Sum of a and b
        """
        result = a + b
        self.history.append(result)
        return result
    
    def get_history(self) -> List[float]:
        """Get calculation history.
        
        Returns:
            List of past results
        """
        return self.history.copy()


if __name__ == "__main__":
    # Test the functions
    message = greet("World")
    print(message)
    
    calc = Calculator()
    result = calc.add(5, 3)
    print(f"5 + 3 = {result}")
