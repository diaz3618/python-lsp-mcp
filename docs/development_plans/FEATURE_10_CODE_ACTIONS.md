# Feature: Code Actions (Quick Fixes & Refactorings)

**Feature ID**: FEATURE_10  
**Priority**: HIGH  
**Complexity**: MEDIUM  
**Estimated Time**: 2-3 hours  
**Implementation Status**: ❌ NOT STARTED  
**LSP Method**: `textDocument/codeAction`  
**LSP Capability**: `codeActionProvider`

---

## Overview

Enable AI agents to discover and apply automatic code fixes, refactorings, and quick fixes at specific positions in Python files.

**What this provides**:
- 🔧 Quick fixes for diagnostics (errors/warnings)
- 🔄 Refactoring suggestions (extract function, inline variable)
- 📦 Import management (add missing imports, organize imports)
- ✨ Code improvements (simplify expressions, remove unused code)

**Why Critical**: Essential for code quality - enables AI to automatically fix errors and suggest improvements without manual intervention.

---

## Current State Analysis

### What We Have ✅
- MCP server framework (`src/python_lsp_mcp/server.py`)
- LSP client with `send_request()` (`src/python_lsp_mcp/lsp_client.py`)
- Pattern for tool implementation (existing 5 tools: hover, definition, references, symbols, completion)
- Input validation helpers (`validate_file()`)
- Capability checking helpers (`check_capability()`)
- Integration test framework (`tests/test_integration.py`)

### What We Need ⚠️
- **Input Model**: `CodeActionInput` with file path, range (start/end line/character), optional filter by `CodeActionKind`
- **Tool Handler**: `textDocument_codeAction` that sends LSP request and formats response
- **Response Formatting**: Display code actions with title, kind, and edit preview
- **Integration Test**: Verify code actions work with real LSP server
- **Documentation**: Update README.md with new tool
- **LSP Plugin**: Requires pylsp plugins (rope, autopep8, python-lsp-isort) for full functionality

### Gaps from Reference Implementation

Reference implementation (repos/v0.3.0) doesn't use code actions - it implements refactoring tools directly via Rope. Our approach is different:
- **Reference**: Direct Rope refactoring (rename, move, change signature)
- **Our approach**: Expose LSP code actions (more generic, supports any LSP server)
- **Trade-off**: Less control over refactoring flow, but more flexibility with backend selection

---

## LSP Specification Reference

### Method: `textDocument/codeAction`

**Capability**: `codeActionProvider` (check via `lsp_client.has_capability("codeActionProvider")`)

**Request Parameters**:
```python
{
    "textDocument": {"uri": "file:///path/to/file.py"},
    "range": {
        "start": {"line": 10, "character": 5},
        "end": {"line": 10, "character": 20}
    },
    "context": {
        "diagnostics": [],  # Optional: errors/warnings at position
        "only": []          # Optional: filter by CodeActionKind
    }
}
```

**Response**: `CodeAction[]` or `Command[]` or `null`

**CodeAction Structure**:
```python
{
    "title": "Add import 'import pandas as pd'",
    "kind": "quickfix",
    "diagnostics": [...],  # Related diagnostics (if fixing an error)
    "isPreferred": false,
    "edit": {  # WorkspaceEdit - changes to apply
        "changes": {
            "file:///path/to/file.py": [
                {
                    "range": {"start": {"line": 0, "character": 0}, "end": {"line": 0, "character": 0}},
                    "newText": "import pandas as pd\n"
                }
            ]
        }
    },
    "command": {...}  # Optional: command to execute instead of/after edit
}
```

**CodeActionKind Enum** (for filtering):
- `quickfix` - Fix errors/warnings
- `refactor` - General refactoring
- `refactor.extract` - Extract function/variable
- `refactor.inline` - Inline function/variable
- `refactor.rewrite` - Rewrite code
- `source` - Source-level actions
- `source.organizeImports` - Sort/organize imports
- `source.fixAll` - Apply all available fixes

**Official Spec**: https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_codeAction

---

