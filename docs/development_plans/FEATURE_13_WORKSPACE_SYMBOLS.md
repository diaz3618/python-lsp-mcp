# Feature: Workspace Symbols

**Feature ID**: FEATURE_13  
**Priority**: MEDIUM  
**Complexity**: LOW-MEDIUM  
**Estimated Time**: 1-2 hours  
**Implementation Status**: ❌ NOT STARTED  
**LSP Method**: `workspace/symbol`  
**LSP Capability**: `workspaceSymbolProvider`

---

## Overview

Enable AI agents to search for symbols (functions, classes, variables) across entire workspace by name.

**What this provides**:
- 🔍 Workspace-wide symbol search
- 📦 Find definitions without knowing file location
- 🎯 Locate classes, functions, variables by name
- ⚡ Fast code discovery

**Why Useful**: Code discovery - find definitions across multiple files without navigating manually.

---

## Current State Analysis

### What We Have ✅
- MCP server and LSP client infrastructure
- Pattern for tool implementation (5 existing tools)
- Helpers for validation and capability checking

### What We Need ⚠️
- **Input Model**: `WorkspaceSymbolInput` with search query
- **Tool Handler**: `workspace_symbol`
- **Integration Test**: Verify search across multiple files
- **Symbol kind mapping**: Human-readable symbol type names

---

## LSP Specification Reference

**Method**: `workspace/symbol`  
**Capability**: `workspaceSymbolProvider`

**Request**:
```python
{
    "query": "MyClass"  # Search query
}
```

**Response**: `SymbolInformation[]` or `WorkspaceSymbol[]`

**SymbolInformation structure**:
```python
{
    "name": "MyClass",
    "kind": 5,  # Class
    "location": {
        "uri": "file:///path/to/file.py",
        "range": {
            "start": {"line": 10, "character": 0},
            "end": {"line": 20, "character": 0}
        }
    },
    "containerName": "my_module"  # Optional: parent scope
}
```

**Symbol kinds**:
- 1: File
- 2: Module
- 5: Class
- 6: Method
- 12: Function
- 13: Variable
- 14: Constant

---

## Implementation Strategy

### Phase 1: Define Input Model (10 minutes)

**File**: `src/python_lsp_mcp/server.py`

```python
class WorkspaceSymbolInput(BaseModel):
    """Input for workspace/symbol tool."""

    query: str = Field(..., description="Search query for symbol name (e.g., 'MyClass', 'calculate_sum')")
    lsp_id: str | None = Field(None, description="Specific LSP server ID to use (optional)")
```

### Phase 2: Implement Tool Handler (1 hour)

**File**: `src/python_lsp_mcp/server.py`

```python
    # Tool: workspace/symbol
    @server.call_tool()
    async def workspace_symbol(arguments: dict[str, Any]) -> list[Any]:
        """Search for symbols across entire workspace by name.

        Returns functions, classes, variables, and other symbols matching the query.
        """
        input_data = WorkspaceSymbolInput(**arguments)

        # Get appropriate LSP client
        if input_data.lsp_id:
            lsp_client = lsp_manager.get_lsp_by_id(input_data.lsp_id)
        else:
            # Use first available LSP client (workspace search doesn't need file extension)
            lsp_client = next(iter(lsp_manager.lsps.values()), None)
            if not lsp_client:
                return [{"type": "text", "text": "Error: No LSP servers configured"}]

        try:
            # Ensure client is started
            if not lsp_client.is_started():
                await lsp_client.start()

            # Check capability
            cap_error = await check_capability(
                lsp_client, "workspaceSymbolProvider", "workspace symbol search"
            )
            if cap_error:
                return cap_error

            # Build request parameters
            params = {"query": input_data.query}

            response = await lsp_client.send_request("workspace/symbol", params, timeout=30.0)

            # Format response
            if not response:
                return [{"type": "text", "text": f"No symbols found for query: {input_data.query}"}]

            # Symbol kind mapping
            kind_names = {
                1: "File",
                2: "Module",
                3: "Namespace",
                4: "Package",
                5: "Class",
                6: "Method",
                7: "Property",
                8: "Field",
                9: "Constructor",
                10: "Enum",
                11: "Interface",
                12: "Function",
                13: "Variable",
                14: "Constant",
                15: "String",
                16: "Number",
                17: "Boolean",
                18: "Array",
            }

            result_lines = [f"Found {len(response)} symbol(s) matching '{input_data.query}':"]
            
            for symbol in response[:20]:  # Limit to 20 results
                if isinstance(symbol, dict):
                    name = symbol.get("name", "")
                    kind = symbol.get("kind", 0)
                    location = symbol.get("location", {})
                    container = symbol.get("containerName", "")
                else:
                    name = getattr(symbol, "name", "")
                    kind = getattr(symbol, "kind", 0)
                    location = getattr(symbol, "location", {})
                    container = getattr(symbol, "containerName", "")

                kind_name = kind_names.get(kind, f"Kind{kind}")

                # Extract location info
                if isinstance(location, dict):
                    uri = location.get("uri", "")
                    range_info = location.get("range", {})
                    start = range_info.get("start", {})
                    line = start.get("line", 0) if isinstance(start, dict) else 0
                else:
                    uri = getattr(location, "uri", "")
                    line = getattr(location.range.start, "line", 0) if hasattr(location, "range") else 0

                file_name = Path(uri.replace("file://", "")).name if uri else "unknown"
                
                result_lines.append(f"\n{kind_name}: {name}")
                result_lines.append(f"  File: {file_name}:{line + 1}")
                if container:
                    result_lines.append(f"  Container: {container}")

            if len(response) > 20:
                result_lines.append(f"\n... and {len(response) - 20} more")

            return [{"type": "text", "text": "\n".join(result_lines)}]

        except Exception as e:
            logger.error(f"Error in workspace_symbol: {e}", exc_info=True)
            return [{"type": "text", "text": f"Error searching workspace symbols: {e}"}]
```

