# OpenAI Codex Setup

Configure Python LSP-MCP server for use with OpenAI Codex and GPT models.

## Prerequisites

- Python 3.12+ installed
- OpenAI API key
- `pylsp` or `pyright` language server installed
- OpenAI Python SDK

## Installation

```bash
# Install python-lsp-mcp
pip install python-lsp-mcp

# Install LSP server
pip install python-lsp-server

# Install OpenAI SDK
pip install openai
```

## Configuration

### For OpenAI API Integration

When building custom integration with OpenAI:

```python
# openai_mcp_config.py
import openai
import subprocess
import json

# Configure OpenAI
openai.api_key = "YOUR_API_KEY"

# Start MCP server
mcp_process = subprocess.Popen(
    ["python-lsp-mcp", "--lsp-command", "pylsp", "--workspace", "/path/to/workspace"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
```

### Using Config File

Create `codex-config.toml`:

```toml
workspace = "/path/to/your/python/project"

[[lsps]]
id = "pylsp"
command = "pylsp"
args = []
extensions = [".py", ".pyi"]
languages = ["python"]

# Optimize for Codex
methods = [
  "textDocument/hover",
  "textDocument/definition",
  "textDocument/references",
  "textDocument/documentSymbol",
  "textDocument/completion"
]
```

## Integration with OpenAI Function Calling

### Convert MCP Tools to OpenAI Functions

```python
from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")

# Define MCP tools as OpenAI functions
tools = [
    {
        "type": "function",
        "function": {
            "name": "textDocument_hover",
            "description": "Get type information and documentation for code at a specific position in a Python file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "description": "Absolute path to the Python file"
                    },
                    "line": {
                        "type": "integer",
                        "description": "Line number (0-indexed)"
                    },
                    "character": {
                        "type": "integer",
                        "description": "Character position in the line (0-indexed)"
                    }
                },
                "required": ["file", "line", "character"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "textDocument_definition",
            "description": "Find where a symbol is defined",
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "File path"},
                    "line": {"type": "integer", "description": "Line number (0-indexed)"},
                    "character": {"type": "integer", "description": "Character position (0-indexed)"}
                },
                "required": ["file", "line", "character"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "textDocument_references",
            "description": "Find all references to a symbol",
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string"},
                    "line": {"type": "integer"},
                    "character": {"type": "integer"}
                },
                "required": ["file", "line", "character"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "textDocument_documentSymbol",
            "description": "Get the structure of a Python file (classes, functions, variables)",
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "description": "Path to Python file"
                    }
                },
                "required": ["file"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "textDocument_completion",
            "description": "Get code completion suggestions at a position",
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {"type": "string"},
                    "line": {"type": "integer"},
                    "character": {"type": "integer"}
                },
                "required": ["file", "line", "character"]
            }
        }
    }
]
```

### Complete Integration Example

```python
#!/usr/bin/env python3
"""OpenAI GPT-4 + Python LSP-MCP integration."""

import asyncio
import json
import subprocess
from typing import Optional, List, Dict
from openai import OpenAI

class OpenAIMCPIntegration:
    def __init__(self, api_key: str, workspace: str):
        self.client = OpenAI(api_key=api_key)
        self.mcp_process = None
        self.workspace = workspace
        self.request_id = 0
        self.conversation_history = []
    
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
        
        # Initialize MCP
        await self._send_mcp_request("initialize", {"capabilities": {}})
    
    async def _send_mcp_request(self, method: str, params: dict) -> dict:
        """Send request to MCP server."""
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
    
    async def call_mcp_tool(self, tool_name: str, arguments: dict) -> dict:
        """Call MCP tool and return result."""
        response = await self._send_mcp_request(
            "tools/call",
            {"name": tool_name, "arguments": arguments}
        )
        return response.get("result", {})
    
    def chat(self, user_message: str, tools: List[dict]) -> str:
        """Chat with OpenAI using MCP tools."""
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Call OpenAI with tools
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=self.conversation_history,
            tools=tools,
            tool_choice="auto"
        )
        
        return response
    
    async def chat_with_tools(self, user_message: str) -> str:
        """Complete chat loop with tool execution."""
        
        tools = self._get_openai_tools()
        
        while True:
            response = self.chat(user_message, tools)
            message = response.choices[0].message
            
            # If no tool calls, return response
            if not message.tool_calls:
                self.conversation_history.append({
                    "role": "assistant",
                    "content": message.content
                })
                return message.content
            
            # Execute tool calls
            self.conversation_history.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": message.tool_calls
            })
            
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                # Call MCP tool
                result = await self.call_mcp_tool(tool_name, arguments)
                
                # Add tool result to history
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })
            
            # Continue conversation with tool results
            user_message = ""  # Empty for continuation
    
    def _get_openai_tools(self) -> List[dict]:
        """Get OpenAI-formatted tool definitions."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "textDocument_hover",
                    "description": "Get type and documentation at position",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file": {"type": "string"},
                            "line": {"type": "integer"},
                            "character": {"type": "integer"}
                        },
                        "required": ["file", "line", "character"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "textDocument_definition",
                    "description": "Find symbol definition",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file": {"type": "string"},
                            "line": {"type": "integer"},
                            "character": {"type": "integer"}
                        },
                        "required": ["file", "line", "character"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "textDocument_documentSymbol",
                    "description": "Get file structure",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file": {"type": "string"}
                        },
                        "required": ["file"]
                    }
                }
            }
        ]
    
    async def stop(self):
        """Stop MCP server."""
        if self.mcp_process:
            await self._send_mcp_request("shutdown", {})
            self.mcp_process.terminate()
            await self.mcp_process.wait()

# Usage
async def main():
    integration = OpenAIMCPIntegration(
        api_key="YOUR_API_KEY",
        workspace="/path/to/workspace"
    )
    
    await integration.start()
    
    # Chat with tool support
    response = await integration.chat_with_tools(
        "What's the type of the function at line 25 in src/main.py?"
    )
    
    print(response)
    
    # Follow-up question
    response = await integration.chat_with_tools(
        "Where is that function defined?"
    )
    
    print(response)
    
    await integration.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

## Assistants API Integration

Use with OpenAI Assistants:

```python
from openai import OpenAI