## Implementation Strategy

### Phase 1: Define Input Model (15 minutes)

**File**: `src/python_lsp_mcp/server.py` (after existing input models, ~line 65)

```python
class CodeActionInput(BaseModel):
    """Input for textDocument/codeAction tool."""

    file: str = Field(..., description="Path to the Python file")
    line_start: int = Field(..., description="Start line number (0-indexed)")
    character_start: int = Field(..., description="Start character position (0-indexed)")
    line_end: int = Field(..., description="End line number (0-indexed)")
    character_end: int = Field(..., description="End character position (0-indexed)")
    kind: str | None = Field(
        None,
        description="Filter by CodeActionKind (e.g., 'quickfix', 'refactor', 'source.organizeImports'). Leave None for all kinds."
    )
    lsp_id: str | None = Field(None, description="Specific LSP server ID to use (optional)")
```

**Validation Notes**:
- All line/character positions are 0-indexed (LSP convention)
- `kind` is optional - if not provided, return all available actions
- Range must be valid (end >= start)

### Phase 2: Implement Tool Handler (1.5-2 hours)

**File**: `src/python_lsp_mcp/server.py` (after `textDocument_completion` tool, ~line 520)

```python
    # Tool: textDocument/codeAction
    @server.call_tool()
    async def textDocument_codeAction(arguments: dict[str, Any]) -> list[Any]:
        """Get available code actions (quick fixes, refactorings) for a range.

        Returns actions like: add missing imports, extract function, format code,
        organize imports, fix PEP 8 violations, etc.
        
        Args:
            arguments: Tool arguments with file path, range, and optional kind filter
            
        Returns:
            List with single text content showing available code actions
        """
        input_data = CodeActionInput(**arguments)
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
            cap_error = await check_capability(lsp_client, "codeActionProvider", "code actions")
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
                "context": {
                    "diagnostics": [],  # Could be enhanced to pass diagnostics from previous call
                    "only": [input_data.kind] if input_data.kind else []
                }
            }

            response = await lsp_client.send_request("textDocument/codeAction", params, timeout=30.0)

            # Format response
            if not response:
                return [{"type": "text", "text": "No code actions available at this position"}]

            result_lines = [f"Found {len(response)} code action(s):"]
            for idx, action in enumerate(response, 1):
                # Handle both CodeAction and Command responses
                if isinstance(action, dict):
                    title = action.get("title", "Unknown action")
                    kind = action.get("kind", "unknown")
                    is_preferred = action.get("isPreferred", False)
                    edit = action.get("edit")
                else:
                    title = getattr(action, "title", "Unknown action")
                    kind = getattr(action, "kind", "unknown")
                    is_preferred = getattr(action, "isPreferred", False)
                    edit = getattr(action, "edit", None)

                result_lines.append(f"\n{idx}. {title}")
                result_lines.append(f"   Kind: {kind}")
                if is_preferred:
                    result_lines.append("   ⭐ Preferred action")

                # Show edit preview if available
                if edit:
                    if isinstance(edit, dict):
                        changes = edit.get("changes", {})
                    else:
                        changes = getattr(edit, "changes", {})
                    
                    if changes:
                        changes_count = sum(len(edits) for edits in changes.values())
                        result_lines.append(f"   Edits: {changes_count} text edit(s) across {len(changes)} file(s)")
                        
                        # Show which files will be modified
                        for file_uri in changes.keys():
                            file_name = Path(file_uri.replace("file://", "")).name
                            result_lines.append(f"   - {file_name}")

            return [{"type": "text", "text": "\n".join(result_lines)}]

        except Exception as e:
            logger.error(f"Error in textDocument_codeAction: {e}", exc_info=True)
            return [{"type": "text", "text": f"Error getting code actions: {e}"}]
```

**Implementation Notes**:
- Timeout set to 30 seconds (code actions can be slow)
- Handles both `CodeAction` and `Command` responses (LSP spec allows both)
- Shows edit preview with file count and edit count
- Marks preferred actions with ⭐
- Filters by `kind` if provided (useful for "only show refactorings" or "only show quick fixes")

