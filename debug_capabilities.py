#!/usr/bin/env python3
"""Debug pylsp capabilities."""
import asyncio
import json
from python_lsp_mcp.lsp_client import LspClient

async def debug():
    client = LspClient(
        id="debug",
        command="pylsp",
        args=[],
        workspace="/home/diaz/mygit/python-lsp-mcp",
        extensions=[".py"],
        languages=["python"]
    )
    
    print("Starting LSP server...")
    await client.start()
    await asyncio.sleep(1)
    
    print("\n=== Server Capabilities ===")
    caps = client.get_capabilities()
    print(json.dumps(caps, indent=2))
    
    print("\n=== Checking specific capabilities ===")
    print(f"hoverProvider: {caps.get('hoverProvider')}")
    print(f"definitionProvider: {caps.get('definitionProvider')}")
    print(f"referencesProvider: {caps.get('referencesProvider')}")
    print(f"documentSymbolProvider: {caps.get('documentSymbolProvider')}")
    print(f"completionProvider: {caps.get('completionProvider')}")
    
    await client.stop()

asyncio.run(debug())
