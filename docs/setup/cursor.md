# Cursor Setup

Configure Python LSP-MCP server for use with Cursor AI IDE.

## Prerequisites

- Cursor installed
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

Cursor uses the same configuration format as VS Code but in its own config directory.

### Location

**MCP Configuration File**:
- **macOS**: `~/.cursor/mcp.json`
- **Windows**: `%APPDATA%\Cursor\mcp.json`
- **Linux**: `~/.config/Cursor/mcp.json`

### Basic Configuration

Create or edit `~/.cursor/mcp.json`:

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

### Workspace-Specific Configuration

For project-specific settings, create `.cursor/mcp.json` in your project root:

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

### Using Virtual Environment

```json
{
  "mcpServers": {
    "python-lsp": {
      "command": "/path/to/venv/bin/python-lsp-mcp",
      "args": [
        "--lsp-command", "/path/to/venv/bin/pylsp",
        "--workspace", "${workspaceFolder}"
      ]
    }
  }
}
```

### Advanced Configuration with TOML

Create `~/.cursor/python-lsp-config.toml`:

```toml
workspace = "/path/to/default/workspace"

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
```

Then reference in `mcp.json`:

```json
{
  "mcpServers": {
    "python-lsp": {
      "command": "python-lsp-mcp",
      "args": ["--config", "~/.cursor/python-lsp-config.toml"]
    }
  }
}
```

## Cursor Settings

You may also want to configure Cursor settings in `.cursor/settings.json`:

```json
{
  "cursor.mcp.enabled": true,
  "cursor.mcp.autoStart": true
}
```

## Restart Cursor

After editing configuration:
1. **Quit** Cursor completely
2. **Restart** Cursor
3. MCP server will start automatically

## Verify Setup

### Check MCP Status

1. Open Command Palette: `Cmd/Ctrl + Shift + P`
2. Type: "MCP: Show Status" or "MCP: List Servers"
3. Verify `python-lsp` appears in the list

### Test in Chat

1. Open Cursor Chat (Cmd/Ctrl + L)
2. Type: "What MCP tools are available?"
3. Should list Python LSP tools

## Using with Cursor AI

### Chat Commands

Cursor AI can use Python LSP-MCP tools automatically:

```
Show me the hover information for the function at line 25

What's defined at this location in my code?

Find all references to the calculate_total function

Show me the structure of this Python file

Get code completions for this position
```

### Inline AI Requests

Use Cursor's inline AI (Cmd/Ctrl + K) with LSP context:

```
// Highlight code block
Cmd/Ctrl + K: "Analyze the types here using LSP hover"

Cmd/Ctrl + K: "Show me where this is defined"
```

### Composer Mode

In Composer, you can reference LSP information:

```
@python-lsp get the document structure of utils.py
then refactor based on the symbol hierarchy
```

## Project Configuration

### Per-Project Setup

Create `.cursor/mcp.json` in your project:

```json
{
  "mcpServers": {
    "python-lsp": {
      "command": "python-lsp-mcp",
      "args": [
        "--workspace", ".",
        "--lsp-command", ".venv/bin/pylsp"
      ]
    }
  }
}
```

### Share with Team

Commit to version control:

```bash
git add .cursor/mcp.json
git commit -m "Add Python LSP-MCP configuration for team"
```

Team members will automatically get the configuration when they pull.

## Troubleshooting

### Check Logs

