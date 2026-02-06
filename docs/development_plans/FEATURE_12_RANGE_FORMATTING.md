# Feature: Range Formatting

**Feature ID**: FEATURE_12  
**Priority**: MEDIUM  
**Complexity**: LOW  
**Estimated Time**: 1 hour  
**Implementation Status**: ❌ NOT STARTED  
**LSP Method**: `textDocument/rangeFormatting`  
**LSP Capability**: `documentRangeFormattingProvider`

---

## Overview

Enable AI agents to format specific code ranges instead of entire files.

**What this provides**:
- 🎯 Format only selected code regions
- ⚡ Performance optimization (skip unchanged sections)
- 🔧 Preserve manually formatted sections
- ✨ Precise formatting control

**Why Useful**: Performance and control - format only newly generated code without reformatting entire file.

---

## Current State Analysis

### What We Have ✅
- FEATURE_11 (Document Formatting) implementation pattern
- All necessary helpers and infrastructure

### What We Need ⚠️
- **Input Model**: `RangeFormattingInput` with range parameters
- **Tool Handler**: `textDocument_rangeFormatting`
- **Integration Test**: Verify partial formatting

---

## LSP Specification Reference

**Method**: `textDocument/rangeFormatting`  
**Capability**: `documentRangeFormattingProvider`

**Request**:
```python
{
    "textDocument": {"uri": "file:///path/to/file.py"},
    "range": {
        "start": {"line": 5, "character": 0},
        "end": {"line": 10, "character": 0}
    },
    "options": {
        "tabSize": 4,
        "insertSpaces": true
    }
}
```

**Response**: `TextEdit[]` or `null`

---

## Implementation Strategy

### Phase 1: Define Input Model (10 minutes)

**File**: `src/python_lsp_mcp/server.py`

```python
class RangeFormattingInput(BaseModel):
    """Input for textDocument/rangeFormatting tool."""

    file: str = Field(..., description="Path to the Python file")
    line_start: int = Field(..., description="Start line number (0-indexed)")
    character_start: int = Field(..., description="Start character position (0-indexed)")
    line_end: int = Field(..., description="End line number (0-indexed)")
    character_end: int = Field(..., description="End character position (0-indexed)")
    tab_size: int = Field(4, description="Tab size (default: 4)")
    insert_spaces: bool = Field(True, description="Use spaces instead of tabs (default: True)")
    lsp_id: str | None = Field(None, description="Specific LSP server ID to use (optional)")
```

### Phase 2: Implement Tool Handler (30 minutes)

**File**: `src/python_lsp_mcp/server.py`

```python
    # Tool: textDocument/rangeFormatting
    @server.call_tool()
    async def textDocument_rangeFormatting(arguments: dict[str, Any]) -> list[Any]:
        """Format specific code range according to style guidelines.

        More efficient than full document formatting for large files.
        """
        input_data = RangeFormattingInput(**arguments)
        file_path = Path(input_data.file)

        # Validate file exists
        is_valid, error_msg = validate_file(file_path)
        if not is_valid:
            return [{"type": "text", "text": f"Error: {error_msg}"}]

        # Get appropriate LSP client
        if input_data.lsp_id:
            lsp_client = lsp_manager.get_lsp_by_id(input_data.lsp_id)
        else:
            lsp_client = lsp_manager.get_lsp_by_extension(file_path)

        if not lsp_client:
            return [{"type": "text", "text": f"Error: No LSP server configured for {file_path.suffix}"}]

        try:
            # Ensure client is started
            if not lsp_client.is_started():
                await lsp_client.start()

            # Check capability
            cap_error = await check_capability(
                lsp_client, "documentRangeFormattingProvider", "range formatting"
            )
            if cap_error:
                return cap_error

            # Notify document open
            await lsp_client.notify_document_open(str(file_path.absolute()), "python")

            # Build request parameters
            params = {
                "textDocument": {"uri": f"file://{file_path.absolute()}"},
                "range": {
                    "start": {
                        "line": input_data.line_start,
                        "character": input_data.character_start
                    },
                    "end": {
                        "line": input_data.line_end,
                        "character": input_data.character_end
                    }
                },
                "options": {
                    "tabSize": input_data.tab_size,
                    "insertSpaces": input_data.insert_spaces
                }
            }

            response = await lsp_client.send_request(
                "textDocument/rangeFormatting", params, timeout=30.0
            )

            # Format response (same as document formatting)
            if not response:
                return [{"type": "text", "text": "No formatting changes needed in selected range"}]

            edit_count = len(response) if isinstance(response, list) else 1
            result_lines = [f"Range formatting applied: {edit_count} text edit(s)"]
            result_lines.append(f"Range: lines {input_data.line_start + 1}-{input_data.line_end + 1}")

            return [{"type": "text", "text": "\n".join(result_lines)}]

        except Exception as e:
            logger.error(f"Error in textDocument_rangeFormatting: {e}", exc_info=True)
            return [{"type": "text", "text": f"Error formatting range: {e}"}]
```

### Phase 3: Add Integration Test (20 minutes)

**File**: `tests/test_integration.py`

```python
    @pytest.mark.asyncio
    async def test_range_formatting_request(self, workspace_dir, sample_python_file):
        """Test range formatting request end-to-end."""
        # Write code with formatting issues in specific section
        code = textwrap.dedent("""
            def foo(x, y):
                return x + y
            
            def bar(a,b):
                return a+b
            
            def baz(m, n):
                return m * n
        """).strip()
        
        sample_python_file.write_text(code)

        config = create_test_config(workspace_dir)
        config.workspace = workspace_dir

        # Create server
        server, manager = create_server(config)

        try:
            # Start LSP clients
            await manager.start_all()

            # Format only the 'bar' function (lines 3-4)
            arguments = {
                "file": str(sample_python_file),
                "line_start": 3,
                "character_start": 0,
                "line_end": 4,
                "character_end": 20
            }

            result = await server.call_tool("textDocument_rangeFormatting", arguments)

            # Verify response
            assert isinstance(result, list)
            assert len(result) > 0
            text = result[0]["text"]
            assert "range" in text.lower() and "edit" in text.lower()

        finally:
            await manager.shutdown_all()
```

### Phase 4: Update Documentation (10 minutes)

**File**: `README.md`

**Add**:
```markdown
- `textDocument_rangeFormatting`: Format specific code range (lines X-Y)
```

---

## Verification Checklist

- [ ] `RangeFormattingInput` model defined
- [ ] Tool handler implemented (similar to FEATURE_11)
- [ ] Integration test passes
- [ ] README.md updated
- [ ] Works with partial file selection
- [ ] All tests pass

---

## Usage Example

```python
# Format only lines 5-10
textDocument_rangeFormatting(
    file="/tmp/code.py",
    line_start=5,
    character_start=0,
    line_end=10,
    character_end=0
)

# Response:
"""
Range formatting applied: 2 text edit(s)
Range: lines 6-11
"""
```

---

## Integration Points

- Reuses all infrastructure from FEATURE_11
- Same formatter requirements (autopep8/yapf/black)

---

**Last Updated**: February 6, 2026  
**Status**: Ready for implementation  
**Estimated Completion**: 1 hour
