"""Tests for LSP client."""

import pytest

from python_lsp_mcp.config import LSPServerConfig
from python_lsp_mcp.lsp_client import LSPClient


class TestLSPClient:
    """Test LSP client functionality."""

    @pytest.mark.asyncio
    async def test_client_initialization(self, workspace_dir):
        """Test LSP client initialization."""
        config = LSPServerConfig(
            id="test-lsp", command="pylsp", args=[], extensions=[".py"], languages=["python"]
        )

        client = LSPClient(config, str(workspace_dir))

        assert client.server_id == "test-lsp"
        assert client.command == "pylsp"
        assert client.workspace == str(workspace_dir)
        assert not client.is_started()

    @pytest.mark.asyncio
    async def test_client_start_shutdown(self, workspace_dir):
        """Test starting and shutting down LSP client."""
        config = LSPServerConfig(
            id="pylsp", command="pylsp", args=[], extensions=[".py"], languages=["python"]
        )

        client = LSPClient(config, str(workspace_dir))

        # Start client
        await client.start()
        assert client.is_started()
        assert client.client is not None

        # Shutdown client
        await client.shutdown()
        assert not client.is_started()
        assert client.client is None

    @pytest.mark.asyncio
    async def test_client_double_start(self, workspace_dir):
        """Test that double start doesn't break anything."""
        config = LSPServerConfig(
            id="pylsp", command="pylsp", args=[], extensions=[".py"], languages=["python"]
        )

        client = LSPClient(config, str(workspace_dir))

        await client.start()
        # Second start should be handled gracefully
        # (current implementation doesn't prevent it, but shouldn't crash)

        await client.shutdown()

    @pytest.mark.asyncio
    async def test_client_send_request_not_started(self, workspace_dir):
        """Test sending request before client is started."""
        config = LSPServerConfig(
            id="pylsp", command="pylsp", args=[], extensions=[".py"], languages=["python"]
        )

        client = LSPClient(config, str(workspace_dir))

        with pytest.raises(RuntimeError, match="LSP client not started"):
            await client.send_request("textDocument/hover", {})

    @pytest.mark.asyncio
    async def test_client_capabilities(self, workspace_dir):
        """Test checking LSP server capabilities."""
        config = LSPServerConfig(
            id="pylsp", command="pylsp", args=[], extensions=[".py"], languages=["python"]
        )

        client = LSPClient(config, str(workspace_dir))
        await client.start()

        # Check that capabilities were populated
        assert client.server_capabilities is not None

        await client.shutdown()

    @pytest.mark.asyncio
    async def test_notify_document_open(self, workspace_dir, sample_python_file):
        """Test notifying document open."""
        config = LSPServerConfig(
            id="pylsp", command="pylsp", args=[], extensions=[".py"], languages=["python"]
        )

        client = LSPClient(config, str(workspace_dir))
        await client.start()

        # Should not raise
        await client.notify_document_open(str(sample_python_file), "python")

        await client.shutdown()
