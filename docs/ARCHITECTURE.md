# Python LSP-MCP Server Architecture Design

## Project Overview
A Python implementation of LSP-MCP server that enables LLMs/AI agents to interact with Python Language Server Protocol (LSP) servers for language-aware context from Python codebases.

## Goals
1. Focus ONLY on Python development (not TypeScript/JavaScript)
2. Use Python MCP SDK native patterns (decorator-based)
3. Integrate with Python LSP servers (pylsp, pyright, jedi-language-server)
4. Simple, Pythonic, maintainable codebase
5. Support multiple Python LSP servers simultaneously

## Non-Goals
- TypeScript/JavaScript LSP server support
- Complex JSON schema generation from TypeScript definitions
- Frontend/web infrastructure features

## Technology Stack

### Core Dependencies
- **Python 3.12+**: Modern async features
- **mcp[cli]**: Model Context Protocol Python SDK
- **pygls**: Python Language Server implementation
- **lsprotocol**: LSP protocol types
- **pydantic**: Data validation and settings management
- **tomli / tomllib**: TOML configuration parsing
- **asyncio**: Async I/O

### Development Dependencies
- **pytest**: Testing framework
- **pytest-asyncio**: Async test support
- **black**: Code formatting
- **ruff**: Linting
- **mypy**: Type checking

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│ AI Client (Claude Desktop, Cursor, etc.)                    │
└─────────────────────────────────────────────────────────────┘
                         ↓ MCP Protocol (stdio)
┌─────────────────────────────────────────────────────────────┐
│ Python LSP-MCP Server                                       │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ MCPServer (from mcp.server.mcpserver)                │   │
│  │ - Decorator-based tool registration                  │   │
│  │ - Automatic schema generation                        │   │
│  │ - Built-in transport handling                        │   │
│  └──────────────────────────────────────────────────────┘   │
│                         ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Tool Implementations (tools/)                        │   │
│  │ - @mcp.tool() decorated functions                    │   │
│  │ - One module per LSP method category                 │   │
│  │ - Pydantic models for input/output                   │   │
│  └──────────────────────────────────────────────────────┘   │
│                         ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ LSP Manager                                          │   │
│  │ - Manages multiple LSP client instances              │   │
│  │ - Routes requests to appropriate LSP                 │   │
│  │ - By language, extension, or explicit ID             │   │
│  └──────────────────────────────────────────────────────┘   │
│                         ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ LSP Clients (lsp_client.py)                          │   │
│  │ - Wraps pygls BaseLanguageClient                     │   │
│  │ - Manages subprocess (asyncio)                       │   │
│  │ - Handles initialization and capabilities            │   │
│  │ - File notification (didOpen)                        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                         ↓ LSP Protocol (JSON-RPC)
┌─────────────────────────────────────────────────────────────┐
│ Python LSP Servers (pylsp, pyright, etc.)                   │
└─────────────────────────────────────────────────────────────┘
```

### Project Structure

```
python-lsp-mcp/
├── src/
│   └── python_lsp_mcp/
│       ├── __init__.py
│       ├── __main__.py          # Entry point
│       ├── server.py             # MCPServer setup and configuration
│       ├── config.py             # Configuration loading (TOML)
│       ├── lsp_client.py         # LSP client wrapper
│       ├── lsp_manager.py        # LSP client management
│       ├── models.py             # Pydantic models
│       └── tools/                # Tool implementations
│           ├── __init__.py
│           ├── textdocument.py  # textDocument/* methods
│           ├── workspace.py     # workspace/* methods
│           └── utils.py         # Shared utilities
├── tests/
│   ├── __init__.py
│   ├── test_lsp_client.py
│   ├── test_lsp_manager.py
│   └── test_tools.py
├── configs/
│   └── example.toml             # Example configuration
├── docs/
│   ├── README.md
│   └── research/
├── pyproject.toml
├── README.md
└── .gitignore
```

## Core Components

### 1. Entry Point (__main__.py)

```python
import argparse
import asyncio
import sys
from pathlib import Path

from .server import create_server
from .config import load_config

