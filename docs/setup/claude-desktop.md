# Claude Desktop Setup

Configure Python LSP-MCP server for use with Claude Desktop.

## Prerequisites

- Claude Desktop app installed
- Python 3.12+ installed
- `pylsp` or `pyright` language server installed

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install python-lsp-mcp
# or with uv
uv pip install python-lsp-mcp
```

### Option 2: Install from GitHub

```bash
pip install git+https://github.com/yourusername/python-lsp-mcp.git
# or with uv
uv pip install git+https://github.com/yourusername/python-lsp-mcp.git
```

### Option 3: Local Development Install

```bash
git clone https://github.com/yourusername/python-lsp-mcp.git
cd python-lsp-mcp
pip install -e .
```

## Install LSP Server

Choose your preferred Python LSP server:

```bash
# pylsp (recommended)
pip install python-lsp-server

# or pyright
npm install -g pyright
```

## Configuration

### Location

Claude Desktop configuration file location:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Basic Configuration

Edit your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "python-lsp": {
      "command": "python-lsp-mcp",
      "args": ["--lsp-command", "pylsp"]
    }
  }
}
```

### Advanced Configuration with Config File

Create a config file (e.g., `~/.config/python-lsp-mcp/config.toml`):

```toml
workspace = "/path/to/your/python/projects"

[[lsps]]
id = "pylsp"
command = "pylsp"
args = []
extensions = [".py", ".pyi"]
languages = ["python"]
```

Then update `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "python-lsp": {
      "command": "python-lsp-mcp",
      "args": ["--config", "/Users/you/.config/python-lsp-mcp/config.toml"]
    }
  }
}
```

### Using Virtual Environment

If Python LSP-MCP is in a virtual environment:

```json
{
  "mcpServers": {
    "python-lsp": {
      "command": "/path/to/venv/bin/python-lsp-mcp",
      "args": ["--lsp-command", "pylsp", "--workspace", "/path/to/workspace"]
    }
  }
}
```

### Multiple LSP Servers

Use a config file for multiple language servers:

```toml
workspace = "/path/to/workspace"

[[lsps]]
id = "pylsp"
command = "pylsp"
args = []
extensions = [".py"]
languages = ["python"]

[[lsps]]
id = "pyright"
command = "pyright-langserver"
args = ["--stdio"]
extensions = [".py"]
languages = ["python"]
```

## Restart Claude Desktop

After editing the configuration:

1. **Quit** Claude Desktop completely (not just close window)
2. **Restart** Claude Desktop
3. The MCP server will start automatically when needed

## Verify Setup

1. Open Claude Desktop
2. Start a conversation
3. Ask: "What MCP tools are available?"
4. You should see Python LSP tools like:
   - `textDocument_hover`
   - `textDocument_definition`
   - `textDocument_references`
   - `textDocument_documentSymbol`
   - `textDocument_completion`
   - `lsp_info`

## Test the Integration

Try these commands in Claude:

```
Can you show me the hover information for line 10, character 5 in /path/to/file.py?

Find the definition of the function at line 20 in my_module.py

Show me all references to the class Calculator in project.py

Get the document structure of utils.py
```

## Troubleshooting

### Server Not Starting

Check Claude Desktop logs:
- **macOS**: `~/Library/Logs/Claude/mcp*.log`
- **Windows**: `%APPDATA%\Claude\logs\mcp*.log`
- **Linux**: `~/.local/state/Claude/logs/mcp*.log`

### Common Issues

**Issue**: `python-lsp-mcp: command not found`
- **Solution**: Use full path to executable or ensure it's in PATH

**Issue**: LSP server not responding
- **Solution**: Test LSP server independently: `pylsp --version`

**Issue**: No tools appear
- **Solution**: Check JSON syntax in config file, restart Claude Desktop

### Debug Mode

Enable verbose logging:

```json
{
  "mcpServers": {
    "python-lsp": {
      "command": "python-lsp-mcp",
      "args": ["--lsp-command", "pylsp", "--verbose"]
    }
  }
}
```

## Available Tools

### textDocument_hover
Get hover information (types, docs) at a position.

**Parameters**:
- `file`: Path to Python file
- `line`: Line number (0-indexed)
- `character`: Character position (0-indexed)
- `lsp_id`: (Optional) Specific LSP server to use

### textDocument_definition
Go to symbol definition.

**Parameters**: Same as hover

### textDocument_references
Find all references to a symbol.

**Parameters**: Same as hover

### textDocument_documentSymbol
Get document structure (classes, functions, variables).

**Parameters**:
- `file`: Path to Python file
- `lsp_id`: (Optional) LSP server ID

### textDocument_completion
Get code completion suggestions.

**Parameters**: Same as hover

### lsp_info
Get information about configured LSP servers.

**Parameters**:
- `lsp_id`: (Optional) Specific LSP server ID

## Example Workflows

### Code Exploration

```
1. Ask Claude: "Show me the structure of utils.py"
   → Uses textDocument_documentSymbol

2. "What's the type of the calculate function at line 25?"
   → Uses textDocument_hover

3. "Where is the Logger class defined?"
   → Uses textDocument_definition

4. "Find all usages of the database connection"
   → Uses textDocument_references
```

### Code Completion

```
Ask: "What completions are available at line 50, character 10 in main.py?"
→ Uses textDocument_completion to suggest variables, functions, classes
```

## Next Steps

- Configure workspace paths for your projects
- Install additional LSP servers if needed
- Explore Python-specific features
- Check out the [Publishing Guide](../publishing.md) if you want to share your setup

## Support

- Issues: https://github.com/yourusername/python-lsp-mcp/issues
- Discussions: https://github.com/yourusername/python-lsp-mcp/discussions
- MCP Documentation: https://modelcontextprotocol.io
