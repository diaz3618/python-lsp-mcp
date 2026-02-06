# Feature: Document Formatting

**Feature ID**: FEATURE_11  
**Priority**: HIGH  
**Complexity**: LOW-MEDIUM  
**Estimated Time**: 1-2 hours  
**Implementation Status**: ❌ NOT STARTED  
**LSP Method**: `textDocument/formatting`  
**LSP Capability**: `documentFormattingProvider`

---

## Overview

Enable AI agents to automatically format entire Python files according to style guidelines (PEP 8).

**What this provides**:
- 🎨 Automatic PEP 8 formatting
- 📏 Consistent code style (indentation, spacing, line length)
- 🔧 Configurable formatter (autopep8, yapf, or black)
- ✨ Clean, readable code without manual effort

**Why Critical**: Essential for code quality - ensures all AI-generated code follows Python conventions consistently.

---

## Current State Analysis

### What We Have ✅
- MCP server framework
- LSP client with `send_request()`
- Pattern for tool implementation (5 existing tools)
- Input validation and capability checking helpers

### What We Need ⚠️
- **Input Model**: `FormattingInput` with file path and formatting options
- **Tool Handler**: `textDocument_formatting` that sends LSP request
- **Response Formatting**: Show edit count and preview
- **Integration Test**: Verify formatting works with badly formatted code
- **LSP Plugin**: Requires formatter (autopep8, yapf, or black)

---

## LSP Specification Reference

**Method**: `textDocument/formatting`  
**Capability**: `documentFormattingProvider`

**Request**:
```python
{
    "textDocument": {"uri": "file:///path/to/file.py"},
    "options": {
        "tabSize": 4,
        "insertSpaces": true,
        "trimTrailingWhitespace": true,
        "insertFinalNewline": true
    }
}
```

**Response**: `TextEdit[]` or `null`

**Official Spec**: https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_formatting

---

## Implementation Strategy

### Phase 1: Define Input Model (10 minutes)

**File**: `src/python_lsp_mcp/server.py`

```python
class FormattingInput(BaseModel):
    """Input for textDocument/formatting tool."""

    file: str = Field(..., description="Path to the Python file")
    tab_size: int = Field(4, description="Tab size (default: 4)")
    insert_spaces: bool = Field(True, description="Use spaces instead of tabs (default: True)")
    trim_trailing_whitespace: bool = Field(True, description="Trim trailing whitespace (default: True)")
    insert_final_newline: bool = Field(True, description="Insert final newline (default: True)")
    lsp_id: str | None = Field(None, description="Specific LSP server ID to use (optional)")
```

### Phase 2: Implement Tool Handler (45 minutes)

**File**: `src/python_lsp_mcp/server.py`

```python
    # Tool: textDocument/formatting
    @server.call_tool()
    async def textDocument_formatting(arguments: dict[str, Any]) -> list[Any]:
        """Format entire Python file according to style guidelines.

        Applies formatting using configured formatter (autopep8, yapf, or black).
        """
        input_data = FormattingInput(**arguments)
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
                lsp_client, "documentFormattingProvider", "formatting"
            )
            if cap_error:
                return cap_error

            # Notify document open
            await lsp_client.notify_document_open(str(file_path.absolute()), "python")

            # Build request parameters
            params = {
                "textDocument": {"uri": f"file://{file_path.absolute()}"},
                "options": {
                    "tabSize": input_data.tab_size,
                    "insertSpaces": input_data.insert_spaces,
                    "trimTrailingWhitespace": input_data.trim_trailing_whitespace,
                    "insertFinalNewline": input_data.insert_final_newline
                }
            }

            response = await lsp_client.send_request("textDocument/formatting", params, timeout=30.0)

            # Format response
            if not response:
                return [{"type": "text", "text": "No formatting changes needed (code already formatted)"}]

            # Response is TextEdit[] - show number of edits
            edit_count = len(response) if isinstance(response, list) else 1
            result_lines = [f"Formatting applied: {edit_count} text edit(s)"]

            # Show preview of first edit (if available)
            if isinstance(response, list) and len(response) > 0:
                first_edit = response[0]
                if isinstance(first_edit, dict):
                    range_info = first_edit.get("range", {})
                    new_text = first_edit.get("newText", "")
                else:
                    range_info = getattr(first_edit, "range", None)
                    new_text = getattr(first_edit, "newText", "")

                if range_info:
                    if isinstance(range_info, dict):
                        start = range_info.get("start", {})
                        end = range_info.get("end", {})
                        start_line = start.get("line", 0) if isinstance(start, dict) else getattr(start, "line", 0)
                        end_line = end.get("line", 0) if isinstance(end, dict) else getattr(end, "line", 0)
                    else:
                        start_line = getattr(range_info.start, "line", 0)
                        end_line = getattr(range_info.end, "line", 0)

                    result_lines.append(f"\nFirst edit: lines {start_line + 1}-{end_line + 1}")
                    # Show preview (truncate if too long)
                    preview = new_text[:100] + ('...' if len(new_text) > 100 else '')
                    result_lines.append(f"Preview: {preview}")

            return [{"type": "text", "text": "\n".join(result_lines)}]

        except Exception as e:
            logger.error(f"Error in textDocument_formatting: {e}", exc_info=True)
            return [{"type": "text", "text": f"Error formatting document: {e}"}]
```