### Phase 3: Add Integration Test (30 minutes)

**File**: `tests/test_integration.py` (after existing tests, ~line 150)

```python
    @pytest.mark.asyncio
    async def test_code_action_request(self, workspace_dir, sample_python_file):
        """Test code action request end-to-end."""
        # Write code with a fixable issue (undefined name)
        code_with_error = textwrap.dedent("""
            def calculate_sum(a, b):
                return a + b
            
            result = calculate_sum(10, 20)
            print(result)
            
            # Intentional error for code action
            undefined_variable
        """).strip()
        
        sample_python_file.write_text(code_with_error)

        config = create_test_config(workspace_dir)
        config.workspace = workspace_dir

        # Create server
        server, manager = create_server(config)

        try:
            # Start LSP clients
            await manager.start_all()

            # Get code actions for the error line
            arguments = {
                "file": str(sample_python_file),
                "line_start": 7,  # Line with undefined_variable
                "character_start": 0,
                "line_end": 7,
                "character_end": 20,
                "kind": None  # Get all kinds
            }

            result = await server.call_tool("textDocument_codeAction", arguments)

            # Verify response format
            assert isinstance(result, list)
            assert len(result) > 0
            assert "type" in result[0]
            assert "text" in result[0]

            # Verify content has code actions or "No code actions" message
            text = result[0]["text"]
            assert "action" in text.lower() or "no code actions" in text.lower()

        finally:
            await manager.shutdown_all()

    @pytest.mark.asyncio
    async def test_code_action_organize_imports(self, workspace_dir, sample_python_file):
        """Test code action with kind filter (organize imports)."""
        # Write code with unorganized imports
        code_with_imports = textwrap.dedent("""
            import sys
            import json
            import os
            from pathlib import Path
            import asyncio
            
            def main():
                print(Path.cwd())
        """).strip()
        
        sample_python_file.write_text(code_with_imports)

        config = create_test_config(workspace_dir)
        config.workspace = workspace_dir

        # Create server
        server, manager = create_server(config)

        try:
            # Start LSP clients
            await manager.start_all()

            # Get only organize imports actions
            arguments = {
                "file": str(sample_python_file),
                "line_start": 0,
                "character_start": 0,
                "line_end": 0,
                "character_end": 0,
                "kind": "source.organizeImports"
            }

            result = await server.call_tool("textDocument_codeAction", arguments)

            # Verify response format
            assert isinstance(result, list)
            assert len(result) > 0
            assert "type" in result[0]
            assert "text" in result[0]

            # Should mention organizing imports
            text = result[0]["text"]
            assert "import" in text.lower() or "no code actions" in text.lower()

        finally:
            await manager.shutdown_all()
```

**Test Coverage**:
- ✅ Code actions available (multiple actions returned)
- ✅ No code actions (empty result)
- ✅ Filter by kind (`source.organizeImports`)
- ✅ File validation (tested by existing fixtures)
- ✅ Capability check (tested by check_capability helper)

### Phase 4: Update Documentation (15 minutes)

**File**: `README.md` (update "Available Tools" section, ~line 30)

**Add**:
```markdown
- `textDocument_codeAction`: Get available code actions (quick fixes, refactorings, import management)
```

**File**: `DEVELOPMENT_PLANS.md` (update feature table)

**Mark FEATURE_10 as**:
```markdown
| **FEATURE_10** | Code Actions | HIGH | MEDIUM | 2-3h | ✅ COMPLETE | pylsp plugins |
```

---

## Testing Plan

### Unit Test Scenarios

1. **✅ Code actions available (multiple)**
   - Test with code that has fixable issues
   - Verify multiple actions returned with titles, kinds, edit counts

2. **✅ No code actions available**
   - Test with perfect code or position without actions
   - Verify "No code actions available" message

3. **✅ Filter by kind**
   - Test with `kind="source.organizeImports"`
   - Test with `kind="quickfix"`
   - Test with `kind="refactor"`
   - Verify only matching actions returned

