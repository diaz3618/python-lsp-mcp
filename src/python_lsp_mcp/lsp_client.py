"""LSP Client wrapper using pygls."""

import logging
from pathlib import Path
from typing import Any

from pygls.client import JsonRPCClient

from .config import LSPServerConfig

logger = logging.getLogger(__name__)


class LSPClient:
    """Wrapper around pygls JsonRPCClient for LSP server communication."""

    def __init__(self, config: LSPServerConfig, workspace: str):
        """Initialize LSP client.

        Args:
            config: LSP server configuration
            workspace: Workspace root path
        """
        self.config = config
        self.server_id = config.id
        self.command = config.command
        self.args = config.args
        self.workspace = workspace
        self.client: JsonRPCClient | None = None
        self.server_capabilities: dict[str, Any] = {}
        self._started = False

    async def start(self) -> None:
        """Start the LSP server process and initialize connection."""
        logger.info(f"Starting LSP server: {self.command} {' '.join(self.args)}")

        try:
            # Create JSON-RPC client
            self.client = JsonRPCClient()

            # Start LSP server subprocess and connect via stdio
            # start_io handles subprocess creation internally
            logger.info("Starting LSP server subprocess...")
            await self.client.start_io(self.command, *self.args)

            logger.info("LSP server process started")

            # Initialize LSP server
            init_params = {
                "processId": None,
                "rootUri": f"file://{self.workspace}",
                "capabilities": {
                    "textDocument": {
                        "hover": {"contentFormat": ["plaintext", "markdown"]},
                        "definition": {"linkSupport": True},
                        "references": {},
                        "documentSymbol": {},
                        "completion": {"completionItem": {"snippetSupport": False}},
                    },
                    "workspace": {"symbol": {}},
                },
            }

            logger.info("Sending initialize request...")
            result = await self.client.protocol.send_request_async("initialize", init_params)
            # Result is an lsprotocol Object, convert to dict
            if hasattr(result, "__dict__"):
                result_dict = result.__dict__
            elif hasattr(result, "_asdict"):
                result_dict = result._asdict()
            else:
                result_dict = result

            if isinstance(result_dict, dict):
                self.server_capabilities = result_dict.get("capabilities", {})
            else:
                self.server_capabilities = {}
            logger.info("LSP server initialized successfully")

            # Send initialized notification
            self.client.protocol.notify("initialized", {})

            self._started = True

        except Exception as e:
            logger.error(f"Failed to start LSP server: {e}")
            await self.shutdown()
            raise RuntimeError(f"Failed to start LSP server: {e}") from e

    async def shutdown(self) -> None:
        """Shutdown the LSP server cleanly."""
        if not self._started:
            return

        try:
            if self.client:
                # Send shutdown request
                await self.client.protocol.send_request_async("shutdown", {})
                # Send exit notification
                self.client.protocol.notify("exit", {})
                # Stop the client (closes subprocess)
                await self.client.stop()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        finally:
            self._started = False
            self.client = None

    def is_started(self) -> bool:
        """Check if LSP server is started and ready."""
        return self._started

    async def send_request(self, method: str, params: Any) -> Any:
        """Send a request to the LSP server.

        Args:
            method: LSP method name (e.g., "textDocument/hover")
            params: Request parameters

        Returns:
            Response from LSP server
        """
        if not self._started or not self.client:
            raise RuntimeError("LSP client not started")

        return await self.client.protocol.send_request_async(method, params)

    async def notify_document_open(self, file_path: str, language_id: str) -> None:
        """Notify LSP server that a document was opened.

        Args:
            file_path: Absolute path to the file
            language_id: Language identifier (e.g., "python")
        """
        if not self._started or not self.client:
            raise RuntimeError("LSP client not started")

        # Read file content
        content = Path(file_path).read_text()

        self.client.protocol.notify(
            "textDocument/didOpen",
            {
                "textDocument": {
                    "uri": f"file://{file_path}",
                    "languageId": language_id,
                    "version": 1,
                    "text": content,
                }
            },
        )

    def has_capability(self, capability_path: str) -> bool:
        """Check if LSP server has a specific capability.

        Args:
            capability_path: Dot-separated path to capability
                            (e.g., "textDocument.hover")

        Returns:
            True if capability is supported
        """
        parts = capability_path.split(".")
        current = self.server_capabilities

        for part in parts:
            if not isinstance(current, dict) or part not in current:
                return False
            current = current[part]

        return True