### Phase 3: Add Integration Test (30 minutes)

**File**: `tests/test_integration.py`

```python
    @pytest.mark.asyncio
    async def test_formatting_request(self, workspace_dir, sample_python_file):
        """Test formatting request end-to-end."""
        # Write intentionally badly formatted code
        badly_formatted = textwrap.dedent("""
            def foo(x,y):
                return x+y
            
            
            def bar( a , b ):
                return a-b
        """).strip()
        
        sample_python_file.write_text(badly_formatted)

        config = create_test_config(workspace_dir)
        config.workspace = workspace_dir

        # Create server
        server, manager = create_server(config)

        try:
            # Start LSP clients
            await manager.start_all()

            # Format document
            arguments = {
                "file": str(sample_python_file),
                "tab_size": 4,
                "insert_spaces": True
            }

            result = await server.call_tool("textDocument_formatting", arguments)

            # Verify response format
            assert isinstance(result, list)
            assert len(result) > 0
            assert "type" in result[0]
            assert "text" in result[0]

            # Verify content indicates formatting applied or no changes needed
            text = result[0]["text"]
            assert "edit" in text.lower() or "no formatting" in text.lower()

        finally:
            await manager.shutdown_all()

    @pytest.mark.asyncio
    async def test_formatting_already_formatted(self, workspace_dir, sample_python_file):
        """Test formatting on already-formatted code."""
        # Write properly formatted code
        well_formatted = textwrap.dedent("""
            def foo(x, y):
                return x + y
            
            
            def bar(a, b):
                return a - b
        """).strip()
        
        sample_python_file.write_text(well_formatted)

        config = create_test_config(workspace_dir)
        config.workspace = workspace_dir

        # Create server
        server, manager = create_server(config)

        try:
            # Start LSP clients
            await manager.start_all()

            # Format document
            arguments = {
                "file": str(sample_python_file)
            }

            result = await server.call_tool("textDocument_formatting", arguments)

            # Verify response
            assert isinstance(result, list)
            text = result[0]["text"]
            # Should indicate no changes or minimal edits
            assert "no formatting" in text.lower() or "edit" in text.lower()

        finally:
            await manager.shutdown_all()
```

### Phase 4: Update Documentation (10 minutes)

**File**: `README.md`

**Add**:
```markdown
- `textDocument_formatting`: Format entire document according to style guidelines (PEP 8)
```

---

## Testing Plan

### Test Scenarios
1. ✅ Format badly formatted code (should apply edits)
2. ✅ Format already-formatted code (no edits or minimal edits)
3. ✅ File validation (non-existent file)
4. ✅ Capability check (LSP without formatter)
5. ✅ Custom formatting options (tabSize, insertSpaces)
6. ✅ LSP server timeout

---

## Verification Checklist

### Code Implementation
- [ ] `FormattingInput` model defined
- [ ] Tool handler follows existing pattern
- [ ] Response shows edit count and preview
- [ ] Proper error handling
- [ ] Logging with `logger.error()`

### Testing
- [ ] Integration test with badly formatted code passes
- [ ] Integration test with well-formatted code passes
- [ ] File validation works
- [ ] All existing tests still pass

### Documentation
- [ ] README.md updated
- [ ] DEVELOPMENT_PLANS.md updated

### Manual Verification
- [ ] Tested with autopep8 formatter
- [ ] Formatted code follows PEP 8
- [ ] Error messages are clear
- [ ] Works with custom options (tab_size, etc.)

---

## Usage Example

```python
# Python code with formatting issues
# File: /tmp/messy.py
"""
def foo(x,y):
    return x+y
"""

# Call tool
textDocument_formatting(
    file="/tmp/messy.py",
    tab_size=4,
    insert_spaces=True
)

# Response:
"""
Formatting applied: 1 text edit(s)

First edit: lines 1-2
Preview: def foo(x, y):
    return x + y
"""
```

---

## Integration Points

### Dependencies
- `validate_file()`, `check_capability()` helpers
- `lsp_manager.get_lsp_by_extension()`
- `lsp_client.send_request()`
- `lsp_client.notify_document_open()`

### LSP Plugin Requirements

```bash
# Default formatter (autopep8)
pip install autopep8

# Alternative formatters
pip install yapf  # or
pip install black
```

---

## References

- **LSP Specification**: https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_formatting
- **autopep8**: https://github.com/hhatto/autopep8
- **black**: https://github.com/psf/black
- **yapf**: https://github.com/google/yapf

---

**Last Updated**: February 6, 2026  
**Status**: Ready for implementation  
**Estimated Completion**: 1-2 hours
