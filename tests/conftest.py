"""Pytest configuration and fixtures."""

import asyncio
import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def sample_python_file(tmp_path):
    """Create a sample Python file for testing."""
    file_path = tmp_path / "sample.py"
    file_path.write_text('''"""Sample Python module for testing."""

from typing import List, Optional


def greet(name: str) -> str:
    """Greet a person by name.

    Args:
        name: Person's name

    Returns:
        Greeting message
    """
    return f"Hello, {name}!"


class Calculator:
    """Simple calculator class."""

    def __init__(self):
        self.history: List[float] = []

    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        result = a + b
        self.history.append(result)
        return result


if __name__ == "__main__":
    message = greet("World")
    print(message)
''')
    return file_path


@pytest.fixture
def workspace_dir(tmp_path):
    """Create a temporary workspace directory."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    return workspace


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