def main():
    parser = argparse.ArgumentParser(
        description="Python LSP-MCP Server"
    )
    parser.add_argument(
        "--config",
        "-c",
        type=Path,
        help="Path to configuration file (TOML)"
    )
    parser.add_argument(
        "--workspace",
        "-w",
        type=Path,
        default=Path("/"),
        help="Workspace root path"
    )
    parser.add_argument(
        "--lsp-command",
        help="Single LSP command (e.g., 'pylsp')"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    if args.config:
        config = load_config(args.config)
    elif args.lsp_command:
        # Simple single LSP mode
        config = create_simple_config(args.lsp_command, args.workspace)
    else:
        print("Error: Provide --config or --lsp-command", file=sys.stderr)
        sys.exit(1)
    
    # Create and run server
    mcp = create_server(config)
    mcp.run()  # Stdio transport by default

if __name__ == "__main__":
    main()
```

### 2. Server Setup (server.py)

```python
from mcp.server.mcpserver import MCPServer
from typing import TYPE_CHECKING

from .lsp_manager import LspManager
from .config import Config
from .tools.textdocument import register_textdocument_tools
from .tools.workspace import register_workspace_tools

if TYPE_CHECKING:
    from .lsp_client import LspClient

# Global LSP manager (accessible by tool functions)
_lsp_manager: LspManager | None = None

def get_lsp_manager() -> LspManager:
    """Get the global LSP manager instance"""
    if _lsp_manager is None:
        raise RuntimeError("LSP manager not initialized")
    return _lsp_manager

def create_server(config: Config) -> MCPServer:
    """Create and configure the MCP server"""
    global _lsp_manager
    
    # Create MCP server
    mcp = MCPServer("python-lsp-mcp")
    
    # Initialize LSP manager
    _lsp_manager = LspManager(config)
    
    # Register tools
    register_textdocument_tools(mcp)
    register_workspace_tools(mcp)
    
    # Register lsp_info tool
    @mcp.tool()
    def lsp_info() -> dict:
        """Get information about available LSP servers"""
        manager = get_lsp_manager()
        return {
            "servers": [
                {
                    "id": client.id,
                    "languages": client.languages,
                    "extensions": client.extensions,
                    "started": client.is_started(),
                    "capabilities": client.capabilities if client.is_started() else None
                }
                for client in manager.get_all_clients()
            ]
        }
    
    return mcp
```

### 3. LSP Client (lsp_client.py)

```python
import asyncio
import os
from pathlib import Path
from typing import Any

from lsprotocol import types
from pygls.lsp.client import BaseLanguageClient

class LspClient:
    """Wrapper around pygls BaseLanguageClient for LSP server communication"""
    
    def __init__(
        self,
        id: str,
        languages: list[str],
        extensions: list[str],
        command: str,
        args: list[str],
        workspace: Path
    ):
        self.id = id
        self.languages = languages
        self.extensions = extensions
        self.command = command
        self.args = args
        self.workspace = workspace
        
        self._client: BaseLanguageClient | None = None
        self._process: asyncio.subprocess.Process | None = None
        self.capabilities: types.ServerCapabilities | None = None
        self._opened_files: set[str] = set()
    
    def is_started(self) -> bool:
        """Check if LSP server is started"""
        return self._client is not None
    
    async def start(self) -> None:
        """Start the LSP server subprocess and initialize"""
        if self.is_started():
            return
        
        # Spawn LSP server process
        self._process = await asyncio.create_subprocess_exec(
            self.command,
            *self.args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        if not self._process.stdin or not self._process.stdout:
            raise RuntimeError("Failed to create LSP subprocess")
        
        # Create pygls client
        self._client = BaseLanguageClient(
            "python-lsp-mcp",
            "1.0.0",
            self._process.stdin,
            self._process.stdout
        )
        
        # Start client
        await self._client.start()
        
        # Initialize LSP server
        result = await self._client.send_request(
            types.INITIALIZE,
            types.InitializeParams(
                process_id=os.getpid(),
                root_uri=self.workspace.as_uri(),
                capabilities=types.ClientCapabilities()
            )
        )
        
        self.capabilities = result.capabilities
        
        # Send initialized notification
        await self._client.send_notification(
            types.INITIALIZED,
            types.InitializedParams()
        )
    
    async def open_file(self, file_path: Path, language_id: str = "python") -> str:
        """Open a file in the LSP server and return its URI"""
        uri = file_path.as_uri()
        
        if uri in self._opened_files:
            return uri
        
        # Read file contents
        content = file_path.read_text()
        
        # Send didOpen notification
        await self._client.send_notification(
            types.TEXT_DOCUMENT_DID_OPEN,
            types.DidOpenTextDocumentParams(
                text_document=types.TextDocumentItem(
                    uri=uri,
                    language_id=language_id,
                    version=1,
                    text=content
                )
            )
        )
        
        self._opened_files.add(uri)
        return uri
    
    async def send_request(self, method: str, params: Any) -> Any:
        """Send a request to the LSP server"""
        if not self.is_started():
            await self.start()
        
        if self._client is None:
            raise RuntimeError("LSP client not started")
        
        return await self._client.send_request(method, params)
    
    async def dispose(self) -> None:
        """Clean up resources"""
        if self._client:
            await self._client.stop()
        if self._process:
            self._process.terminate()
            await self._process.wait()
```

### 4. LSP Manager (lsp_manager.py)

```python
from pathlib import Path
from typing import Optional

from .lsp_client import LspClient
from .config import Config, LspServerConfig

class LspManager:
    """Manages multiple LSP client instances"""
    
    def __init__(self, config: Config):
        self._clients: dict[str, LspClient] = {}
        self._language_map: dict[str, LspClient] = {}
        self._extension_map: dict[str, LspClient] = {}
        
        # Create LSP clients from config
        for server_config in config.lsp_servers:
            client = LspClient(
                id=server_config.id,
                languages=server_config.languages,
                extensions=server_config.extensions,
                command=server_config.command,
                args=server_config.args,
                workspace=config.workspace
            )
            
            self._clients[server_config.id] = client
            
            # Build language and extension maps
            for lang in server_config.languages:
                self._language_map[lang] = client
            for ext in server_config.extensions:
                self._extension_map[ext] = client
    
    def get_client_by_id(self, id: str) -> Optional[LspClient]:
        """Get LSP client by ID"""
        return self._clients.get(id)
    
    def get_client_by_language(self, language: str) -> Optional[LspClient]:
        """Get LSP client by programming language"""
        return self._language_map.get(language)
    
    def get_client_by_extension(self, extension: str) -> Optional[LspClient]:
        """Get LSP client by file extension"""
        return self._extension_map.get(extension)
    
    def get_client_by_file(self, file_path: Path) -> Optional[LspClient]:
        """Get LSP client by file path (using extension)"""
        extension = file_path.suffix
        return self.get_client_by_extension(extension)
    
    def get_default_client(self) -> Optional[LspClient]:
        """Get the first LSP client as default"""
        return next(iter(self._clients.values()), None)
    
    def get_all_clients(self) -> list[LspClient]:
        """Get all LSP clients"""
        return list(self._clients.values())
    
    async def dispose_all(self) -> None:
        """Dispose all LSP clients"""
        for client in self._clients.values():
            await client.dispose()
```

### 5. Tool Implementation Example (tools/textdocument.py)

```python
from pathlib import Path
from pydantic import BaseModel, Field
from mcp.server.mcpserver import MCPServer
from lsprotocol import types

from ..server import get_lsp_manager

class HoverParams(BaseModel):
    """Parameters for textDocument/hover"""
    file: Path = Field(description="Path to the Python file")
    line: int = Field(description="Line number (0-indexed)", ge=0)
    character: int = Field(description="Character position (0-indexed)", ge=0)

class DefinitionParams(BaseModel):
    """Parameters for textDocument/definition"""
    file: Path = Field(description="Path to the Python file")
    line: int = Field(description="Line number (0-indexed)", ge=0)
    character: int = Field(description="Character position (0-indexed)", ge=0)

def register_textdocument_tools(mcp: MCPServer) -> None:
    """Register textDocument/* LSP method tools"""
    
    @mcp.tool()
    async def textDocument_hover(params: HoverParams) -> dict:
        """Get hover information for a code element.
        
        Returns information like type, documentation, and value when you hover
        over a symbol in the code.
        """
        manager = get_lsp_manager()
        
        # Get appropriate LSP client
        client = manager.get_client_by_file(params.file)
        if not client:
            raise ValueError(f"No LSP server configured for {params.file}")
        
        # Open file in LSP
        uri = await client.open_file(params.file)
        
        # Send hover request
        result = await client.send_request(
            types.TEXT_DOCUMENT_HOVER,
            types.HoverParams(
                text_document=types.TextDocumentIdentifier(uri=uri),
                position=types.Position(line=params.line, character=params.character)
            )
        )
        
        return result.model_dump() if result else {}
    
    @mcp.tool()
    async def textDocument_definition(params: DefinitionParams) -> dict:
        """Go to definition of a symbol.
        
        Returns the location(s) where a symbol is defined, useful for
        navigating code and understanding symbol origins.
        """
        manager = get_lsp_manager()
        
        client = manager.get_client_by_file(params.file)
        if not client:
            raise ValueError(f"No LSP server configured for {params.file}")
        
        uri = await client.open_file(params.file)
        
        result = await client.send_request(
            types.TEXT_DOCUMENT_DEFINITION,
            types.DefinitionParams(
                text_document=types.TextDocumentIdentifier(uri=uri),
                position=types.Position(line=params.line, character=params.character)
            )
        )
        
        return result.model_dump() if result else {}
```

### 6. Configuration (config.py)

```python
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
import tomllib

class LspServerConfig(BaseModel):
    """Configuration for a single LSP server"""
    id: str
    languages: list[str]
    extensions: list[str]
    command: str
    args: list[str] = Field(default_factory=list)

class Config(BaseModel):
    """Main configuration"""
    workspace: Path = Field(default=Path("/"))
    lsp_servers: list[LspServerConfig]
    enabled_methods: Optional[list[str]] = None

def load_config(config_path: Path) -> Config:
    """Load configuration from TOML file"""
    with open(config_path, "rb") as f:
        data = tomllib.load(f)
    
    return Config(**data)

def create_simple_config(command: str, workspace: Path) -> Config:
    """Create a simple single-LSP configuration"""
    return Config(
        workspace=workspace,
        lsp_servers=[
            LspServerConfig(
                id="pylsp",
                languages=["python"],
                extensions=[".py"],
                command=command,
                args=[]
            )
        ]
    )
```

## Configuration Format

### example.toml
```toml
workspace = "/path/to/workspace"

[[lsp_servers]]
id = "pylsp"
languages = ["python"]
extensions = [".py", ".pyi"]
command = "pylsp"
args = []

[[lsp_servers]]
id = "pyright"
languages = ["python"]
extensions = [".py", ".pyi"]
command = "pyright-langserver"
args = ["--stdio"]

# Optional: filter enabled methods
enabled_methods = [
    "textDocument/hover",
    "textDocument/definition",
    "textDocument/references",
    "textDocument/documentSymbol"
]
```

## Implementation Plan

### Phase 1: Foundation
1. ✅ Project structure
2. ✅ Configuration system
3. ✅ LSP client wrapper
4. ✅ LSP manager

### Phase 2: Core Tools
5. textDocument/hover
6. textDocument/definition
7. textDocument/references
8. textDocument/documentSymbol

### Phase 3: Additional Tools
9. textDocument/completion
10. textDocument/signatureHelp
11. textDocument/formatting
12. workspace/symbol

### Phase 4: Polish
13. Testing
14. Documentation
15. Error handling
16. Performance optimization

## Key Design Decisions

### 1. Decorator-based Tools
**Decision**: Use `@mcp.tool()` decorators
**Rationale**: Pythonic, clean, automatic schema generation

### 2. Pydantic Models
**Decision**: Use Pydantic for all input/output
**Rationale**: Runtime validation, automatic docs, type safety

### 3. Async All the Way
**Decision**: Full async/await pattern
**Rationale**: LSP operations are I/O bound, better performance

### 4. TOML Configuration
**Decision**: Use TOML instead of JSON
**Rationale**: More Pythonic, better for humans, comments supported

### 5. pygls for LSP
**Decision**: Use pygls library
**Rationale**: Well-maintained, full LSP implementation, Python-native

### 6. Focus on Python Only
**Decision**: Support only Python LSP servers
**Rationale**: Simpler, more focused, better Python developer experience

## Next Steps

1. Set up pyproject.toml with dependencies
2. Implement LSP client wrapper
3. Implement LSP manager
4. Create first tool (textDocument/hover)
5. Test with real Python project
6. Iterate and expand
