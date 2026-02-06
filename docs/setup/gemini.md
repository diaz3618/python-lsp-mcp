# Google Gemini Setup

Configure Python LSP-MCP server for use with Google Gemini API and Gemini Code Assist.

## Prerequisites

- Python 3.12+ installed
- Google Cloud account with Gemini API access
- `pylsp` or `pyright` language server installed
- Gemini SDK or compatible client

## Installation

```bash
# Install python-lsp-mcp
pip install python-lsp-mcp

# Install LSP server
pip install python-lsp-server

# Install Gemini SDK (if using programmatically)
pip install google-generativeai
```

## Configuration

### For Gemini Code Assist (IDE Extension)

If using Gemini Code Assist in VS Code or JetBrains:

**Location**: Extension settings or `.vscode/mcp.json`

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

### For Gemini API Integration

When building custom integration with Gemini API:

```python
# example_gemini_integration.py
import google.generativeai as genai
import subprocess
import json

# Configure Gemini
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-pro')

# Start MCP server
mcp_process = subprocess.Popen(
    ["python-lsp-mcp", "--lsp-command", "pylsp"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Initialize MCP server
init_request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {"capabilities": {}}
}
mcp_process.stdin.write(json.dumps(init_request).encode() + b"\n")
mcp_process.stdin.flush()

# Get tools
tools_request = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
}
mcp_process.stdin.write(json.dumps(tools_request).encode() + b"\n")
mcp_process.stdin.flush()

# Read available tools
response = json.loads(mcp_process.stdout.readline())
print(f"Available tools: {response}")
```

### Using Config File

Create `gemini-config.toml`:

```toml
workspace = "/path/to/your/python/project"

[[lsps]]
id = "pylsp"
command = "pylsp"
args = []
extensions = [".py", ".pyi"]
languages = ["python"]

# Optimize for Gemini's context window
methods = [
  "textDocument/hover",
  "textDocument/definition",
  "textDocument/references"
]
```

## Integration Patterns

### Pattern 1: Function Calling with MCP Tools

Convert MCP tools to Gemini function declarations:

```python
import google.generativeai as genai

# Define Gemini function based on MCP tool
hover_function = genai.protos.FunctionDeclaration(
    name="textDocument_hover",
    description="Get type information and documentation for code at a specific position",
    parameters={
        "type": "object",
        "properties": {
            "file": {
                "type": "string",
                "description": "Path to Python file"
            },
            "line": {
                "type": "integer",
                "description": "Line number (0-indexed)"
            },
            "character": {
                "type": "integer",
                "description": "Character position (0-indexed)"
            }
        },
        "required": ["file", "line", "character"]
    }
)

# Create tool config
tool_config = genai.protos.Tool(
    function_declarations=[hover_function]
)

# Use with Gemini
model = genai.GenerativeModel('gemini-pro', tools=[tool_config])
```

### Pattern 2: MCP Server as Context Provider

Use MCP server to provide code context to Gemini:

```python
async def get_code_context(file_path: str, line: int) -> str:
    """Get code context via MCP for Gemini."""
    
    # Call MCP hover tool
    hover_result = await call_mcp_tool(
        "textDocument_hover",
        {"file": file_path, "line": line, "character": 0}
    )
    
    # Call MCP documentSymbol tool
    symbols_result = await call_mcp_tool(
        "textDocument_documentSymbol",
        {"file": file_path}
    )
    
    # Format for Gemini
    context = f"""
    Code Context:
    - Type Information: {hover_result}
    - File Structure: {symbols_result}
    """
    
    return context

# Use with Gemini
async def analyze_with_context(file_path: str, query: str):
    context = await get_code_context(file_path, 10)
    
    response = model.generate_content(f"{context}\n\nQuery: {query}")
    return response.text
```

### Pattern 3: Agentic Workflow

Build agent that uses MCP tools via Gemini:

```python
from typing import Optional
import asyncio

class GeminiMCPAgent:
    def __init__(self, mcp_server, gemini_model):
        self.mcp = mcp_server
        self.model = gemini_model
    
    async def analyze_code(self, file_path: str) -> dict:
        """Multi-step code analysis using Gemini + MCP."""
        
        # Step 1: Get structure
        structure = await self.mcp.call_tool(
            "textDocument_documentSymbol",
            {"file": file_path}
        )
        
        # Step 2: Ask Gemini to identify interesting parts
        prompt = f"Given this code structure: {structure}, which functions should I analyze in detail?"
        interesting = self.model.generate_content(prompt)
        
        # Step 3: Get detailed info for each
        details = []
        for location in self.parse_locations(interesting.text):
            hover = await self.mcp.call_tool(
                "textDocument_hover",
                {"file": file_path, "line": location["line"], "character": 0}
            )
            details.append(hover)
        
        # Step 4: Synthesize with Gemini
        final_prompt = f"Analyze: {details}"
        analysis = self.model.generate_content(final_prompt)
        
        return {
            "structure": structure,
            "details": details,
            "analysis": analysis.text
        }
```

## Gemini Code Assist Extension

For Gemini Code Assist in VS Code:

### Extension Settings

1. Open VS Code Settings
2. Search for "Gemini Code Assist"
3. Enable "MCP Servers"
4. Add MCP configuration:

```json
{
  "gemini.mcp.servers": {
    "python-lsp": {
      "command": "python-lsp-mcp",
      "args": ["--lsp-command", "pylsp", "--workspace", "${workspaceFolder}"]
    }
  }
}
```

