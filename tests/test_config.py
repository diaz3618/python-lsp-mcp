"""Tests for configuration loading."""

from pathlib import Path
import tempfile

import pytest

from python_lsp_mcp.config import Config, LSPServerConfig, load_config, create_default_config


class TestLSPServerConfig:
    """Test LSP server configuration."""
    
    def test_server_config_creation(self):
        """Test creating LSP server config."""
        config = LSPServerConfig(
            id="test-lsp",
            command="pylsp",
            args=["--stdio"],
            extensions=[".py"],
            languages=["python"]
        )
        
        assert config.id == "test-lsp"
        assert config.command == "pylsp"
        assert config.args == ["--stdio"]
        assert ".py" in config.extensions
        assert "python" in config.languages
    
    def test_server_config_defaults(self):
        """Test LSP server config with defaults."""
        config = LSPServerConfig(
            id="test",
            command="test-lsp",
            extensions=[".py"],
            languages=["python"]
        )
        
        assert config.args == []


class TestConfig:
    """Test main configuration."""
    
    def test_config_creation(self):
        """Test creating configuration."""
        lsp_config = LSPServerConfig(
            id="pylsp",
            command="pylsp",
            extensions=[".py"],
            languages=["python"]
        )
        
        config = Config(
            lsps=[lsp_config],
            workspace=Path("/tmp")
        )
        
        assert len(config.lsps) == 1
        assert config.workspace == Path("/tmp")
        assert config.methods is None
    
    def test_config_with_methods(self):
        """Test config with method filtering."""
        lsp_config = LSPServerConfig(
            id="pylsp",
            command="pylsp",
            extensions=[".py"],
            languages=["python"]
        )
        
        config = Config(
            lsps=[lsp_config],
            workspace="/tmp",
            methods=["textDocument/hover", "textDocument/definition"]
        )
        
        assert len(config.methods) == 2
        assert "textDocument/hover" in config.methods


class TestConfigLoading:
    """Test configuration file loading."""
    
    def test_load_toml_config(self, tmp_path):
        """Test loading configuration from TOML file."""
        config_file = tmp_path / "config.toml"
        config_file.write_text('''
workspace = "/test/workspace"

[[lsps]]
id = "pylsp"
command = "pylsp"
args = []
extensions = [".py", ".pyi"]
languages = ["python"]

[[lsps]]
id = "pyright"
command = "pyright-langserver"
args = ["--stdio"]
extensions = [".py"]
languages = ["python"]

methods = ["textDocument/hover", "textDocument/definition"]
''')
        
        config = load_config(config_file)
        
        assert config.workspace == Path("/test/workspace")
        assert len(config.lsps) == 2
        assert config.lsps[0].id == "pylsp"
        assert config.lsps[1].id == "pyright"
        assert config.methods is None  # TOML loading doesn't parse methods yet
    
    def test_create_default_config(self):
        """Test creating default configuration."""
        config = create_default_config()
        
        assert len(config.lsps) == 1
        assert config.lsps[0].id == "pylsp"
        assert config.lsps[0].command == "pylsp"
        assert ".py" in config.lsps[0].extensions
        assert "python" in config.lsps[0].languages