client = OpenAI()

# Create assistant with MCP tools
assistant = client.beta.assistants.create(
    name="Python Code Analyzer",
    instructions="You are a Python code analysis assistant with access to LSP tools.",
    model="gpt-4",
    tools=[
        # Add MCP tool definitions here
        {"type": "function", "function": {...}}
    ]
)

# Create thread
thread = client.beta.threads.create()

# Add message
client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Analyze the code structure of main.py"
)

# Run with tool execution
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id
)
```

## Code Completion with Codex

Enhance Codex completions with LSP context:

```python
async def get_completion_with_context(file_path: str, line: int, char: int) -> str:
    """Get Codex completion enhanced with LSP context."""
    
    # Get LSP hover info for context
    hover_result = await call_mcp_tool(
        "textDocument_hover",
        {"file": file_path, "line": line, "character": char}
    )
    
    # Get document structure
    symbols = await call_mcp_tool(
        "textDocument_documentSymbol",
        {"file": file_path}
    )
    
    # Read file content
    with open(file_path) as f:
        code = f.read()
    
    # Build prompt with context
    prompt = f"""
    File: {file_path}
    Structure: {json.dumps(symbols, indent=2)}
    Current Position: Line {line}, Char {char}
    Type Context: {hover_result}
    
    Code:
    {code}
    
    Complete the code at the cursor position.
    """
    
    # Get Codex completion
    response = client.completions.create(
        model="code-davinci-002",
        prompt=prompt,
        max_tokens=150
    )
    
    return response.choices[0].text
```

## Optimization for OpenAI

### Token Management

Optimize for OpenAI's token limits:

```python
def truncate_for_openai(mcp_result: dict, max_tokens: int = 1000) -> str:
    """Truncate MCP result to fit token budget."""
    
    result_str = json.dumps(mcp_result, indent=2)
    
    # Rough estimate: 1 token ≈ 4 chars
    max_chars = max_tokens * 4
    
    if len(result_str) <= max_chars:
        return result_str
    
    # Truncate with indicator
    return result_str[:max_chars] + "\n... (truncated)"
```

### Caching Responses

Cache MCP results to reduce costs:

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
async def cached_mcp_call(tool_name: str, args_hash: str) -> dict:
    """Cache MCP tool calls."""
    arguments = json.loads(args_hash)
    return await call_mcp_tool(tool_name, arguments)

def hash_arguments(args: dict) -> str:
    """Create cache key from arguments."""
    return hashlib.md5(json.dumps(args, sort_keys=True).encode()).hexdigest()
```

## Troubleshooting

### High Token Usage

**Issue**: OpenAI costs too high

**Solution**:
- Limit methods in config to essential ones
- Truncate MCP responses
- Cache frequently accessed results
- Use GPT-3.5 instead of GPT-4 where appropriate

### Tool Not Being Called

**Issue**: OpenAI doesn't use MCP tools

**Solution**:
```python
# Be explicit in system message
system_message = {
    "role": "system",
    "content": "You have access to Python LSP tools. Always use textDocument_hover to get type information before answering questions about types."
}
```

### Rate Limiting

**Issue**: OpenAI API rate limits

**Solution**:
```python
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(5)
)
async def call_openai_with_retry(messages, tools):
    return client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=tools
    )
```

## Example Workflows

### Code Analysis Workflow

```
User: "Analyze the Database class in models.py"

1. GPT-4 calls textDocument_documentSymbol
   → Gets class structure
2. GPT-4 calls textDocument_hover on each method
   → Gets type signatures
3. GPT-4 calls textDocument_references
   → Finds usage patterns
4. GPT-4 synthesizes analysis
```

### Refactoring Assistant

```
User: "Help me refactor the calculate() function"

1. GPT-4 calls textDocument_definition
   → Locates function
2. GPT-4 calls textDocument_references
   → Finds all usages
3. GPT-4 calls textDocument_hover
   → Gets parameter types
4. GPT-4 suggests refactoring
```

## Next Steps

- Review [Generic Setup](./generic.md) for MCP fundamentals
- Check [Publishing Guide](../publishing.md) for distribution
- Explore [OpenAI API Documentation](https://platform.openai.com/docs)

## Support

- OpenAI API: https://platform.openai.com/docs
- Python LSP-MCP: https://github.com/yourusername/python-lsp-mcp/issues
- MCP Protocol: https://modelcontextprotocol.io
