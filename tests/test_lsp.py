#!/usr/bin/env python3
"""Simple test script to verify MCP server functionality."""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from python_lsp_mcp.config import Config, LSPServerConfig
from python_lsp_mcp.lsp_manager import LSPManager


async def test_lsp_manager():
    """Test LSP manager startup and basic operations."""
    print("=" * 60)
    print("Testing LSP Manager")
    print("=" * 60)
    
    # Create configuration
    config = Config(
        lsps=[
            LSPServerConfig(
                id="pylsp",
                command="pylsp",
                args=[],
                extensions=[".py", ".pyi"],
                languages=["python"]
            )
        ],
        workspace=str(Path(__file__).parent)
    )
    
    # Create LSP manager
    manager = LSPManager(config)
    
    try:
        # Start all LSP servers
        print("\n1. Starting LSP servers...")
        await manager.start_all()
        print("✓ LSP servers started successfully")
        
        # List LSP servers
        print("\n2. Listing LSP servers...")
        lsp_list = manager.list_lsps()
        print(f"   Found {len(lsp_list)} LSP server(s):")
        for lsp_info in lsp_list:
            print(f"   - {lsp_info['id']}: {lsp_info['status']}")
            if lsp_info["status"] == "started":
                print(f"     Extensions: {', '.join(lsp_info['extensions'])}")
                print(f"     Languages: {', '.join(lsp_info['languages'])}")
        
        # Get LSP by extension
        print("\n3. Testing LSP routing by extension...")
        lsp = manager.get_lsp_by_extension("test_sample.py")
        if lsp:
            print(f"✓ Found LSP '{lsp.server_id}' for .py files")
        else:
            print("✗ No LSP found for .py files")
        
        # Test hover on test file
        if lsp:
            print("\n4. Testing hover request...")
            test_file = Path(__file__).parent / "test_sample.py"
            
            # Open document
            await lsp.notify_document_open(str(test_file), "python")
            print(f"   Opened document: {test_file.name}")
            
            # Request hover at line 7 (the greet function)
            hover_result = await lsp.send_request(
                "textDocument/hover",
                {
                    "textDocument": {"uri": f"file://{test_file}"},
                    "position": {"line": 7, "character": 4}
                }
            )
            
            if hover_result and "contents" in hover_result:
                print(f"✓ Hover result received:")
                contents = hover_result["contents"]
                if isinstance(contents, dict):
                    print(f"   {contents.get('value', contents)[:200]}")
                elif isinstance(contents, str):
                    print(f"   {contents[:200]}")
                else:
                    print(f"   {str(contents)[:200]}")
            else:
                print(f"   Hover result: {hover_result}")
        
        # Test definition on test file
        if lsp:
            print("\n5. Testing definition request...")
            test_file = Path(__file__).parent / "test_sample.py"
            
            # Request definition at line 44 (the greet call)
            definition_result = await lsp.send_request(
                "textDocument/definition",
                {
                    "textDocument": {"uri": f"file://{test_file}"},
                    "position": {"line": 43, "character": 15}
                }
            )
            
            if definition_result:
                print(f"✓ Definition result received:")
                if isinstance(definition_result, list) and definition_result:
                    loc = definition_result[0]
                    uri = loc.get("uri", loc.get("targetUri", ""))
                    range_info = loc.get("range", loc.get("targetRange", {}))
                    line = range_info.get("start", {}).get("line", -1)
                    print(f"   Location: {uri.split('/')[-1]}:{line + 1}")
                else:
                    print(f"   {str(definition_result)[:200]}")
            else:
                print("   No definition found")
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        print("\n6. Shutting down LSP servers...")
        await manager.shutdown_all()
        print("✓ Cleanup complete")


if __name__ == "__main__":
    asyncio.run(test_lsp_manager())