4. **✅ File validation**
   - Test with non-existent file
   - Verify error message returned

5. **✅ Capability check**
   - Test with LSP server that doesn't support code actions
   - Verify capability error returned

6. **✅ Invalid range**
   - Test with end position before start position
   - Verify graceful error handling

7. **✅ LSP server timeout**
   - Mock slow LSP server
   - Verify timeout after 30 seconds

### Integration Test Verification

**With pylsp (default LSP server)**:
```bash
# Install plugins for full code action support
pip install "python-lsp-server[rope]"  # Refactoring actions
pip install autopep8                     # PEP 8 fixes
pip install python-lsp-isort            # Import organization

# Run tests
pytest tests/test_integration.py::TestIntegration::test_code_action_request -v
pytest tests/test_integration.py::TestIntegration::test_code_action_organize_imports -v
```

**Expected Results**:
- Code actions returned for fixable issues
- Organize imports action available
- Edit counts and file names displayed correctly

### Manual Testing Checklist

- [ ] **Missing imports**: Code with undefined names shows "Add import" actions
- [ ] **PEP 8 violations**: Code with formatting issues shows fix actions
- [ ] **Unused imports**: Code with unused imports shows remove actions (requires isort)
- [ ] **Extract function**: Selected code shows refactoring actions (requires rope)
- [ ] **Organize imports**: Shows import sorting action (requires isort)
- [ ] **Filter by kind**: Only shows requested action types
- [ ] **No actions**: Perfect code shows "No code actions" message
- [ ] **Error handling**: Invalid file path shows clear error

---

## Verification Checklist

### Code Implementation
- [ ] `CodeActionInput` model defined with all required fields
- [ ] Tool handler follows existing pattern (validate → check capability → request → format → error handling)
- [ ] Response format matches MCP specification (`[{"type": "text", "text": "..."}]`)
- [ ] Handles both `CodeAction` and `Command` responses
- [ ] Shows edit preview with file count and edit count
- [ ] Marks preferred actions
- [ ] Supports kind filtering
- [ ] Proper error handling with try/except
- [ ] Logging with `logger.error()` for exceptions

### Testing
- [ ] Integration test passes with real LSP server
- [ ] Test with code actions available (multiple)
- [ ] Test with no code actions
- [ ] Test with kind filter (`source.organizeImports`)
- [ ] Test file validation
- [ ] Test capability check
- [ ] All existing tests still pass (`pytest tests/ -v`)

### Documentation
- [ ] README.md updated with new tool description
- [ ] DEVELOPMENT_PLANS.md feature table updated with status
- [ ] Code comments explain non-obvious logic

### Manual Verification
- [ ] Tested with pylsp and rope plugin installed
- [ ] Tested with missing imports scenario
- [ ] Tested with PEP 8 violations
- [ ] Tested with organize imports kind
- [ ] Tested with invalid file path (shows error)
- [ ] Logs show no exceptions with `--verbose` flag
- [ ] Response format is readable for humans

### Prerequisites Installed
- [ ] pylsp installed: `pip install python-lsp-server`
- [ ] rope plugin: `pip install "python-lsp-server[rope]"`
- [ ] autopep8: `pip install autopep8`
- [ ] python-lsp-isort: `pip install python-lsp-isort`

---

## Usage Examples

### Example 1: Get All Code Actions

```python
# Python code with undefined variable
# File: /tmp/test.py
"""
def calculate(x, y):
    return result  # Error: undefined 'result'
"""

# Call tool
textDocument_codeAction(
    file="/tmp/test.py",
    line_start=2,
    character_start=11,
    line_end=2,
    character_end=17,
    kind=None
)

# Response:
"""
Found 2 code action(s):

1. Ignore undefined name 'result'
   Kind: quickfix
   
2. Add 'result = None' before usage
   Kind: quickfix
   Edits: 1 text edit(s) across 1 file(s)
   - test.py
"""
```

### Example 2: Organize Imports Only

