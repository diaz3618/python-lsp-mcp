#!/usr/bin/env python3
"""Test py-lsp-mcp tools with MCP client."""
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_tools():
    """Test all 6 tools."""
    server_params = StdioServerParameters(
        command="python-lsp-mcp",
        args=["--lsp-command", "pylsp", "--workspace", "/home/diaz/mygit/python-lsp-mcp"],
        env=None,
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Test 1: lsp_info
            print("\n=== TEST 1: lsp_info ===")
            try:
                result = await session.call_tool("lsp_info", arguments={})
                print(f"✓ lsp_info: {json.dumps(result.content[0].text[:200])}")
            except Exception as e:
                print(f"✗ lsp_info failed: {e}")
            
            # Test 2: textDocument_hover on "greet" function
            print("\n=== TEST 2: textDocument_hover (greet function) ===")
            try:
                result = await session.call_tool("textDocument_hover", arguments={
                    "file": "/home/diaz/mygit/python-lsp-mcp/test_sample.py",
                    "line": 3,
                    "character": 4
                })
                print(f"✓ hover: {result.content[0].text[:200]}...")
            except Exception as e:
                print(f"✗ hover failed: {e}")
            
            # Test 3: textDocument_definition on "greet" call
            print("\n=== TEST 3: textDocument_definition (greet call) ===")
            try:
                result = await session.call_tool("textDocument_definition", arguments={
                    "file": "/home/diaz/mygit/python-lsp-mcp/test_sample.py",
                    "line": 27,
                    "character": 13
                })
                print(f"✓ definition: {result.content[0].text[:200]}...")
            except Exception as e:
                print(f"✗ definition failed: {e}")
            
            # Test 4: textDocument_references on "greet"
            print("\n=== TEST 4: textDocument_references (greet) ===")
            try:
                result = await session.call_tool("textDocument_references", arguments={
                    "file": "/home/diaz/mygit/python-lsp-mcp/test_sample.py",
                    "line": 3,
                    "character": 4
                })
                print(f"✓ references: {result.content[0].text[:200]}...")
            except Exception as e:
                print(f"✗ references failed: {e}")
            
            # Test 5: textDocument_documentSymbol
            print("\n=== TEST 5: textDocument_documentSymbol ===")
            try:
                result = await session.call_tool("textDocument_documentSymbol", arguments={
                    "file": "/home/diaz/mygit/python-lsp-mcp/test_sample.py"
                })
                print(f"✓ symbols: {result.content[0].text[:300]}...")
            except Exception as e:
                print(f"✗ symbols failed: {e}")
            
            # Test 6: textDocument_completion on partial "calc."
            print("\n=== TEST 6: textDocument_completion (calc.) ===")
            try:
                result = await session.call_tool("textDocument_completion", arguments={
                    "file": "/home/diaz/mygit/python-lsp-mcp/test_sample.py",
                    "line": 30,
                    "character": 20
                })
                print(f"✓ completion: {result.content[0].text[:300]}...")
            except Exception as e:
                print(f"✗ completion failed: {e}")
            
            print("\n=== ALL TESTS COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(test_tools())
