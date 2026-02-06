"""Sample Python file to test LSP tools."""

def greet(name: str) -> str:
    """Greet someone by name.
    
    Args:
        name: The person's name
        
    Returns:
        A greeting message
    """
    return f"Hello, {name}!"


class Calculator:
    """Simple calculator class."""
    
    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        return a + b
    
    def multiply(self, a: int, b: int) -> int:
        """Multiply two numbers."""
        return a * b


if __name__ == "__main__":
    result = greet("World")
    print(result)
    
    calc = Calculator()
    sum_result = calc.add(5, 3)
    print(f"Sum: {sum_result}")