```python
# Python code with unorganized imports
# File: /tmp/imports.py
"""
import sys
import json
import os
"""

# Call tool with kind filter
textDocument_codeAction(
    file="/tmp/imports.py",
    line_start=0,
    character_start=0,
    line_end=0,
    character_end=0,
    kind="source.organizeImports"
)

# Response:
"""
Found 1 code action(s):

1. Organize imports
   Kind: source.organizeImports
   Edits: 3 text edit(s) across 1 file(s)
   - imports.py
"""
```

### Example 3: Extract Function (with rope)

```python
# Python code with complex logic
# File: /tmp/complex.py
"""
def process_data(data):
    # Selected lines
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
"""

# Call tool on selected lines
textDocument_codeAction(
    file="/tmp/complex.py",
    line_start=3,
    character_start=4,
    line_end=6,
    character_end=30,
    kind="refactor.extract"
)

# Response:
"""
Found 1 code action(s):

1. Extract method
   Kind: refactor.extract
   ⭐ Preferred action
   Edits: 2 text edit(s) across 1 file(s)
   - complex.py
"""
```

---

## Integration Points

### Dependencies
- `validate_file()` helper (already exists in `server.py`)
- `check_capability()` helper (already exists in `server.py`)
- `lsp_manager.get_lsp_by_extension()` (already exists in `lsp_manager.py`)
- `lsp_manager.get_lsp_by_id()` (already exists in `lsp_manager.py`)
- `lsp_client.send_request()` (already exists in `lsp_client.py`)
- `lsp_client.has_capability()` (already exists in `lsp_client.py`)
- `lsp_client.notify_document_open()` (already exists in `lsp_client.py`)

### Affects
- **Tool registration**: Adds 6th tool to MCP server
- **README.md**: Adds tool to "Available Tools" section
- **Integration tests**: Adds 2 new tests (code actions, organize imports)
- **LSP plugins**: Full functionality requires rope, autopep8, python-lsp-isort

### pylsp Plugin Requirements

For full code action support, install these plugins:

```bash
# Refactoring actions (extract function, inline variable)
pip install "python-lsp-server[rope]"

# PEP 8 formatting fixes
pip install autopep8

# Import organization (sort, remove unused)
pip install python-lsp-isort
```

**Without plugins**: Basic code actions from pylsp core (limited)  
**With plugins**: Rich code actions (refactoring, formatting, import management)

---

## Error Handling Patterns

### File Validation Error
```python
# Input: Non-existent file
# Output: Error: File does not exist: /tmp/missing.py
```

### Capability Error
```python
# Input: LSP server without code actions
# Output: Error: LSP server does not support code actions. Required capability: codeActionProvider
```

### No Actions Available
```python
# Input: Perfect code, no issues
# Output: No code actions available at this position
```

### LSP Timeout
```python
# Input: Slow LSP server
# Output: Error getting code actions: Request timed out after 30.0 seconds
```

---

## Future Enhancements

**Potential Improvements** (not in scope for this feature):

1. **Apply code action**: Add `textDocument_codeAction_apply` tool to actually execute the edit
2. **Pass diagnostics**: Enhance to pass diagnostics from previous `textDocument/publishDiagnostics` 
3. **Resolve code action**: Support LSP `codeAction/resolve` for lazy-loaded edits
4. **Batch actions**: Apply multiple code actions at once
5. **Refactoring preview**: Show full diff before applying

---

## References

### Official Documentation
- **LSP Specification**: https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_codeAction
- **MCP Specification**: https://modelcontextprotocol.io/specification/draft
- **pylsp Documentation**: https://github.com/python-lsp/python-lsp-server
- **Rope Documentation**: https://rope.readthedocs.io/

### Related Features
- **FEATURE_01**: Rename Refactoring (direct Rope implementation)
- **FEATURE_02**: Backend Switching (affects code action backend)
- **FEATURE_11**: Document Formatting (related to PEP 8 fixes)

---

**Last Updated**: February 6, 2026  
**Status**: Ready for implementation  
**Estimated Completion**: 2-3 hours