### Phase 3: Add Integration Test (30 minutes)

**File**: `tests/test_integration.py`

```python
    @pytest.mark.asyncio
    async def test_workspace_symbol_request(self, workspace_dir, sample_python_file):
        """Test workspace symbol search end-to-end."""
        # Create another file with additional symbols
        additional_file = workspace_dir / "module.py"
        additional_file.write_text(textwrap.dedent("""
            class Calculator:
                def add(self, x, y):
                    return x + y
                
                def subtract(self, x, y):
                    return x - y
            
            def calculate_sum(numbers):
                return sum(numbers)
        """).strip())

        config = create_test_config(workspace_dir)
        config.workspace = workspace_dir

        # Create server
        server, manager = create_server(config)

        try:
            # Start LSP clients
            await manager.start_all()

            # Search for symbols containing "calc"
            arguments = {
                "query": "calc"
            }

            result = await server.call_tool("workspace_symbol", arguments)

            # Verify response format
            assert isinstance(result, list)
            assert len(result) > 0
            assert "type" in result[0]
            assert "text" in result[0]

            # Verify content has results or "No symbols found"
            text = result[0]["text"]
            assert "symbol" in text.lower()

        finally:
            await manager.shutdown_all()

    @pytest.mark.asyncio
    async def test_workspace_symbol_no_results(self, workspace_dir, sample_python_file):
        """Test workspace symbol search with no matches."""
        config = create_test_config(workspace_dir)
        config.workspace = workspace_dir

        # Create server
        server, manager = create_server(config)

        try:
            # Start LSP clients
            await manager.start_all()

            # Search for non-existent symbol
            arguments = {
                "query": "NonExistentSymbolXYZ123"
            }

            result = await server.call_tool("workspace_symbol", arguments)

            # Verify response
            assert isinstance(result, list)
            text = result[0]["text"]
            assert "no symbols" in text.lower()

        finally:
            await manager.shutdown_all()
```

### Phase 4: Update Documentation (10 minutes)

**File**: `README.md`

**Add**:
```markdown
- `workspace_symbol`: Search for symbols (functions, classes, variables) across entire workspace
```

---

## Testing Plan

### Test Scenarios
1. ✅ Search finds results (multiple symbols)
2. ✅ Search finds no results
3. ✅ Empty query (should return error or all symbols)
4. ✅ Case-insensitive search
5. ✅ Capability check (LSP without workspace symbols)
6. ✅ Limit results to 20 (performance)

---

## Verification Checklist

### Code Implementation
- [ ] `WorkspaceSymbolInput` model defined
- [ ] Tool handler implemented
- [ ] Symbol kind mapping included
- [ ] Results limited to 20 (with "... and X more" message)
- [ ] Proper error handling

### Testing
- [ ] Integration test with multiple files passes
- [ ] Integration test with no results passes
- [ ] All existing tests still pass

### Documentation
- [ ] README.md updated
- [ ] DEVELOPMENT_PLANS.md updated

### Manual Verification
- [ ] Search across multiple Python files works
- [ ] Symbol kinds displayed correctly (Class, Function, Method, etc.)
- [ ] File names and line numbers shown
- [ ] Container names shown when available

---

## Usage Examples

### Example 1: Find Classes

```python
# Workspace with multiple files

# Call tool
workspace_symbol(query="Calculator")

# Response:
"""
Found 2 symbol(s) matching 'Calculator':

Class: Calculator
  File: module.py:5
  Container: module

Method: Calculator.add
  File: module.py:6
  Container: Calculator
"""
```

### Example 2: Find Functions

```python
workspace_symbol(query="calculate")

# Response:
"""
Found 3 symbol(s) matching 'calculate':

Function: calculate_sum
  File: module.py:12

Function: calculate_product
  File: utils.py:25

Method: Calculator.calculate
  File: module.py:15
  Container: Calculator
"""
```

---

## Integration Points

### Dependencies
- `check_capability()` helper
- `lsp_manager.get_lsp_by_id()`
- `lsp_manager.lsps` (dictionary of LSP clients)
- `lsp_client.send_request()`

### Notes
- Does NOT require file path (workspace-level operation)
- Uses first available LSP client if no `lsp_id` specified
- Requires LSP server to index workspace (may take time for large projects)

---

## References

- **LSP Specification**: https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#workspace_symbol

---

**Last Updated**: February 6, 2026  
**Status**: Ready for implementation  
**Estimated Completion**: 1-2 hours
