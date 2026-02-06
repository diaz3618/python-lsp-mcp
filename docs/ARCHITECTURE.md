# Python LSP-MCP Server Architecture Design

## Project Overview
A Python implementation of LSP-MCP server that enables LLMs/AI agents to interact with Python Language Server Protocol (LSP) servers for language-aware context from Python codebases.

## Goals
1. Focus on Python development
2. Use Python MCP SDK native patterns (decorator-based)
3. Integrate with Python LSP servers (pylsp, pyright, jedi-language-server)
4. Simple, Pythonic, maintainable codebase
5. Support multiple Python LSP servers simultaneously

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