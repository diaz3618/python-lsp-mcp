"""MCP Server implementation for Python LSP integration."""

import logging
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from pydantic import BaseModel, Field

from .config import Config
from .lsp_manager import LSPManager

logger = logging.getLogger(__name__)


# Pydantic models for tool inputs
class HoverInput(BaseModel):
    """Input for textDocument/hover tool."""

    file: str = Field(..., description="Path to the Python file")
    line: int = Field(..., description="Line number (0-indexed)")
    character: int = Field(..., description="Character position (0-indexed)")
    lsp_id: str | None = Field(None, description="Specific LSP server ID to use (optional)")


class DefinitionInput(BaseModel):
    """Input for textDocument/definition tool."""

    file: str = Field(..., description="Path to the Python file")
    line: int = Field(..., description="Line number (0-indexed)")
    character: int = Field(..., description="Character position (0-indexed)")
    lsp_id: str | None = Field(None, description="Specific LSP server ID to use (optional)")


class LSPInfoInput(BaseModel):
    """Input for lsp_info tool."""

    lsp_id: str | None = Field(None, description="Specific LSP server ID to query (optional)")


class ReferencesInput(BaseModel):
    """Input for textDocument/references tool."""

    file: str = Field(..., description="Path to the Python file")
    line: int = Field(..., description="Line number (0-indexed)")
    character: int = Field(..., description="Character position (0-indexed)")
    lsp_id: str | None = Field(None, description="Specific LSP server ID to use (optional)")


class DocumentSymbolInput(BaseModel):
    """Input for textDocument/documentSymbol tool."""

    file: str = Field(..., description="Path to the Python file")
    lsp_id: str | None = Field(None, description="Specific LSP server ID to use (optional)")


class CompletionInput(BaseModel):
    """Input for textDocument/completion tool."""

    file: str = Field(..., description="Path to the Python file")
    line: int = Field(..., description="Line number (0-indexed)")
    character: int = Field(..., description="Character position (0-indexed)")
    lsp_id: str | None = Field(None, description="Specific LSP server ID to use (optional)")


