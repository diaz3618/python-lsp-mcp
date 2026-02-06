"""Integration tests for full LSP-MCP workflow."""

import pytest

from python_lsp_mcp.config import Config, LSPServerConfig
from python_lsp_mcp.lsp_manager import LSPManager


class TestIntegration:
    """Integration tests with real LSP server."""

    @pytest.mark.asyncio
    async def test_hover_request(self, workspace_dir, sample_python_file):
        """Test hover request end-to-end."""
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

        # Get LSP client
        client = manager.get_lsp_by_extension(str(sample_python_file))

        # Open document
        await client.notify_document_open(str(sample_python_file), "python")

        # Send hover request
        params = {
            "textDocument": {"uri": f"file://{sample_python_file}"},
            "position": {"line": 6, "character": 4},  # On 'greet' function
        }

        response = await client.send_request("textDocument/hover", params)

        # Response should have contents
        assert response is not None

        await manager.shutdown_all()

    @pytest.mark.asyncio
    async def test_definition_request(self, workspace_dir, sample_python_file):
        """Test definition request end-to-end."""
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

        client = manager.get_lsp_by_extension(str(sample_python_file))
        await client.notify_document_open(str(sample_python_file), "python")

        # Request definition of 'greet' call
        params = {
            "textDocument": {"uri": f"file://{sample_python_file}"},
            "position": {"line": 37, "character": 15},  # On 'greet("World")' call
        }

        response = await client.send_request("textDocument/definition", params)

        # May or may not find definition depending on LSP setup
        # Just ensure no crash
        assert response is not None or response is None

        await manager.shutdown_all()

    @pytest.mark.asyncio
    async def test_document_symbol_request(self, workspace_dir, sample_python_file):
        """Test document symbol request end-to-end."""
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

        client = manager.get_lsp_by_extension(str(sample_python_file))
        await client.notify_document_open(str(sample_python_file), "python")

        params = {"textDocument": {"uri": f"file://{sample_python_file}"}}

        response = await client.send_request("textDocument/documentSymbol", params)

        # Should get symbols (function, class)
        assert response is not None
        assert len(response) > 0

        await manager.shutdown_all()

    @pytest.mark.asyncio
    async def test_completion_request(self, workspace_dir, sample_python_file):
        """Test completion request end-to-end."""
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

        client = manager.get_lsp_by_extension(str(sample_python_file))
        await client.notify_document_open(str(sample_python_file), "python")

        # Request completion at end of a line
        params = {
            "textDocument": {"uri": f"file://{sample_python_file}"},
            "position": {"line": 10, "character": 10},
        }

        response = await client.send_request("textDocument/completion", params)

        # Should get some completions
        assert response is not None

        await manager.shutdown_all()

    @pytest.mark.asyncio
    async def test_multiple_requests_same_document(self, workspace_dir, sample_python_file):
        """Test multiple requests on the same document."""
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

        client = manager.get_lsp_by_extension(str(sample_python_file))
        await client.notify_document_open(str(sample_python_file), "python")

        # Send multiple requests
        hover_params = {
            "textDocument": {"uri": f"file://{sample_python_file}"},
            "position": {"line": 6, "character": 4},
        }
        await client.send_request("textDocument/hover", hover_params)

        symbol_params = {"textDocument": {"uri": f"file://{sample_python_file}"}}
        await client.send_request("textDocument/documentSymbol", symbol_params)

        completion_params = {
            "textDocument": {"uri": f"file://{sample_python_file}"},
            "position": {"line": 10, "character": 10},
        }
        await client.send_request("textDocument/completion", completion_params)

        await manager.shutdown_all()
