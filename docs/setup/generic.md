# Generic MCP Client Setup

Configure Python LSP-MCP server for any MCP-compatible client.

## Overview

Python LSP-MCP follows the [Model Context Protocol](https://modelcontextprotocol.io) specification and works with any compliant MCP client.

## Prerequisites

- Python 3.12+ installed
- LSP server installed (`pylsp`, `pyright`, etc.)
- MCP client installed

## Installation

### From PyPI

```bash
pip install python-lsp-mcp
# or
uv pip install python-lsp-mcp
```

### From GitHub

```bash
pip install git+https://github.com/yourusername/python-lsp-mcp.git
```

### From Source

```bash
git clone https://github.com/yourusername/python-lsp-mcp.git
cd python-lsp-mcp
pip install -e .
```

## Install LSP Server

```bash
# Python LSP Server (pylsp)
pip install python-lsp-server

# or Pyright
npm install -g pyright

# or both
pip install python-lsp-server && npm install -g pyright
```

## Configuration

### MCP Configuration Format

Python LSP-MCP uses standard MCP configuration:

```json
{
  "mcpServers": {
    "python-lsp": {
      "command": "python-lsp-mcp",
      "args": ["--lsp-command", "pylsp"],
      "env": {}
    }
  }
}
```

### Command-Line Arguments

```bash
python-lsp-mcp --help

Options:
  --config, -c CONFIG              Path to TOML configuration file
  --workspace, -w WORKSPACE        Workspace root path (default: current directory)
  --lsp-command LSP_COMMAND        Single LSP command to run (e.g., 'pylsp' or 'pyright-langserver --stdio')
  --verbose, -v                    Enable verbose logging
```

### Using Config File

Create a TOML configuration file:

```toml
# config.toml
workspace = "/path/to/workspace"

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

# Optional: limit exposed methods
methods = [
  "textDocument/hover",
  "textDocument/definition",
  "textDocument/references",
  "textDocument/documentSymbol",
  "textDocument/completion"
]
```

Then use with MCP client:

```json
{
  "mcpServers": {
    "python-lsp": {
      "command": "python-lsp-mcp",
      "args": ["--config", "/path/to/config.toml"]
    }
  }
}
```

### Inline Configuration

Quick setup without config file:

```json
{
  "mcpServers": {
    "python-lsp": {
      "command": "python-lsp-mcp",
      "args": [
        "--lsp-command", "pylsp",
        "--workspace", "/path/to/workspace"
      ]
    }
  }
}
```

## MCP Protocol Details

### Transport

Python LSP-MCP uses **stdio transport** (standard input/output):

- **Input**: JSON-RPC messages via stdin
- **Output**: JSON-RPC responses via stdout
- **Logging**: Errors/warnings via stderr

### Capabilities

Server exposes these MCP capabilities:

```json
{
  "capabilities": {
    "tools": {
      "listChanged": false
    }
  }
}
```

### Available Tools

#### 1. textDocument_hover

Get hover information (types, documentation) at a position.

**Input Schema**:
```json
{
  "file": "string (required)",
  "line": "integer (required, 0-indexed)",
  "character": "integer (required, 0-indexed)",
  "lsp_id": "string (optional)"
}
```

**Example**:
```json
{
  "name": "textDocument_hover",
  "arguments": {
    "file": "/workspace/src/utils.py",
    "line": 10,
    "character": 5
  }
}
```

#### 2. textDocument_definition

Navigate to symbol definition.

**Input Schema**: Same as hover

**Example**:
```json
{
  "name": "textDocument_definition",
  "arguments": {
    "file": "/workspace/src/main.py",
    "line": 25,
    "character": 10
  }
}
```

#### 3. textDocument_references

Find all references to a symbol.

**Input Schema**: Same as hover

#### 4. textDocument_documentSymbol

Get document structure (classes, functions, variables).

**Input Schema**:
```json
{
  "file": "string (required)",
  "lsp_id": "string (optional)"
}
```

#### 5. textDocument_completion

Get code completion suggestions.

**Input Schema**: Same as hover

#### 6. lsp_info

Get information about LSP servers.

**Input Schema**:
```json
{
  "lsp_id": "string (optional)"
}
```

## Testing the Server

### Using MCP Inspector

```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Test the server
mcp-inspector python-lsp-mcp --lsp-command pylsp
```

### Manual Testing

Test via stdio:

```bash
# Start server
python-lsp-mcp --lsp-command pylsp --verbose

# Send initialize request (stdin)
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"capabilities":{}}}

# Send tool list request
{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}

# Call a tool
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"lsp_info","arguments":{}}}
```

### Using Python

```python
import asyncio
import json
import subprocess

async def test_mcp_server():
    # Start server
    proc = await asyncio.create_subprocess_exec(
        "python-lsp-mcp",
        "--lsp-command", "pylsp",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    )
    
    # Send initialize
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {"capabilities": {}}
    }
    proc.stdin.write(json.dumps(request).encode() + b"\n")
    await proc.stdin.drain()
    
    # Read response
    response = await proc.stdout.readline()
    print(json.loads(response))

asyncio.run(test_mcp_server())
```

## Environment Variables

Control server behavior via environment:

```bash
# Disable buffering for immediate output
export PYTHONUNBUFFERED=1

# Custom Python path
export PYTHONPATH=/custom/path

# LSP server environment
export LSP_CUSTOM_VAR=value
```

In MCP configuration:

```json
{
  "mcpServers": {
    "python-lsp": {
      "command": "python-lsp-mcp",
      "args": ["--lsp-command", "pylsp"],
      "env": {
        "PYTHONUNBUFFERED": "1",
        "PYTHONPATH": "/custom/path"
      }
    }
  }
}
```

## Security Considerations

### File Access

- Server only accesses files within configured workspace
- Use `--workspace` to restrict file access scope
- LSP servers may have additional file access restrictions

### Command Execution

- Only executes configured LSP server commands
- LSP commands should be from trusted sources
- Avoid untrusted LSP servers

### Sandboxing

For enhanced security:

```bash
# Run in Docker container
docker run -it \
  -v /workspace:/workspace:ro \
  python:3.12 \
  python-lsp-mcp --workspace /workspace
```

## Performance Tuning

### Startup Time

Minimize startup time:

```toml
# Only enable needed LSP servers
[[lsps]]
id = "pylsp"
command = "pylsp"
extensions = [".py"]
languages = ["python"]

# Limit methods
methods = ["textDocument/hover", "textDocument/definition"]
```

### Memory Usage

Control LSP server memory:

```bash
# Configure pylsp memory limit
python-lsp-mcp --lsp-command "pylsp --max-workers 2"
```

### Concurrent Requests

Server handles concurrent requests efficiently:
- Async LSP communication
- Non-blocking I/O
- Parallel tool execution

## Error Handling

### Graceful Degradation

If LSP server fails:
- Server continues running
- Error returned in tool response
- Other tools remain functional

### Logging

View detailed logs:

```bash
python-lsp-mcp --verbose 2> lsp-mcp.log
```

Log levels:
- `INFO`: Normal operations
- `WARNING`: Recoverable issues
- `ERROR`: Failed operations

## Client Implementation Guide

### Minimum Requirements

Your MCP client needs:

1. **JSON-RPC 2.0** support
2. **stdio transport** capability
3. **MCP protocol** implementation

### Example Client Flow

```
1. Start server via subprocess
2. Send "initialize" request
3. Send "tools/list" to discover tools
4. Send "tools/call" to execute tools
5. Handle responses
6. Send "shutdown" when done
```

### Reference Implementations

- **Claude Desktop**: Electron-based client
- **VS Code**: Extension-based integration
- **Cursor**: Native IDE integration

## Troubleshooting

### Server Won't Start

```bash
# Check Python version
python --version  # Should be 3.12+

# Check installation
pip show python-lsp-mcp

# Test directly
python-lsp-mcp --help
```

### LSP Server Issues

```bash
# Test LSP independently
pylsp --help
pyright --help

# Check LSP server logs
python-lsp-mcp --verbose --lsp-command pylsp 2>&1 | grep ERROR
```

### Communication Problems

```bash
# Enable verbose logging
python-lsp-mcp --verbose --lsp-command pylsp 2> debug.log

# Check JSON-RPC messages
tail -f debug.log
```

## Next Steps

- Read [Publishing Guide](../publishing.md) to distribute your server
- Check specific client setups: [Claude](./claude-desktop.md), [VS Code](./vscode.md), [Cursor](./cursor.md)
- Review [MCP Specification](https://modelcontextprotocol.io/specification)

## Support

- GitHub Issues: https://github.com/yourusername/python-lsp-mcp/issues
- MCP Community: https://github.com/modelcontextprotocol/servers/discussions
- Protocol Documentation: https://modelcontextprotocol.io
