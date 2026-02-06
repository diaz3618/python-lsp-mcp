#!/usr/bin/env python3
"""Test py-lsp-mcp tools with eager initialization."""
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_tools():
    """Test all 6 tools with eager init."""
    server_params = StdioServerParameters(
        command="python-lsp-mcp",
        args=["--config", "/home/diaz/mygit/python-lsp-mcp/test_config.toml"],
        env=None,
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Give LSP server time to start
            print("Waiting for LSP server to initialize...")
            await asyncio.sleep(3)
            
            # Test 1: lsp_info
            print("\n=== TEST 1: lsp_info ===")
            try:
                result = await session.call_tool("lsp_info", arguments={})
                content = result.content[0].text
                print(f"✓ lsp_info:\n{content}")
            except Exception as e:
                print(f"✗ lsp_info failed: {e}")
            
            # Test 2: textDocument_hover on "greet" function (line 3, char 4)
            print("\n=== TEST 2: textDocument_hover (greet function) ===")
            try:
                result = await session.call_tool("textDocument_hover", arguments={
                    "file": "/home/diaz/mygit/python-lsp-mcp/test_sample.py",
                    "line": 3,
                    "character": 4
                })
                content = result.content[0].text
                print(f"✓ hover: {content[:400]}")
            except Exception as e:
                print(f"✗ hover failed: {e}")
            
            # Test 3: textDocument_definition on "greet" call (line 27)
            print("\n=== TEST 3: textDocument_definition (greet call) ===")
            try:
                result = await session.call_tool("textDocument_definition", arguments={
                    "file": "/home/diaz/mygit/python-lsp-mcp/test_sample.py",
                    "line": 27,
                    "character": 13
                })
                content = result.content[0].text
                print(f"✓ definition: {content[:400]}")
            except Exception as e:
                print(f"✗ definition failed: {e}")
            
            # Test 4: textDocument_documentSymbol
            print("\n=== TEST 4: textDocument_documentSymbol ===")
            try:
                result = await session.call_tool("textDocument_documentSymbol", arguments={
                    "file": "/home/diaz/mygit/python-lsp-mcp/test_sample.py"
                })
                content = result.content[0].text
                print(f"✓ symbols: {content[:600]}")
            except Exception as e:
                print(f"✗ symbols failed: {e}")
            
            print("\n=== ALL CRITICAL TESTS COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(test_tools())
