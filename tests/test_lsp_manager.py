"""Tests for LSP manager."""

import pytest

from python_lsp_mcp.config import Config, LSPServerConfig
from python_lsp_mcp.lsp_manager import LSPManager


class TestLSPManager:
    """Test LSP manager functionality."""

    def test_manager_initialization(self, workspace_dir):
        """Test LSP manager initialization."""
        config = Config(
            lsps=[
                LSPServerConfig(
                    id="pylsp",
                    command="pylsp",
                    args=[],
                    extensions=[".py", ".pyi"],
                    languages=["python"],
                )
            ],
            workspace=str(workspace_dir),
        )

        manager = LSPManager(config)

        # Manager creates clients on-demand, check routing maps instead
        assert len(manager.extension_map) > 0
        assert ".py" in manager.extension_map
        assert ".py" in manager.extension_map
        assert "python" in manager.language_map

    def test_manager_multiple_lsps(self, workspace_dir):
        """Test manager with multiple LSP servers."""
        config = Config(
            lsps=[
                LSPServerConfig(
                    id="pylsp", command="pylsp", args=[], extensions=[".py"], languages=["python"]
                ),
                LSPServerConfig(
                    id="typescript",
                    command="typescript-language-server",
                    args=["--stdio"],
                    extensions=[".ts", ".tsx"],
                    languages=["typescript"],
                ),
            ],
            workspace=str(workspace_dir),
        )

        manager = LSPManager(config)

        # Check routing maps for both LSPs
        assert len(manager.extension_map) >= 2
        assert ".py" in manager.extension_map
        assert ".ts" in manager.extension_map

    @pytest.mark.asyncio
    async def test_get_lsp_by_id(self, workspace_dir):
        """Test getting LSP by ID."""
        config = Config(
            lsps=[
                LSPServerConfig(
                    id="pylsp", command="pylsp", args=[], extensions=[".py"], languages=["python"]
                )
            ],
            workspace=str(workspace_dir),
        )

        manager = LSPManager(config)
        # Must start LSP before getting it
        await manager.start_lsp("pylsp")
        client = manager.get_lsp_by_id("pylsp")

        assert client is not None
        assert client.server_id == "pylsp"

        await manager.shutdown_all()

    def test_get_lsp_by_id_not_found(self, workspace_dir):
        """Test getting non-existent LSP by ID."""
        config = Config(
            lsps=[
                LSPServerConfig(
                    id="pylsp", command="pylsp", args=[], extensions=[".py"], languages=["python"]
                )
            ],
            workspace=str(workspace_dir),
        )

        manager = LSPManager(config)

        with pytest.raises(ValueError, match="not found or not started"):
            manager.get_lsp_by_id("nonexistent")

    @pytest.mark.asyncio
    async def test_get_lsp_by_extension(self, workspace_dir):
        """Test getting LSP by file extension."""
        config = Config(
            lsps=[
                LSPServerConfig(
                    id="pylsp",
                    command="pylsp",
                    args=[],
                    extensions=[".py", ".pyi"],
                    languages=["python"],
                )
            ],
            workspace=str(workspace_dir),
        )

        manager = LSPManager(config)
        await manager.start_all()

        client = manager.get_lsp_by_extension("test.py")
        assert client.server_id == "pylsp"

        client = manager.get_lsp_by_extension("types.pyi")
        assert client.server_id == "pylsp"

        await manager.shutdown_all()

    def test_get_lsp_by_extension_not_found(self, workspace_dir):
        """Test getting LSP for unsupported extension."""
        config = Config(
            lsps=[
                LSPServerConfig(
                    id="pylsp", command="pylsp", args=[], extensions=[".py"], languages=["python"]
                )
            ],
            workspace=str(workspace_dir),
        )

        manager = LSPManager(config)

        with pytest.raises(ValueError, match="No LSP server configured"):
            manager.get_lsp_by_extension("test.js")

    @pytest.mark.asyncio
    async def test_get_lsp_by_language(self, workspace_dir):
        """Test getting LSP by language ID."""
        config = Config(
            lsps=[
                LSPServerConfig(
                    id="pylsp", command="pylsp", args=[], extensions=[".py"], languages=["python"]
                )
            ],
            workspace=str(workspace_dir),
        )

        manager = LSPManager(config)
        await manager.start_all()
        client = manager.get_lsp_by_language("python")

        assert client.server_id == "pylsp"

        await manager.shutdown_all()

    def test_list_lsps(self, workspace_dir):
        """Test listing all LSP servers."""
        config = Config(
            lsps=[
                LSPServerConfig(
                    id="pylsp", command="pylsp", args=[], extensions=[".py"], languages=["python"]
                )
            ],
            workspace=str(workspace_dir),
        )

        manager = LSPManager(config)
        lsp_list = manager.list_lsps()

        assert len(lsp_list) == 1
        assert lsp_list[0]["id"] == "pylsp"
        assert lsp_list[0]["status"] == "stopped"

    @pytest.mark.asyncio
    async def test_start_all(self, workspace_dir):
        """Test starting all LSP servers."""
        config = Config(
            lsps=[
                LSPServerConfig(
                    id="pylsp", command="pylsp", args=[], extensions=[".py"], languages=["python"]
                )
            ],
            workspace=str(workspace_dir),
        )

        manager = LSPManager(config)
        await manager.start_all()

        lsp_list = manager.list_lsps()
        assert lsp_list[0]["status"] == "running"

        await manager.shutdown_all()

    @pytest.mark.asyncio
    async def test_start_lsp(self, workspace_dir):
        """Test starting specific LSP server."""
        config = Config(
            lsps=[
                LSPServerConfig(
                    id="pylsp", command="pylsp", args=[], extensions=[".py"], languages=["python"]
                )
            ],
            workspace=str(workspace_dir),
        )

        manager = LSPManager(config)
        await manager.start_lsp("pylsp")

        client = manager.get_lsp_by_id("pylsp")
        assert client.is_started()

        await manager.shutdown_all()
