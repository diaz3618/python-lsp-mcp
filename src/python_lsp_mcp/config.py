"""Configuration module for Python LSP-MCP Server."""

import sys
from pathlib import Path

from pydantic import BaseModel, Field

# Python 3.11+ has tomllib built-in, earlier versions need tomli
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


class LSPServerConfig(BaseModel):
    """Configuration for a single LSP server."""

    id: str = Field(..., description="Unique identifier for this LSP server")
    command: str = Field(..., description="Command to start the LSP server")
    args: list[str] = Field(default_factory=list, description="Arguments for the LSP command")
    extensions: list[str] = Field(
        default_factory=list, description="File extensions this LSP handles"
    )
    languages: list[str] = Field(default_factory=list, description="Language IDs this LSP handles")


class Config(BaseModel):
    """Main configuration for Python LSP-MCP Server."""

    lsps: list[LSPServerConfig] = Field(default_factory=list, description="LSP servers to manage")
    workspace: Path = Field(default=Path("/"), description="Default workspace root path")
    methods: list[str] | None = Field(
        default=None, description="Optional list of LSP methods to expose as tools"
    )
    eager_init: bool = Field(
        default=False, description="Whether to start all LSP servers at launch (default: False)"
    )


def load_config(config_path: Path) -> Config:
    """Load configuration from TOML file.

    Args:
        config_path: Path to TOML configuration file

    Returns:
        Config object with loaded settings

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config file is invalid
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    try:
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
        return Config(**data)
    except Exception as e:
        raise ValueError(f"Invalid configuration file: {e}") from e


def create_default_config() -> Config:
    """Create default configuration for Python development.

    Returns:
        Config with sensible defaults for Python LSP servers
    """
    return Config(
        lsps=[
            LSPServerConfig(
                id="pylsp",
                command="pylsp",
                args=[],
                extensions=[".py", ".pyi"],
                languages=["python"],
            )
        ],
        workspace=Path.cwd(),
    )
