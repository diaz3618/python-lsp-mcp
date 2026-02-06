# VS Code Setup

Configure Python LSP-MCP server for use with VS Code through GitHub Copilot Chat.

## Prerequisites

- VS Code installed
- GitHub Copilot extension installed
- Python 3.12+ installed
- `pylsp` or `pyright` language server installed

## Installation

```bash
# Install python-lsp-mcp
pip install python-lsp-mcp

# Install LSP server
pip install python-lsp-server
```

## Configuration

### MCP Settings File

VS Code uses a separate MCP configuration file.

**Location**: `.vscode/mcp.json` (workspace) or user settings

Create `.vscode/mcp.json` in your workspace:

```json
{
  "mcpServers": {
    "python-lsp": {
      "command": "python-lsp-mcp",
      "args": ["--workspace", "${workspaceFolder}"]
    }
  }
}
```

### Using Workspace Variable

```json
{
  "mcpServers": {
    "python-lsp": {
      "command": "python-lsp-mcp",
      "args": [
        "--lsp-command", "pylsp",
        "--workspace", "${workspaceFolder}"
      ]
    }
  }
}
```

### With Virtual Environment

```json
{
  "mcpServers": {
    "python-lsp": {
      "command": "${workspaceFolder}/.venv/bin/python-lsp-mcp",
      "args": [
        "--lsp-command", "${workspaceFolder}/.venv/bin/pylsp",
        "--workspace", "${workspaceFolder}"
      ]
    }
  }
}
```

### With Config File

Create `configs/python-lsp.toml`:

```toml
workspace = "."  # Will be relative to workspace root

[[lsps]]
id = "pylsp"
command = "pylsp"
args = []
extensions = [".py", ".pyi"]
languages = ["python"]
```

Then in `.vscode/mcp.json`:

```json
{
  "mcpServers": {
    "python-lsp": {
      "command": "python-lsp-mcp",
      "args": [
        "--config", "${workspaceFolder}/configs/python-lsp.toml"
      ]
    }
  }
}
```

## VS Code Settings

You may also need to configure VS Code settings in `.vscode/settings.json`:

```json
{
  "github.copilot.chat.mcp.enabled": true,
  "github.copilot.chat.mcp.configFile": ".vscode/mcp.json"
}
```

## Restart VS Code

After configuration:
1. **Reload Window**: `Cmd/Ctrl + Shift + P` → "Developer: Reload Window"
2. Or restart VS Code completely

## Verify Setup

1. Open GitHub Copilot Chat
2. Type: `@workspace /mcp list`
3. You should see `python-lsp` server with available tools

## Using in Copilot Chat

### Example Prompts

```
@workspace Can you analyze the hover info at line 25 of utils.py?

@workspace Show me the definition of calculate_total function

@workspace Find all references to DatabaseConnection class

@workspace What's the structure of the main.py file?

@workspace Get completions at line 50, character 10 in app.py
```

### Direct Tool Usage

You can also invoke tools directly:

```
@workspace Use textDocument_hover on file: src/main.py, line: 10, character: 5

@workspace Use textDocument_documentSymbol on file: src/utils.py
```

## Multi-Root Workspaces

For multi-root workspaces, create `.vscode/mcp.json` in each workspace root or use user-level configuration.

**User Settings Location**:
- **macOS**: `~/Library/Application Support/Code/User/mcp.json`
- **Windows**: `%APPDATA%\Code\User\mcp.json`
- **Linux**: `~/.config/Code/User/mcp.json`

## Troubleshooting

### Check MCP Status

1. Open Command Palette: `Cmd/Ctrl + Shift + P`
2. Run: `GitHub Copilot: Show MCP Status`
3. Check if `python-lsp` server is running

### View Logs

1. Open Output Panel: `Cmd/Ctrl + Shift + U`
2. Select "GitHub Copilot Chat" from dropdown
3. Look for MCP-related messages

### Common Issues

**Issue**: Server not found
- **Solution**: Check path to `python-lsp-mcp` executable
- Try: `which python-lsp-mcp` (macOS/Linux) or `where python-lsp-mcp` (Windows)

**Issue**: LSP server fails
- **Solution**: Test LSP independently: `pylsp --help`
- Ensure LSP server is in PATH or use full path

**Issue**: Tools not appearing
- **Solution**: Check JSON syntax, reload window, check Copilot status

### Debug Configuration

Enable verbose logging:

```json
{
  "mcpServers": {
    "python-lsp": {
      "command": "python-lsp-mcp",
      "args": [
        "--lsp-command", "pylsp",
        "--workspace", "${workspaceFolder}",
        "--verbose"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

## Per-Project Configuration

### Project-Specific Settings

Create `.vscode/mcp.json` in project root:

```json
{
  "mcpServers": {
    "python-lsp": {
      "command": "python-lsp-mcp",
      "args": [
        "--config", "${workspaceFolder}/.vscode/python-lsp-config.toml"
      ]
    }
  }
}
```

### Shared Team Configuration

Commit `.vscode/mcp.json` to version control for team sharing:

```bash
git add .vscode/mcp.json
git commit -m "Add Python LSP-MCP configuration"
```

## Integration with Python Extension

Python LSP-MCP works alongside VS Code's Python extension:

- **Python Extension**: Provides IntelliSense, debugging, testing
- **Python LSP-MCP**: Provides AI-accessible language intelligence via Copilot

Both can run simultaneously without conflict.

## Advanced Usage

### Custom LSP Configuration

Create advanced LSP config for specific project needs:

```toml
workspace = "${workspaceFolder}"

[[lsps]]
id = "pylsp"
command = "pylsp"
args = []
extensions = [".py", ".pyi"]
languages = ["python"]

# Only expose specific LSP methods
methods = [
  "textDocument/hover",
  "textDocument/definition",
  "textDocument/references"
]
```

### Environment Variables

Pass environment variables to LSP server:

```json
{
  "mcpServers": {
    "python-lsp": {
      "command": "python-lsp-mcp",
      "args": ["--lsp-command", "pylsp"],
      "env": {
        "PYTHONPATH": "${workspaceFolder}/src",
        "VIRTUAL_ENV": "${workspaceFolder}/.venv"
      }
    }
  }
}
```

## Example Workflows

### Code Review Assistant

```
@workspace Review the hover types in this file and suggest improvements

@workspace Find all references to this deprecated function

@workspace Show me the symbol hierarchy of this module
```

### Documentation Helper

```
@workspace Get hover docs for all public functions in utils.py

@workspace Map out the class structure using documentSymbol
```

### Refactoring Support

```
@workspace Find all references before I rename this variable

@workspace Show completions to help me discover available methods
```

## Next Steps

- Explore [Publishing Guide](../publishing.md) for sharing configurations
- Check [Generic Setup](./generic.md) for other MCP clients
- Read [MCP Documentation](https://modelcontextprotocol.io) for advanced features

## Support

- VS Code MCP Issues: https://github.com/microsoft/vscode/issues
- Python LSP-MCP Issues: https://github.com/yourusername/python-lsp-mcp/issues