### Usage in Gemini Chat

```
Ask Gemini: "Show me the type of the function at line 25 of utils.py"
→ Gemini uses textDocument_hover tool

Ask: "Where is the Database class defined?"
→ Gemini uses textDocument_definition tool

Ask: "Refactor this function based on its actual usage"
→ Gemini uses textDocument_references tool
```

## Optimization for Gemini

### Context Window Management

Gemini has context window limits. Optimize MCP responses:

```toml
# gemini-optimized-config.toml
workspace = "."

[[lsps]]
id = "pylsp"
command = "pylsp"
args = []
extensions = [".py"]
languages = ["python"]

# Only essential methods to save tokens
methods = [
  "textDocument/hover",
  "textDocument/definition"
]
```

### Response Filtering

Filter MCP responses to reduce token usage:

```python
def filter_for_gemini(mcp_response: dict) -> str:
    """Extract essential info for Gemini's context window."""
    
    if "hover" in mcp_response:
        # Extract just type and first line of docs
        content = mcp_response["hover"]["contents"]
        if isinstance(content, dict):
            return content.get("value", "").split("\n")[0]
    
    if "definition" in mcp_response:
        # Just file and line, not full content
        loc = mcp_response["definition"][0]
        return f"{loc['uri']}:{loc['range']['start']['line']}"
    
    return str(mcp_response)[:500]  # Truncate to 500 chars
```

## Authentication

### Google Cloud Authentication

```bash
# Set up Google Cloud credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# Or use gcloud
gcloud auth application-default login
```

### API Key Method

```python
import os
import google.generativeai as genai

# From environment
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
```

## Troubleshooting

### Gemini Not Calling MCP Tools

**Issue**: Gemini doesn't use MCP tools

**Solution**:
1. Ensure function declarations match MCP tool schemas
2. Use clear descriptions in function declarations
3. Prompt Gemini explicitly: "Use the textDocument_hover tool to check types"

### Rate Limiting

**Issue**: Gemini API rate limits

**Solution**:
```python
import time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def call_gemini_with_retry(prompt: str):
    return await model.generate_content_async(prompt)
```

### Context Window Exceeded

**Issue**: Too much context for Gemini

**Solution**:
- Use `methods` filter in config to limit tools
- Implement response filtering
- Cache and reuse previous results
- Use Gemini 1.5 Pro (larger context window)

## Example: Complete Integration

```python
#!/usr/bin/env python3
"""Complete Gemini + Python LSP-MCP integration example."""

import asyncio
import json
import subprocess
from typing import Optional
import google.generativeai as genai

class GeminiLSPIntegration:
    def __init__(self, api_key: str, workspace: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.mcp_process = None
        self.workspace = workspace
        self.request_id = 0
    
    async def start(self):
        """Start MCP server."""
        self.mcp_process = await asyncio.create_subprocess_exec(
            "python-lsp-mcp",
            "--lsp-command", "pylsp",
            "--workspace", self.workspace,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Initialize
        await self._send_request("initialize", {"capabilities": {}})
    
    async def _send_request(self, method: str, params: dict) -> dict:
        """Send JSON-RPC request to MCP server."""
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params
        }
        
        self.mcp_process.stdin.write(json.dumps(request).encode() + b"\n")
        await self.mcp_process.stdin.drain()
        
        response_line = await self.mcp_process.stdout.readline()
        return json.loads(response_line)
    
    async def call_tool(self, tool_name: str, arguments: dict) -> str:
        """Call MCP tool."""
        response = await self._send_request(
            "tools/call",
            {"name": tool_name, "arguments": arguments}
        )
        return response.get("result", {})
    
    async def analyze_code(self, file_path: str, user_query: str) -> str:
        """Analyze code using Gemini + MCP tools."""
        
        # Get code structure
        structure = await self.call_tool(
            "textDocument_documentSymbol",
            {"file": file_path}
        )
        
        # Build context for Gemini
        context = f"""
        Code Structure: {json.dumps(structure, indent=2)}
        
        Available tools:
        - textDocument_hover: Get type info at position
        - textDocument_definition: Find where symbol is defined
        - textDocument_references: Find all usages
        
        User Query: {user_query}
        
        Analyze the code and answer the query.
        """
        
        # Ask Gemini
        response = self.model.generate_content(context)
        return response.text
    
    async def stop(self):
        """Stop MCP server."""
        if self.mcp_process:
            await self._send_request("shutdown", {})
            self.mcp_process.terminate()
            await self.mcp_process.wait()

# Usage
async def main():
    integration = GeminiLSPIntegration(
        api_key="YOUR_API_KEY",
        workspace="/path/to/workspace"
    )
    
    await integration.start()
    
    result = await integration.analyze_code(
        "/path/to/workspace/src/main.py",
        "What are the main functions and their types?"
    )
    
    print(result)
    
    await integration.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

## Next Steps

- Review [Generic Setup](./generic.md) for more MCP details
- Check [Publishing Guide](../publishing.md) for distribution
- Explore [Gemini API Documentation](https://ai.google.dev/docs)

## Support

- Gemini API: https://ai.google.dev/docs
- Python LSP-MCP: https://github.com/yourusername/python-lsp-mcp/issues
- MCP Protocol: https://modelcontextprotocol.io