def create_server(config: Config) -> tuple[Server, LSPManager]:
    """Create and configure the MCP server.

    Args:
        config: Configuration for LSP servers and MCP server

    Returns:
        Tuple of (configured Server instance, LSPManager instance)
    """
    server = Server("python-lsp-mcp")
    lsp_manager = LSPManager(config)

    def validate_file(file_path: Path) -> tuple[bool, str | None]:
        """Validate that a file exists and is a file.

        Args:
            file_path: Path to validate

        Returns:
            Tuple of (is_valid, error_message). If valid, error_message is None.
        """
        if not file_path.exists():
            return False, f"File not found: {file_path}"
        if not file_path.is_file():
            return False, f"Path is not a file: {file_path}"
        return True, None

    async def check_capability(
        lsp_client: Any, capability: str, tool_name: str
    ) -> list[dict[str, str]] | None:
        """Check if LSP supports capability, return error message if not.

        Args:
            lsp_client: The LSP client to check
            capability: Capability path (e.g., 'hoverProvider')
            tool_name: Name of tool for error message

        Returns:
            None if capability exists, error message list if not
        """
        if not lsp_client.has_capability(capability):
            return [
                {
                    "type": "text",
                    "text": f"LSP server '{lsp_client.server_id}' doesn't support {tool_name}",
                }
            ]
        return None

    # Tool: textDocument/hover
    @server.call_tool()
    async def textDocument_hover(arguments: dict[str, Any]) -> list[Any]:
        """Get hover information for a symbol at a position in a Python file.

        Provides type information, documentation, and signatures for symbols.
        """
        input_data = HoverInput(**arguments)
        file_path = Path(input_data.file)

        # Validate file exists
        is_valid, error_msg = validate_file(file_path)
        if not is_valid:
            return [{"type": "text", "text": f"Error: {error_msg}"}]

        # Get appropriate LSP client
        if input_data.lsp_id:
            lsp_client = lsp_manager.get_lsp_by_id(input_data.lsp_id)
        else:
            lsp_client = lsp_manager.get_lsp_by_extension(file_path)

        try:
            # Ensure client is started
            if not lsp_client.is_started():
                await lsp_client.start()

            # Check capability
            cap_error = await check_capability(lsp_client, "hoverProvider", "hover")
            if cap_error:
                return cap_error

            # Notify document open
            await lsp_client.notify_document_open(str(file_path.absolute()), "python")

            # Send hover request
            from lsprotocol.types import (
                HoverParams,
                Position,
                TextDocumentIdentifier,
            )

            params = HoverParams(
                text_document=TextDocumentIdentifier(uri=file_path.as_uri()),
                position=Position(line=input_data.line, character=input_data.character),
            )

            response = await lsp_client.send_request("textDocument/hover", params)

            # Format response
            if response and response.contents:
                contents = response.contents
                if isinstance(contents, str):
                    text = contents
                elif isinstance(contents, dict):
                    text = contents.get("value", str(contents))
                elif isinstance(contents, list):
                    text = "\n".join(
                        item.get("value", str(item)) if isinstance(item, dict) else str(item)
                        for item in contents
                    )
                else:
                    text = str(contents)

                return [{"type": "text", "text": text}]

            return [{"type": "text", "text": "No hover information available"}]

        except Exception as e:
            logger.error(f"Error in textDocument_hover: {e}", exc_info=True)
            return [{"type": "text", "text": f"Error getting hover information: {e}"}]

    # Tool: textDocument/definition
    @server.call_tool()
    async def textDocument_definition(arguments: dict[str, Any]) -> list[Any]:
        """Go to the definition of a symbol.

        Returns the location(s) where the symbol is defined.
        """
        input_data = DefinitionInput(**arguments)
        file_path = Path(input_data.file)

        # Validate file exists
        is_valid, error_msg = validate_file(file_path)
        if not is_valid:
            return [{"type": "text", "text": f"Error: {error_msg}"}]

        # Get appropriate LSP client
        if input_data.lsp_id:
            lsp_client = lsp_manager.get_lsp_by_id(input_data.lsp_id)
        else:
            lsp_client = lsp_manager.get_lsp_by_extension(file_path)

        try:
            # Ensure client is started
            if not lsp_client.is_started():
                await lsp_client.start()

            # Check capability
            cap_error = await check_capability(lsp_client, "definitionProvider", "definition")
            if cap_error:
                return cap_error

            # Notify document open
            await lsp_client.notify_document_open(str(file_path.absolute()), "python")

            # Send definition request
            from lsprotocol.types import (
                DefinitionParams,
                Position,
                TextDocumentIdentifier,
            )

            params = DefinitionParams(
                text_document=TextDocumentIdentifier(uri=file_path.as_uri()),
                position=Position(line=input_data.line, character=input_data.character),
            )

            response = await lsp_client.send_request("textDocument/definition", params)

            # Format response
            if not response:
                return [{"type": "text", "text": "No definition found"}]

            # Response can be Location, Location[], or LocationLink[]
            locations = response if isinstance(response, list) else [response]

            result_lines = []
            for loc in locations:
                if hasattr(loc, "uri"):
                    uri = loc.uri
                    range_info = loc.range if hasattr(loc, "range") else None
                    if range_info:
                        result_lines.append(
                            f"File: {uri}\n"
                            f"Line: {range_info.start.line + 1}\n"
                            f"Character: {range_info.start.character}"
                        )
                    else:
                        result_lines.append(f"File: {uri}")

            if result_lines:
                return [{"type": "text", "text": "\n\n".join(result_lines)}]

            return [{"type": "text", "text": "Definition found but could not be parsed"}]

        except Exception as e:
            logger.error(f"Error in textDocument_definition: {e}", exc_info=True)
            return [{"type": "text", "text": f"Error getting definition: {e}"}]

    # Tool: textDocument/references
    @server.call_tool()
    async def textDocument_references(arguments: dict[str, Any]) -> list[Any]:
        """Find all references to a symbol.

        Returns all locations where the symbol is referenced in the workspace.
        """
        input_data = ReferencesInput(**arguments)
        file_path = Path(input_data.file)

        # Validate file exists
        is_valid, error_msg = validate_file(file_path)
        if not is_valid:
            return [{"type": "text", "text": f"Error: {error_msg}"}]

        # Get appropriate LSP client
        if input_data.lsp_id:
            lsp_client = lsp_manager.get_lsp_by_id(input_data.lsp_id)
        else:
            lsp_client = lsp_manager.get_lsp_by_extension(file_path)

        try:
            # Ensure client is started
            if not lsp_client.is_started():
                await lsp_client.start()

            # Check capability
            cap_error = await check_capability(lsp_client, "referencesProvider", "references")
            if cap_error:
                return cap_error

            # Notify document open
            await lsp_client.notify_document_open(str(file_path.absolute()), "python")

            # Send references request
            params = {
                "textDocument": {"uri": f"file://{file_path.absolute()}"},
                "position": {"line": input_data.line, "character": input_data.character},
                "context": {"includeDeclaration": True},
            }

            response = await lsp_client.send_request("textDocument/references", params)

            # Format response
            if not response:
                return [{"type": "text", "text": "No references found"}]

            result_lines = [f"Found {len(response)} reference(s):"]
            for ref in response:
                if isinstance(ref, dict):
                    uri = ref.get("uri", "")
                    range_info = ref.get("range", {})
                else:
                    uri = getattr(ref, "uri", "")
                    range_info = getattr(ref, "range", {})

                if isinstance(range_info, dict):
                    start = range_info.get("start", {})
                else:
                    start = getattr(range_info, "start", {})

                if isinstance(start, dict):
                    line = start.get("line", -1)
                    char = start.get("character", -1)
                else:
                    line = getattr(start, "line", -1)
                    char = getattr(start, "character", -1)

                file_name = Path(uri.replace("file://", "")).name if uri else "unknown"
                result_lines.append(f"  - {file_name}:{line + 1}:{char + 1}")

            return [{"type": "text", "text": "\n".join(result_lines)}]

        except Exception as e:
            logger.error(f"Error in textDocument_references: {e}", exc_info=True)
            return [{"type": "text", "text": f"Error finding references: {e}"}]

    # Tool: textDocument/documentSymbol
    @server.call_tool()
    async def textDocument_documentSymbol(arguments: dict[str, Any]) -> list[Any]:
        """Get document symbols (outline/structure) of a file.

        Returns all symbols (classes, functions, variables) in the document.
        """
        input_data = DocumentSymbolInput(**arguments)
        file_path = Path(input_data.file)

        # Validate file exists
        is_valid, error_msg = validate_file(file_path)
        if not is_valid:
            return [{"type": "text", "text": f"Error: {error_msg}"}]

        # Get appropriate LSP client
        if input_data.lsp_id:
            lsp_client = lsp_manager.get_lsp_by_id(input_data.lsp_id)
        else:
            lsp_client = lsp_manager.get_lsp_by_extension(file_path)

        try:
            # Ensure client is started
            if not lsp_client.is_started():
                await lsp_client.start()

            # Check capability
            cap_error = await check_capability(
                lsp_client, "documentSymbolProvider", "document symbols"
            )
            if cap_error:
                return cap_error

            # Notify document open
            await lsp_client.notify_document_open(str(file_path.absolute()), "python")

            # Send document symbol request
            params = {"textDocument": {"uri": f"file://{file_path.absolute()}"}}

            response = await lsp_client.send_request("textDocument/documentSymbol", params)

            # Format response
            if not response:
                return [{"type": "text", "text": "No symbols found"}]

            def format_symbol(symbol: Any, indent: int = 0) -> list[str]:
                """Recursively format symbol information."""
                prefix = "  " * indent
                if isinstance(symbol, dict):
                    name = symbol.get("name", "")
                    kind = symbol.get("kind", 0)
                else:
                    name = getattr(symbol, "name", "")
                    kind = getattr(symbol, "kind", 0)

                # Symbol kind mapping (simplified)
                kind_names = {
                    1: "File",
                    2: "Module",
                    3: "Namespace",
                    4: "Package",
                    5: "Class",
                    6: "Method",
                    12: "Function",
                    13: "Variable",
                    14: "Constant",
                }
                kind_name = kind_names.get(kind, f"Kind{kind}")

                lines = [f"{prefix}{kind_name}: {name}"]

                # Process children
                if isinstance(symbol, dict):
                    children = symbol.get("children", [])
                else:
                    children = getattr(symbol, "children", [])
                for child in children:
                    lines.extend(format_symbol(child, indent + 1))

                return lines

            result_lines = ["Document Symbols:"]
            for symbol in response:
                result_lines.extend(format_symbol(symbol))

            return [{"type": "text", "text": "\n".join(result_lines)}]

        except Exception as e:
            logger.error(f"Error in textDocument_documentSymbol: {e}", exc_info=True)
            return [{"type": "text", "text": f"Error getting document symbols: {e}"}]

    # Tool: textDocument/completion
    @server.call_tool()
    async def textDocument_completion(arguments: dict[str, Any]) -> list[Any]:
        """Get code completion suggestions at a position.

        Returns available completions (functions, variables, keywords) at the cursor.
        """
        input_data = CompletionInput(**arguments)
        file_path = Path(input_data.file)

        # Validate file exists
        is_valid, error_msg = validate_file(file_path)
        if not is_valid:
            return [{"type": "text", "text": f"Error: {error_msg}"}]

        # Get appropriate LSP client
        if input_data.lsp_id:
            lsp_client = lsp_manager.get_lsp_by_id(input_data.lsp_id)
        else:
            lsp_client = lsp_manager.get_lsp_by_extension(file_path)

        try:
            # Ensure client is started
            if not lsp_client.is_started():
                await lsp_client.start()

            # Check capability
            cap_error = await check_capability(lsp_client, "completionProvider", "completion")
            if cap_error:
                return cap_error

            # Notify document open
            await lsp_client.notify_document_open(str(file_path.absolute()), "python")

            # Send completion request
            params = {
                "textDocument": {"uri": f"file://{file_path.absolute()}"},
                "position": {"line": input_data.line, "character": input_data.character},
            }

            response = await lsp_client.send_request("textDocument/completion", params)

            # Format response
            if not response:
                return [{"type": "text", "text": "No completions available"}]

            # Response can be CompletionList or CompletionItem[]
            items = response.get("items", response) if isinstance(response, dict) else response

            if not items:
                return [{"type": "text", "text": "No completions available"}]

            result_lines = [f"Found {len(items)} completion(s):"]
            for item in items[:20]:  # Limit to 20 items
                if isinstance(item, dict):
                    label = item.get("label", "")
                    kind = item.get("kind", 0)
                    detail = item.get("detail", "")
                else:
                    label = getattr(item, "label", "")
                    kind = getattr(item, "kind", 0)
                    detail = getattr(item, "detail", "")

                # Completion kind names
                kind_names = {
                    1: "Text",
                    2: "Method",
                    3: "Function",
                    4: "Constructor",
                    5: "Field",
                    6: "Variable",
                    7: "Class",
                    8: "Interface",
                    9: "Module",
                    10: "Property",
                    14: "Keyword",
                    15: "Snippet",
                }
                kind_name = kind_names.get(kind, "")

                result_lines.append(f"  - {label} ({kind_name}) {detail}")

            if len(items) > 20:
                result_lines.append(f"  ... and {len(items) - 20} more")

            return [{"type": "text", "text": "\n".join(result_lines)}]

        except Exception as e:
            logger.error(f"Error in textDocument_completion: {e}", exc_info=True)
            return [{"type": "text", "text": f"Error getting completions: {e}"}]

    # Tool: lsp_info
    @server.call_tool()
    async def lsp_info(arguments: dict[str, Any]) -> list[Any]:
        """Get information about configured LSP servers.

        Shows which LSP servers are configured, their status, and capabilities.
        """
        input_data = LSPInfoInput(**arguments)

        if input_data.lsp_id:
            # Get info for specific LSP
            lsp_client = lsp_manager.get_lsp_by_id(input_data.lsp_id)
            info = (
                f"LSP Server: {lsp_client.config.id}\n"
                f"Command: {lsp_client.config.command} {' '.join(lsp_client.config.args)}\n"
                f"Languages: {', '.join(lsp_client.config.languages)}\n"
                f"Extensions: {', '.join(lsp_client.config.extensions)}\n"
                f"Status: {'started' if lsp_client.is_started() else 'not started'}\n"
            )

            if lsp_client.is_started() and lsp_client.server_capabilities:
                info += f"\nCapabilities:\n{lsp_client.server_capabilities}"

            return [{"type": "text", "text": info}]

        # List all LSPs
        lsps = lsp_manager.list_lsps()
        if not lsps:
            return [{"type": "text", "text": "No LSP servers configured"}]

        info_lines = ["Configured LSP Servers:", ""]
        for lsp_info in lsps:
            info_lines.append(
                f"ID: {lsp_info['id']}\n"
                f"Command: {lsp_info['command']}\n"
                f"Languages: {lsp_info['languages']}\n"
                f"Extensions: {lsp_info['extensions']}\n"
                f"Status: {lsp_info['status']}\n"
            )

        return [{"type": "text", "text": "\n".join(info_lines)}]

    return server, lsp_manager


async def run_server(config: Config) -> None:
    """Run the MCP server with stdio transport.

    Args:
        config: Configuration for the server
    """
    server, lsp_manager = create_server(config)

    # Eager initialization: start all LSP servers if configured
    if config.eager_init:
        logger.info("Eager initialization enabled - starting all LSP servers...")
        await lsp_manager.start_all()
        logger.info("All LSP servers started")

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())