Cursor logs location:
- **macOS**: `~/Library/Logs/Cursor/`
- **Windows**: `%APPDATA%\Cursor\logs\`
- **Linux**: `~/.config/Cursor/logs/`

Look for files starting with `mcp-`.

### Common Issues

**Issue**: Server not starting
- **Solution**: Check if `python-lsp-mcp` is in PATH
- Test: `which python-lsp-mcp` (macOS/Linux) or `where python-lsp-mcp` (Windows)

**Issue**: LSP server not responding
- **Solution**: Test LSP independently: `pylsp --help`
- Try different LSP server: `pyright --help`

**Issue**: Tools not available in chat
- **Solution**: 
  - Verify JSON syntax in mcp.json
  - Restart Cursor completely
  - Check MCP status in Command Palette

### Debug Mode

Enable verbose logging:

```json
{
  "mcpServers": {
    "python-lsp": {
      "command": "python-lsp-mcp",
      "args": [
        "--lsp-command", "pylsp",
        "--verbose"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### Reset MCP Configuration

If things get broken:

1. Backup your config
2. Delete `~/.cursor/mcp.json`
3. Restart Cursor
4. Recreate configuration

## Performance Optimization

### Limit Methods

For faster startup, limit exposed methods:

```toml
# config.toml
workspace = "."

[[lsps]]
id = "pylsp"
command = "pylsp"
args = []
extensions = [".py"]
languages = ["python"]

# Only expose commonly used methods
methods = [
  "textDocument/hover",
  "textDocument/definition",
  "textDocument/references"
]
```

### Workspace Scope

Limit workspace to specific directories:

```json
{
  "mcpServers": {
    "python-lsp": {
      "command": "python-lsp-mcp",
      "args": [
        "--workspace", "${workspaceFolder}/src",
        "--lsp-command", "pylsp"
      ]
    }
  }
}
```

## Integration Tips

### Combine with Cursor's Python Features

- **Cursor's built-in Python**: Code completion, syntax highlighting
- **Python LSP-MCP**: AI-accessible language intelligence
- Both work together without conflict

### Cursor Rules

Create `.cursorrules` to guide AI usage:

```
When analyzing Python code:
1. Use textDocument_hover for type information
2. Use textDocument_definition to understand dependencies
3. Use textDocument_documentSymbol for code structure
4. Use textDocument_references before refactoring
```

### Custom Keybindings

Add keybindings in Cursor for quick LSP queries (keybindings.json):

```json
[
  {
    "key": "cmd+shift+h",
    "command": "cursor.runCommand",
    "args": {
      "command": "Ask AI to show hover info at cursor position"
    }
  }
]
```

## Example Workflows

### Code Exploration

```
1. Open Python file
2. Cursor AI: "Show me the structure of this file"
   → Uses documentSymbol
3. Click on a function
4. Cursor AI: "What's the type signature here?"
   → Uses hover
5. "Where is this defined?"
   → Uses definition
```

### Refactoring

```
1. Select a function name
2. Cursor AI: "Find all uses of this function"
   → Uses references
3. Review results
4. Cursor AI: "Help me refactor based on these usages"
```

### Documentation

```
Cursor AI: "Generate docs for all functions in this file,
include type information from LSP hover"
```

## Advanced Features

### Multiple Projects

Configure different LSP setups per project:

```json
{
  "mcpServers": {
    "python-lsp-project1": {
      "command": "python-lsp-mcp",
      "args": ["--workspace", "/path/to/project1"]
    },
    "python-lsp-project2": {
      "command": "python-lsp-mcp",
      "args": ["--workspace", "/path/to/project2"]
    }
  }
}
```

### Environment Variables

Set environment for LSP:

```json
{
  "mcpServers": {
    "python-lsp": {
      "command": "python-lsp-mcp",
      "args": ["--lsp-command", "pylsp"],
      "env": {
        "PYTHONPATH": "/custom/path",
        "VIRTUAL_ENV": "${workspaceFolder}/.venv"
      }
    }
  }
}
```

## Next Steps

- Explore [Publishing Guide](../publishing.md)
- Check [Generic Setup](./generic.md) for other clients
- Review [Claude Desktop Setup](./claude-desktop.md) for comparison

## Support

- Cursor Community: https://cursor.sh/community
- Python LSP-MCP Issues: https://github.com/yourusername/python-lsp-mcp/issues
- MCP Specification: https://modelcontextprotocol.io
