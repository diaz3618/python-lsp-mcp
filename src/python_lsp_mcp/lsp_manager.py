"""LSP Manager for handling multiple Language Server Protocol clients."""

import logging
from pathlib import Path

from .config import Config, LSPServerConfig
from .lsp_client import LSPClient

logger = logging.getLogger(__name__)


class LSPManager:
    """Manages multiple LSP client instances and routes requests."""

    def __init__(self, config: Config):
        """Initialize LSP manager.

        Args:
            config: Configuration with LSP server definitions
        """
        self.config = config
        self.clients: dict[str, LSPClient] = {}
        self.extension_map: dict[str, str] = {}  # extension -> lsp_id
        self.language_map: dict[str, str] = {}  # language_id -> lsp_id

        # Build routing maps
        for lsp_config in config.lsps:
            for ext in lsp_config.extensions:
                self.extension_map[ext] = lsp_config.id
            for lang in lsp_config.languages:
                self.language_map[lang] = lsp_config.id

    async def start_all(self) -> None:
        """Start all configured LSP servers."""
        for lsp_config in self.config.lsps:
            await self.start_lsp(lsp_config.id)

    async def start_lsp(self, lsp_id: str) -> None:
        """Start a specific LSP server.

        Args:
            lsp_id: ID of the LSP server to start

        Raises:
            ValueError: If LSP ID not found in configuration
        """
        lsp_config = self._get_lsp_config(lsp_id)
        if lsp_id in self.clients:
            logger.warning(f"LSP server {lsp_id} already started")
            return

        client = LSPClient(lsp_config, self.config.workspace)
        await client.start()
        self.clients[lsp_id] = client
        logger.info(f"Started LSP server: {lsp_id}")

    async def shutdown_all(self) -> None:
        """Shutdown all LSP servers."""
        for lsp_id, client in list(self.clients.items()):
            await client.shutdown()
            del self.clients[lsp_id]

    def get_lsp_by_id(self, lsp_id: str) -> LSPClient:
        """Get LSP client by ID.

        Args:
            lsp_id: ID of the LSP server

        Returns:
            LSPClient instance

        Raises:
            ValueError: If LSP not found or not started
        """
        if lsp_id not in self.clients:
            raise ValueError(f"LSP server {lsp_id} not found or not started")
        return self.clients[lsp_id]

    def get_lsp_by_extension(self, file_path: Path) -> LSPClient:
        """Get LSP client for a file based on its extension.

        Args:
            file_path: Path to the file (string or Path object)

        Returns:
            LSPClient instance for this file type

        Raises:
            ValueError: If no LSP server handles this extension
        """
        # Convert to Path if string
        from pathlib import Path
        if isinstance(file_path, str):
            file_path = Path(file_path)
            
        extension = file_path.suffix
        if extension not in self.extension_map:
            raise ValueError(f"No LSP server configured for extension: {extension}")

        lsp_id = self.extension_map[extension]
        return self.get_lsp_by_id(lsp_id)

    def get_lsp_by_language(self, language_id: str) -> LSPClient:
        """Get LSP client for a language.

        Args:
            language_id: Language identifier (e.g., "python")

        Returns:
            LSPClient instance for this language

        Raises:
            ValueError: If no LSP server handles this language
        """
        if language_id not in self.language_map:
            raise ValueError(f"No LSP server configured for language: {language_id}")

        lsp_id = self.language_map[language_id]
        return self.get_lsp_by_id(lsp_id)

    def list_lsps(self) -> list[dict[str, str]]:
        """List all configured LSP servers.

        Returns:
            List of LSP server info dicts
        """
        return [
            {
                "id": lsp_config.id,
                "command": lsp_config.command,
                "languages": ", ".join(lsp_config.languages),
                "extensions": ", ".join(lsp_config.extensions),
                "status": "running" if lsp_config.id in self.clients else "stopped",
            }
            for lsp_config in self.config.lsps
        ]

    def _get_lsp_config(self, lsp_id: str) -> LSPServerConfig:
        """Get LSP server configuration by ID.

        Args:
            lsp_id: ID of the LSP server

        Returns:
            LSPServerConfig for this server

        Raises:
            ValueError: If LSP ID not found
        """
        for lsp_config in self.config.lsps:
            if lsp_config.id == lsp_id:
                return lsp_config
        raise ValueError(f"LSP server {lsp_id} not found in configuration")
