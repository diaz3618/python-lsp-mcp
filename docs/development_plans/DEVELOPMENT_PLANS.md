# Python LSP-MCP Development Plans - Master Index

**AI-Agent-Optimized Implementation Guide**

**Purpose**: Organized, feature-specific implementation plans for Python LSP-MCP enhancements  
**Date**: February 6, 2026  
**Version**: 3.0.0 - Complete Modular Structure  
**Target Audience**: AI coding agents (GitHub Copilot, Claude, etc.)

---

## 📋 Document Organization

This development plan is split into **individual feature documents** for maximum AI agent efficiency. Each feature is self-contained with:

- Complete implementation strategy
- Reference implementation analysis
- Step-by-step code examples
- Testing requirements
- Verification checklists

**Benefits**:
- ✅ Focused context per feature
- ✅ Parallel implementation possible
- ✅ Clear dependency tracking
- ✅ Easier updates and maintenance
- ✅ No massive monolithic files

---

## 🎯 All Features Overview

### Refactoring Features (From Reference Implementation)

| Feature ID | Name | Priority | Complexity | Time | Status | Document |
|------------|------|----------|------------|------|--------|----------|
| **FEATURE_01** | Rename Refactoring | HIGH | MEDIUM | 3-4h | ❌ | [📄 FEATURE_01](./FEATURE_01_RENAME_REFACTORING.md) |
| **FEATURE_02** | Backend Switching | MEDIUM | MEDIUM-HIGH | 4-6h | ❌ | [📄 FEATURE_02](./FEATURE_02_BACKEND_SWITCHING.md) |
| **FEATURE_03** | Move Refactoring | MEDIUM | HIGH | 5-7h | ❌ | [📄 FEATURE_03](./FEATURE_03_MOVE_REFACTORING.md) |
| **FEATURE_04** | Change Signature | MEDIUM | HIGH | 4-6h | 📝 TBD | Not yet documented |
| **FEATURE_05** | Pyright Diagnostics | MEDIUM | MEDIUM | 3-4h | 📝 TBD | Not yet documented |

### LSP Method Features (From Original Plans)

| Feature ID | Name | Priority | Complexity | Time | Status | Document |
|------------|------|----------|------------|------|--------|----------|
| **FEATURE_10** | Code Actions | HIGH | MEDIUM | 2-3h | ❌ | [📄 FEATURE_10](./FEATURE_10_CODE_ACTIONS.md) |
| **FEATURE_11** | Document Formatting | HIGH | LOW-MEDIUM | 1-2h | ❌ | [📄 FEATURE_11](./FEATURE_11_DOCUMENT_FORMATTING.md) |
| **FEATURE_12** | Range Formatting | MEDIUM | LOW | 1h | ❌ | [📄 FEATURE_12](./FEATURE_12_RANGE_FORMATTING.md) |
| **FEATURE_13** | Workspace Symbols | MEDIUM | LOW-MEDIUM | 1-2h | ❌ | [📄 FEATURE_13](./FEATURE_13_WORKSPACE_SYMBOLS.md) |

### Additional Features (Future)

| Feature ID | Name | Priority | Complexity | Estimated Time | Status |
|------------|------|----------|------------|----------------|--------|
| **FEATURE_06** | Signature Help | MEDIUM | LOW | 2-3h | 📝 Not documented |
| **FEATURE_07** | Update Document | LOW | MEDIUM | 2-3h | 📝 Not documented |
| **FEATURE_08** | Regex Search | LOW | MEDIUM | 3-4h | 📝 Not documented |
| **FEATURE_09** | Status Tool | LOW | LOW | 2-3h | 📝 Not documented |

**Legend**:
- ❌ NOT STARTED - Feature document complete, ready to implement
- 🟡 IN PROGRESS - Implementation ongoing
- ✅ COMPLETE - Implementation done and tested
- 📝 TBD - Feature document not yet created

---

## 📚 Quick Links by Category

### ✅ Documented & Ready to Implement

**Refactoring (Rope-based)**:
- [FEATURE_01: Rename Refactoring](./FEATURE_01_RENAME_REFACTORING.md) - Safe workspace-wide symbol renaming
- [FEATURE_02: Backend Switching](./FEATURE_02_BACKEND_SWITCHING.md) - Runtime backend selection (Rope vs Pyright)
- [FEATURE_03: Move Refactoring](./FEATURE_03_MOVE_REFACTORING.md) - Relocate functions/classes between modules

**LSP Methods**:
- [FEATURE_10: Code Actions](./FEATURE_10_CODE_ACTIONS.md) - Quick fixes, refactorings, import management
- [FEATURE_11: Document Formatting](./FEATURE_11_DOCUMENT_FORMATTING.md) - Full document PEP 8 formatting
- [FEATURE_12: Range Formatting](./FEATURE_12_RANGE_FORMATTING.md) - Partial document formatting
- [FEATURE_13: Workspace Symbols](./FEATURE_13_WORKSPACE_SYMBOLS.md) - Search symbols across workspace

### 📝 To Be Documented

- FEATURE_04: Change Signature (modify function parameters)
- FEATURE_05: Pyright Diagnostics (type checking)
- FEATURE_06: Signature Help (function signature tooltips)
- FEATURE_07: Update Document (incremental updates)
- FEATURE_08: Regex Search (ripgrep integration)
- FEATURE_09: Status Tool (server status display)

---

## � Recommended Implementation Order

### Phase 1: Foundation (Week 1) - Refactoring Infrastructure

**Start Here** to enable Rope-based refactoring:

1. **[FEATURE_01: Rename Refactoring](./FEATURE_01_RENAME_REFACTORING.md)** (3-4 hours)
   - Add Rope dependency
   - Create refactoring module
   - Implement rename tool
   - **Enables**: Foundation for all Rope refactoring features

2. **[FEATURE_02: Backend Switching](./FEATURE_02_BACKEND_SWITCHING.md)** (4-6 hours)
   - **Requires**: FEATURE_01
   - Backend configuration system
   - Rope client integration
   - Dual-path tool dispatch
   - **Enables**: Runtime switching between Rope (fast) and Pyright (accurate)

### Phase 2: Advanced Refactoring (Week 2)

3. **[FEATURE_03: Move Refactoring](./FEATURE_03_MOVE_REFACTORING.md)** (5-7 hours)
   - **Requires**: FEATURE_01
   - Extend refactoring module
   - Module relocation logic
   - Import update tracking

4. **FEATURE_04: Change Signature** (4-6 hours) - ⚠️ Not yet documented
   - **Requires**: FEATURE_01
   - Parameter modification
   - Call site updates

### Phase 3: LSP Enhancements (Week 3) - Code Quality

**Independent from Rope features** - can implement in parallel:

5. **[FEATURE_10: Code Actions](./FEATURE_10_CODE_ACTIONS.md)** (2-3 hours)
   - Quick fixes and refactorings
   - Import management
   - **High value**: Enables AI to fix errors automatically

6. **[FEATURE_11: Document Formatting](./FEATURE_11_DOCUMENT_FORMATTING.md)** (1-2 hours)
   - Full document PEP 8 formatting
   - **High value**: Essential for code quality

7. **[FEATURE_12: Range Formatting](./FEATURE_12_RANGE_FORMATTING.md)** (1 hour)
   - Partial document formatting
   - **Depends on**: FEATURE_11 pattern

### Phase 4: Workspace Features (Week 4)

8. **[FEATURE_13: Workspace Symbols](./FEATURE_13_WORKSPACE_SYMBOLS.md)** (1-2 hours)
   - Search symbols across workspace
   - Code discovery without file navigation

9. **Additional Features** (TBD)
   - FEATURE_05: Pyright Diagnostics
   - FEATURE_06: Signature Help
   - FEATURE_07: Update Document
   - FEATURE_08: Regex Search
   - FEATURE_09: Status Tool

---

## 🏗️ Current Architecture Overview

Before implementing features, understand the existing architecture:

### Core Files

**`src/python_lsp_mcp/server.py`** (593 lines):
- MCP server creation and tool registration
- Pattern for new tools:
  1. Define Pydantic input model (e.g., `HoverInput`)
  2. Decorate with `@server.call_tool()`
  3. Validate file with `validate_file()`
  4. Get LSP client via `lsp_manager`
  5. Check capability with `check_capability()`
  6. Call `lsp_client.send_request()` with LSP method
  7. Format response as `[{"type": "text", "text": "..."}]`
  8. Handle exceptions with `try/except`

**`src/python_lsp_mcp/lsp_client.py`** (173 lines):
- LSP client wrapper using pygls
- Key methods:
  - `send_request(method, params, timeout=30.0)` - Send LSP request
  - `has_capability(capability_path)` - Check server support
  - `notify_document_open()` - Document lifecycle

**`src/python_lsp_mcp/lsp_manager.py`**:
- Multi-LSP routing by extension/language
- Client lifecycle management

**`tests/test_integration.py`** (integration tests):
- Pattern for new tests:
  1. Create workspace directory
  2. Write sample Python file
  3. Create LSP client
  4. Call tool via MCP
  5. Assert response format and content

### Existing Tools (5 currently implemented)

1. **textDocument_hover** - Type info and documentation
2. **textDocument_definition** - Symbol definitions
3. **textDocument_references** - Find all references
4. **textDocument_documentSymbol** - Document structure
5. **textDocument_completion** - Code completions

---

## 🔍 Reference Implementation Analysis

### Source: repos/python_lsp_mcp-0.3.0

This is a **feature-rich implementation** we're learning from:

**Architecture Highlights**:
- **Dual Backend System**: Rope (fast, local) + Pyright (accurate, type-aware)
- **Runtime Switching**: Change backends without restarting server
- **Rich Refactoring**: Rename, move, change signature using Rope
- **Advanced LSP**: Signature help, diagnostics, incremental updates
- **Developer Tools**: Hot reload, status inspection, search

**Feature Count**: 15 tools (vs our current 5)

**What We Can Learn**:
- ✅ Backend abstraction pattern
- ✅ Rope refactoring patterns
- ✅ Configuration management
- ✅ Error handling strategies
- ✅ Tool description best practices

---

## 📊 Progress Tracking

### Completion Status

**Refactoring Foundation**: 0/2 complete (0%)
- [ ] FEATURE_01: Rename Refactoring
- [ ] FEATURE_02: Backend Switching

**Advanced Refactoring**: 0/2 complete (0%)
- [ ] FEATURE_03: Move Refactoring
- [ ] FEATURE_04: Change Signature (not yet documented)

**LSP Enhancements**: 0/4 complete (0%)
- [ ] FEATURE_10: Code Actions
- [ ] FEATURE_11: Document Formatting
- [ ] FEATURE_12: Range Formatting
- [ ] FEATURE_13: Workspace Symbols

**Additional Features**: 0/5 complete (0%)
- [ ] FEATURE_05: Pyright Diagnostics (not yet documented)
- [ ] FEATURE_06: Signature Help (not yet documented)
- [ ] FEATURE_07: Update Document (not yet documented)
- [ ] FEATURE_08: Regex Search (not yet documented)
- [ ] FEATURE_09: Status Tool (not yet documented)

**Overall Progress**: 0/13 features (0%)

---

## 🎯 Quick Reference

### File Locations

- **Server logic**: `src/python_lsp_mcp/server.py`
- **Integration tests**: `tests/test_integration.py`
- **Configuration**: `src/python_lsp_mcp/config.py`
- **LSP client**: `src/python_lsp_mcp/lsp_client.py`
- **LSP manager**: `src/python_lsp_mcp/lsp_manager.py`
- **Refactoring module**: `src/python_lsp_mcp/refactoring/` (will be created in FEATURE_01)
- **Documentation**: `README.md`

### Useful Commands

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_integration.py::TestIntegration::test_feature -v

# Type check
mypy src/

# Lint
ruff check src/

# Format
ruff format src/

# Test with MCP CLI
python-lsp-mcp --config config.toml --verbose
```

---

## 🧪 Development Best Practices

### Code Patterns to Follow

**1. Input Validation**:
```python
# Always validate file exists first
is_valid, error_msg = validate_file(file_path)
if not is_valid:
    return [{"type": "text", "text": f"Error: {error_msg}"}]
```

**2. Capability Checking**:
```python
# Always check LSP server supports the feature
cap_error = await check_capability(lsp_client, "featureProvider", "feature name")
if cap_error:
    return cap_error
```

**3. Document Lifecycle**:
```python
# Always notify document open before LSP requests
await lsp_client.notify_document_open(str(file_path.absolute()), "python")
```

**4. Error Handling**:
```python
try:
    # ... implementation
except Exception as e:
    logger.error(f"Error in tool_name: {e}", exc_info=True)
    return [{"type": "text", "text": f"Error message: {e}"}]
```

**5. Response Formatting**:
```python
# Always return list of dicts with type and text
return [{"type": "text", "text": "result message"}]
```

### Testing Patterns

**Integration Test Template**:
```python
@pytest.mark.asyncio
async def test_feature_request(self, workspace_dir, sample_python_file):
    """Test [feature] request end-to-end."""
    config = create_test_config(workspace_dir)
    config.workspace = workspace_dir
    
    server, manager = create_server(config)
    
    try:
        await manager.start_all()
        
        arguments = {
            "file": str(sample_python_file),
            # ... other arguments
        }
        
        result = await server.call_tool("tool_name", arguments)
        
        # Verify response format
        assert isinstance(result, list)
        assert len(result) > 0
        assert "type" in result[0]
        assert "text" in result[0]
        
        # Verify content
        text = result[0]["text"]
        assert "expected content" in text.lower()
        
    finally:
        await manager.shutdown_all()
```

---

## 📚 Additional Resources

### Documentation
- **MCP Specification**: https://modelcontextprotocol.io/specification/draft
- **LSP Specification**: https://microsoft.github.io/language-server-protocol/
- **Rope Documentation**: https://github.com/python-rope/rope
- **Pyright Documentation**: https://github.com/microsoft/pyright
- **pylsp**: https://github.com/python-lsp/python-lsp-server

### Reference Implementations
- **repos/python_lsp_mcp-0.3.0**: Complete feature-rich implementation
- **Rope Examples**: https://rope.readthedocs.io/en/latest/
- **LSP Samples**: https://github.com/microsoft/language-server-protocol/tree/main/samples

---

## 🚀 Getting Started

### To Implement a Feature:

1. **Read feature document**: Start with `FEATURE_XX_NAME.md`
2. **Check dependencies**: Ensure prerequisite features are complete
3. **Review reference**: Study `repos/python_lsp_mcp-0.3.0` implementation (if applicable)
4. **Follow phases**: Implement step-by-step as documented
5. **Test thoroughly**: Run unit tests, integration tests, manual verification
6. **Update documentation**: README.md, this file's progress tracking

### To Create a New Feature Document:

Use this template structure:

```markdown
# Feature: [Feature Name]

**Feature ID**: FEATURE_XX
**Priority**: HIGH/MEDIUM/LOW
**Complexity**: LOW/MEDIUM/HIGH
**Estimated Time**: X-Y hours
**Implementation Status**: ❌ NOT STARTED
**LSP Method**: method_name (if applicable)
**LSP Capability**: capabilityName (if applicable)

---

## Overview
[What this feature does and why it matters]

## Current State Analysis
[What we have, what we need, gaps from reference]

## Implementation Strategy
[Phase-by-phase implementation steps with code examples]

## Testing Plan
[Unit tests, integration tests, verification]

## Verification Checklist
[Checkboxes for completion criteria]

## Usage Examples
[Practical examples of tool usage]

## References
[Links to specs, docs, reference implementations]
```

---

## 💡 Key Decisions

### Why Modular Feature Documents?

**Problem**: 1672-line monolithic file was hard for AI agents to:
- Navigate and find relevant sections
- Load into context window efficiently
- Update without affecting unrelated content
- Implement in parallel

**Solution**: Split into self-contained feature documents
- ✅ Each feature is 300-600 lines (fits well in context)
- ✅ Clear file naming (`FEATURE_XX_NAME.md`)
- ✅ No cross-referencing needed within feature docs
- ✅ Enables parallel implementation by multiple agents/developers

### Why Two Feature Categories?

**Refactoring Features** (FEATURE_01-09):
- From reference implementation (repos/v0.3.0)
- Rope-based or Pyright-based
- More complex, require new dependencies
- 3-7 hours each

**LSP Method Features** (FEATURE_10+):
- From original development plans
- Use existing LSP servers (pylsp/pyright)
- Simpler, extend existing patterns
- 1-3 hours each

---

**End of Master Development Plans v3.0.0**

**Last Updated**: February 6, 2026  
**Next Steps**: Choose a feature from the recommended order above and start implementation!


**Priority**: HIGH  
**Complexity**: MEDIUM  
**Estimated Time**: 2-3 hours  
**Files to Modify**: `server.py`, `test_integration.py`

#### Goal

Enable AI agents to:
- Discover available quick fixes and refactorings at a position
- Get code actions for diagnostics (errors/warnings)
- Apply automatic fixes (add imports, format code, extract functions)

**Why Critical**: Core feature for code quality - enables AI to fix errors automatically and suggest improvements.

#### Prerequisites

✅ **Already in place**:
- MCP server framework (`server.py`)
- LSP client with `send_request()` (`lsp_client.py`)
- Pattern for tool implementation (existing 5 tools)
- Integration test framework (`test_integration.py`)

⚠️ **May need verification**:
- pylsp supports code actions (requires plugins like rope, autopep8)
- LSP server capabilities include `codeActionProvider`

#### LSP Specification Reference

**Method**: `textDocument/codeAction`  
**Capability**: `codeActionProvider` (check via `has_capability("codeActionProvider")`)

**Request**:
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

**Response**: `CodeAction[]` or `Command[]`

**CodeAction structure**:
```python
{
    "title": "Add import 'import pandas as pd'",
    "kind": "quickfix",
    "diagnostics": [...],  # Related diagnostics
    "isPreferred": false,
    "edit": {  # WorkspaceEdit
        "changes": {
            "file:///path/to/file.py": [
                {
                    "range": {...},
                    "newText": "import pandas as pd\n"
                }
            ]
        }
    },
    "command": {...}  # Optional: command to execute
}
```

**CodeActionKind enum** (filter types):
- `quickfix` - Fix errors/warnings
- `refactor` - General refactoring
- `refactor.extract` - Extract function/variable
- `refactor.inline` - Inline function/variable
- `refactor.rewrite` - Rewrite code
- `source` - Source-level actions
- `source.organizeImports` - Sort imports

#### Implementation Steps

**Step 1: Define Input Model** (in `server.py`, after existing input models ~line 65)

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
        description="Filter by CodeActionKind (e.g., 'quickfix', 'refactor', 'source.organizeImports')"
    )
    lsp_id: str | None = Field(None, description="Specific LSP server ID to use (optional)")
```

**Step 2: Implement Tool Handler** (in `server.py`, after `textDocument_completion` tool ~line 520)

```python
    # Tool: textDocument/codeAction
    @server.call_tool()
    async def textDocument_codeAction(arguments: dict[str, Any]) -> list[Any]:
        """Get available code actions (quick fixes, refactorings) for a range.

        Returns actions like: add missing imports, extract function, format code, etc.
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
                    "diagnostics": [],  # Could be enhanced to pass diagnostics
                    "only": [input_data.kind] if input_data.kind else []
                }
            }

            response = await lsp_client.send_request("textDocument/codeAction", params)

            # Format response
            if not response:
                return [{"type": "text", "text": "No code actions available"}]

            result_lines = [f"Found {len(response)} code action(s):"]
            for idx, action in enumerate(response, 1):
                # Handle both CodeAction and Command
                if isinstance(action, dict):
                    title = action.get("title", "Unknown action")
                    kind = action.get("kind", "unknown")
                else:
                    title = getattr(action, "title", "Unknown action")
                    kind = getattr(action, "kind", "unknown")

                result_lines.append(f"\n{idx}. {title}")
                result_lines.append(f"   Kind: {kind}")

                # Show edit preview if available
                if isinstance(action, dict) and "edit" in action:
                    edit = action["edit"]
                    if "changes" in edit:
                        changes_count = sum(len(edits) for edits in edit["changes"].values())
                        result_lines.append(f"   Edits: {changes_count} text edit(s)")

            return [{"type": "text", "text": "\n".join(result_lines)}]

        except Exception as e:
            logger.error(f"Error in textDocument_codeAction: {e}", exc_info=True)
            return [{"type": "text", "text": f"Error getting code actions: {e}"}]
```

**Step 3: Add Integration Test** (in `tests/test_integration.py`, after existing tests ~line 150)

```python
    @pytest.mark.asyncio
    async def test_code_action_request(self, workspace_dir, sample_python_file):
        """Test code action request end-to-end."""
        config = create_test_config(workspace_dir)
        config.workspace = workspace_dir

        # Create server
        server, manager = create_server(config)

        try:
            # Start LSP clients
            await manager.start_all()

            # Get code actions for a range (e.g., function definition)
            arguments = {
                "file": str(sample_python_file),
                "line_start": 5,  # Adjust based on sample_python_file content
                "character_start": 0,
                "line_end": 7,
                "character_end": 0,
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
```

**Step 4: Update README.md** (add to "Available Tools" section ~line 30)

```markdown
- `textDocument_codeAction`: Get available code actions (quick fixes, refactorings, import management)
```

#### Testing Requirements

**Unit Test Scenarios**:
1. ✅ Code actions available (multiple actions returned)
2. ✅ No code actions (empty result)
3. ✅ File validation (file doesn't exist)
4. ✅ Capability check (LSP doesn't support code actions)
5. ✅ Filter by kind (`quickfix`, `refactor`, `source.organizeImports`)
6. ✅ LSP server timeout
7. ✅ Invalid range (end before start)

**Integration Test Verification**:
- Can retrieve code actions from real LSP server (pylsp)
- Response format matches MCP expectations
- Error messages are user-friendly

**Manual Testing** (with MCP CLI):
```bash
# Test with code that has an error (undefined name)
echo 'def foo():\n    return bar' > /tmp/test.py

# Call tool
python-lsp-mcp --config config.toml
# In MCP client:
textDocument_codeAction(
    file="/tmp/test.py",
    line_start=1,
    character_start=11,
    line_end=1,
    character_end=14
)
# Should suggest: "Add import", "Ignore error", etc.
```

#### Integration Points

**Dependencies**:
- `validate_file()` helper (already exists)
- `check_capability()` helper (already exists)
- `lsp_manager.get_lsp_by_extension()` (already exists)
- `lsp_client.send_request()` (already exists)

**Affects**:
- Tool registration in `create_server()` (adds 6th tool)
- README.md documentation (Available Tools section)
- Integration tests (adds 1 new test)

**pylsp Plugin Requirements** (for full functionality):
- **rope** - Refactoring actions (`pip install "python-lsp-server[rope]"`)
- **autopep8** - PEP 8 fixes (`pip install autopep8`)
- **python-lsp-isort** - Import organization (`pip install python-lsp-isort`)

#### Verification Checklist

Before considering this feature complete:

- [ ] Input model defined with all required fields
- [ ] Tool handler follows existing pattern (validate → check capability → request → format → error handling)
- [ ] Response format matches MCP specification (`[{"type": "text", "text": "..."}]`)
- [ ] Integration test passes with real LSP server
- [ ] README.md updated with new tool
- [ ] Manual testing shows code actions for common scenarios:
  - [ ] Missing imports
  - [ ] PEP 8 violations
  - [ ] Unused imports (with isort plugin)
  - [ ] Extract function (with rope plugin)
- [ ] Error messages are clear and actionable
- [ ] Logs show no exceptions (check with `--verbose`)
- [ ] All 28+ tests still pass (`pytest tests/ -v`)

---

### Feature 1.2: textDocument/formatting

**Priority**: HIGH  
**Complexity**: LOW-MEDIUM  
**Estimated Time**: 1-2 hours  
**Files to Modify**: `server.py`, `test_integration.py`

#### Goal

Enable AI agents to:
- Format entire Python files according to style guidelines
- Apply PEP 8 formatting automatically
- Use configurable formatters (autopep8, yapf, black)

**Why Critical**: Essential for code quality - ensures all AI-generated code follows Python conventions.

#### Prerequisites

✅ **Already in place**:
- MCP server framework
- LSP client with `send_request()`
- Pattern for tool implementation

⚠️ **May need verification**:
- pylsp supports formatting (requires formatter plugins)
- LSP server capabilities include `documentFormattingProvider`

#### LSP Specification Reference

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

**TextEdit structure**:
```python
{
    "range": {
        "start": {"line": 0, "character": 0},
        "end": {"line": 10, "character": 0}
    },
    "newText": "formatted code..."
}
```

#### Implementation Steps

**Step 1: Define Input Model** (in `server.py`)

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

**Step 2: Implement Tool Handler** (in `server.py`)

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

            response = await lsp_client.send_request("textDocument/formatting", params)

            # Format response
            if not response:
                return [{"type": "text", "text": "No formatting changes needed"}]

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
                    result_lines.append(f"Preview: {new_text[:100]}{'...' if len(new_text) > 100 else ''}")

            return [{"type": "text", "text": "\n".join(result_lines)}]

        except Exception as e:
            logger.error(f"Error in textDocument_formatting: {e}", exc_info=True)
            return [{"type": "text", "text": f"Error formatting document: {e}"}]
```

**Step 3: Add Integration Test** (in `tests/test_integration.py`)

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

            # Verify content indicates formatting applied
            text = result[0]["text"]
            assert "edit" in text.lower() or "no formatting" in text.lower()

        finally:
            await manager.shutdown_all()
```

**Step 4: Update README.md**

```markdown
- `textDocument_formatting`: Format entire document according to style guidelines (PEP 8)
```

#### Testing Requirements

**Test Scenarios**:
1. ✅ Format messy code (should apply edits)
2. ✅ Format already-formatted code (no edits needed)
3. ✅ File validation
4. ✅ Capability check
5. ✅ Custom formatting options (tabSize, insertSpaces)
6. ✅ LSP server timeout

#### Verification Checklist

- [ ] Input model defined
- [ ] Tool handler implemented following pattern
- [ ] Integration test passes
- [ ] README.md updated
- [ ] Manual testing with messy code shows formatting applied
- [ ] Works with autopep8 (default pylsp formatter)
- [ ] All tests pass

---

### Feature 1.3: textDocument/rangeFormatting

**Priority**: MEDIUM  
**Complexity**: LOW  
**Estimated Time**: 1 hour  
**Files to Modify**: `server.py`, `test_integration.py`

#### Goal

Enable AI agents to format specific code ranges instead of entire files.

**Why Useful**: Performance optimization - format only newly generated code without reformatting entire file.

#### Implementation Steps

**Similar to textDocument/formatting**, but:
1. Add range parameters (`line_start`, `character_start`, `line_end`, `character_end`) to input model
2. Send `textDocument/rangeFormatting` request with range
3. Test with partial file selection

**Refer to Feature 1.2 for detailed implementation pattern.**

---

### Feature 1.4: textDocument/rename

**Priority**: HIGH  
**Complexity**: MEDIUM  
**Estimated Time**: 2-3 hours  
**Files to Modify**: `server.py`, `test_integration.py`

#### Goal

Enable AI agents to rename symbols across entire workspace safely.

**Why Critical**: Essential for refactoring - rename variables/functions without breaking code.

#### LSP Specification Reference

**Method**: `textDocument/rename`  
**Capability**: `renameProvider`

**Request**:
```python
{
    "textDocument": {"uri": "file:///path/to/file.py"},
    "position": {"line": 10, "character": 5},
    "newName": "new_function_name"
}
```

**Response**: `WorkspaceEdit` or `null`

**WorkspaceEdit structure**:
```python
{
    "changes": {
        "file:///path/to/file1.py": [
            {"range": {...}, "newText": "new_function_name"}
        ],
        "file:///path/to/file2.py": [
            {"range": {...}, "newText": "new_function_name"}
        ]
    }
}
```

#### Implementation Steps

**Step 1: Define Input Model**

```python
class RenameInput(BaseModel):
    """Input for textDocument/rename tool."""

    file: str = Field(..., description="Path to the Python file")
    line: int = Field(..., description="Line number (0-indexed)")
    character: int = Field(..., description="Character position (0-indexed)")
    new_name: str = Field(..., description="New name for the symbol")
    lsp_id: str | None = Field(None, description="Specific LSP server ID to use (optional)")
```

**Step 2: Implement Tool Handler**

```python
    # Tool: textDocument/rename
    @server.call_tool()
    async def textDocument_rename(arguments: dict[str, Any]) -> list[Any]:
        """Rename symbol across entire workspace.

        Returns all file changes needed to rename the symbol safely.
        """
        input_data = RenameInput(**arguments)
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

        try:
            # Ensure client is started
            if not lsp_client.is_started():
                await lsp_client.start()

            # Check capability
            cap_error = await check_capability(lsp_client, "renameProvider", "rename")
            if cap_error:
                return cap_error

            # Notify document open
            await lsp_client.notify_document_open(str(file_path.absolute()), "python")

            # Build request parameters
            params = {
                "textDocument": {"uri": f"file://{file_path.absolute()}"},
                "position": {
                    "line": input_data.line,
                    "character": input_data.character
                },
                "newName": input_data.new_name
            }

            response = await lsp_client.send_request("textDocument/rename", params)

            # Format response
            if not response:
                return [{"type": "text", "text": "Rename not possible (symbol not renameable or not found)"}]

            # Response is WorkspaceEdit with changes
            changes = response.get("changes", {}) if isinstance(response, dict) else {}
            
            if not changes:
                return [{"type": "text", "text": "No changes needed for rename"}]

            result_lines = [f"Rename successful - {len(changes)} file(s) affected:"]
            
            for file_uri, edits in changes.items():
                file_name = Path(file_uri.replace("file://", "")).name
                result_lines.append(f"\n{file_name}:")
                result_lines.append(f"  {len(edits)} edit(s)")
                
                # Show first edit preview
                if edits:
                    first_edit = edits[0]
                    if isinstance(first_edit, dict):
                        range_info = first_edit.get("range", {})
                        start = range_info.get("start", {})
                        line = start.get("line", 0) if isinstance(start, dict) else getattr(start, "line", 0)
                    else:
                        line = getattr(first_edit.range.start, "line", 0)
                    
                    result_lines.append(f"  First edit at line {line + 1}")

            return [{"type": "text", "text": "\n".join(result_lines)}]

        except Exception as e:
            logger.error(f"Error in textDocument_rename: {e}", exc_info=True)
            return [{"type": "text", "text": f"Error renaming symbol: {e}"}]
```

**Step 3: Add Integration Test**

```python
    @pytest.mark.asyncio
    async def test_rename_request(self, workspace_dir, sample_python_file):
        """Test rename request end-to-end."""
        config = create_test_config(workspace_dir)
        config.workspace = workspace_dir

        # Create server
        server, manager = create_server(config)

        try:
            # Start LSP clients
            await manager.start_all()

            # Rename a function
            arguments = {
                "file": str(sample_python_file),
                "line": 5,  # Line with function definition
                "character": 4,  # Position on function name
                "new_name": "renamed_function"
            }

            result = await server.call_tool("textDocument_rename", arguments)

            # Verify response format
            assert isinstance(result, list)
            assert len(result) > 0
            assert "type" in result[0]
            assert "text" in result[0]

            # Verify content indicates rename status
            text = result[0]["text"]
            assert "rename" in text.lower()

        finally:
            await manager.shutdown_all()
```

**Step 4: Update README.md**

```markdown
- `textDocument_rename`: Rename symbol across entire workspace safely
```

#### Testing Requirements

**Test Scenarios**:
1. ✅ Rename function (single file)
2. ✅ Rename function (multiple files)
3. ✅ Rename variable (local scope)
4. ✅ Invalid position (no symbol)
5. ✅ File validation
6. ✅ Capability check (requires rope plugin)

**Requires**: `pip install "python-lsp-server[rope]"` for rename support

#### Verification Checklist

- [ ] Input model defined
- [ ] Tool handler implemented
- [ ] Integration test passes
- [ ] README.md updated
- [ ] Manual testing with rope plugin installed
- [ ] Workspace edits correctly formatted
- [ ] All tests pass

---

## Phase 2: Workspace-Level Features

### Feature 2.1: workspace/symbol

**Priority**: MEDIUM  
**Complexity**: LOW-MEDIUM  
**Estimated Time**: 1-2 hours  
**Files to Modify**: `server.py`, `test_integration.py`

#### Goal

Enable AI agents to search for symbols (functions, classes, variables) across entire workspace by name.

**Why Useful**: Code discovery - find definitions without knowing exact file location.

#### LSP Specification Reference

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

#### Implementation Steps

**Step 1: Define Input Model**

```python
class WorkspaceSymbolInput(BaseModel):
    """Input for workspace/symbol tool."""

    query: str = Field(..., description="Search query for symbol name")
    lsp_id: str | None = Field(None, description="Specific LSP server ID to use (optional)")
```

**Step 2: Implement Tool Handler**

```python
    # Tool: workspace/symbol
    @server.call_tool()
    async def workspace_symbol(arguments: dict[str, Any]) -> list[Any]:
        """Search for symbols across entire workspace by name.

        Returns functions, classes, and variables matching the query.
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

            response = await lsp_client.send_request("workspace/symbol", params)

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
                12: "Function",
                13: "Variable",
                14: "Constant",
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

**Step 3: Add Integration Test**

```python
    @pytest.mark.asyncio
    async def test_workspace_symbol_request(self, workspace_dir, sample_python_file):
        """Test workspace symbol search end-to-end."""
        config = create_test_config(workspace_dir)
        config.workspace = workspace_dir

        # Create server
        server, manager = create_server(config)

        try:
            # Start LSP clients
            await manager.start_all()

            # Search for symbols
            arguments = {
                "query": "def"  # Search for function definitions
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
```

**Step 4: Update README.md**

```markdown
- `workspace_symbol`: Search for symbols (functions, classes, variables) across entire workspace
```

#### Testing Requirements

**Test Scenarios**:
1. ✅ Search finds results
2. ✅ Search finds no results
3. ✅ Empty query
4. ✅ Case-insensitive search
5. ✅ Capability check

#### Verification Checklist

- [ ] Input model defined
- [ ] Tool handler implemented
- [ ] Integration test passes
- [ ] README.md updated
- [ ] Works with workspace containing multiple files
- [ ] Results limited to reasonable count (20)
- [ ] All tests pass

---

## Summary of Implementation Priorities

### Phase 1 (Week 1): Code Quality Essentials
1. ✅ **textDocument/codeAction** (HIGH) - 2-3 hours
2. ✅ **textDocument/formatting** (HIGH) - 1-2 hours
3. ✅ **textDocument/rangeFormatting** (MEDIUM) - 1 hour
4. ✅ **textDocument/rename** (HIGH) - 2-3 hours

**Total Phase 1**: ~6-9 hours

### Phase 2 (Week 2): Workspace Features
1. ✅ **workspace/symbol** (MEDIUM) - 1-2 hours
2. Additional features from FEATURE_ADDITIONS.md as time permits

---

## Development Best Practices

### Code Patterns to Follow

**1. Input Validation**:
```python
# Always validate file exists first
is_valid, error_msg = validate_file(file_path)
if not is_valid:
    return [{"type": "text", "text": f"Error: {error_msg}"}]
```

**2. Capability Checking**:
```python
# Always check LSP server supports the feature
cap_error = await check_capability(lsp_client, "featureProvider", "feature name")
if cap_error:
    return cap_error
```

**3. Document Lifecycle**:
```python
# Always notify document open before LSP requests
await lsp_client.notify_document_open(str(file_path.absolute()), "python")
```

**4. Error Handling**:
```python
try:
    # ... implementation
except Exception as e:
    logger.error(f"Error in tool_name: {e}", exc_info=True)
    return [{"type": "text", "text": f"Error message: {e}"}]
```

**5. Response Formatting**:
```python
# Always return list of dicts with type and text
return [{"type": "text", "text": "result message"}]
```

### Testing Patterns

**Integration Test Template**:
```python
@pytest.mark.asyncio
async def test_feature_request(self, workspace_dir, sample_python_file):
    """Test [feature] request end-to-end."""
    config = create_test_config(workspace_dir)
    config.workspace = workspace_dir
    
    server, manager = create_server(config)
    
    try:
        await manager.start_all()
        
        arguments = {
            "file": str(sample_python_file),
            # ... other arguments
        }
        
        result = await server.call_tool("tool_name", arguments)
        
        # Verify response format
        assert isinstance(result, list)
        assert len(result) > 0
        assert "type" in result[0]
        assert "text" in result[0]
        
        # Verify content
        text = result[0]["text"]
        assert "expected content" in text.lower()
        
    finally:
        await manager.shutdown_all()
```

---

## Appendix: Quick Reference

### LSP Methods by Priority

**HIGH Priority** (Implement First):
- `textDocument/codeAction` - Quick fixes and refactorings
- `textDocument/formatting` - Full document formatting
- `textDocument/rename` - Safe symbol renaming

**MEDIUM Priority**:
- `textDocument/rangeFormatting` - Partial document formatting
- `workspace/symbol` - Workspace-wide symbol search

**LOW Priority** (Future):
- `textDocument/documentHighlight` - Highlight symbol occurrences
- `textDocument/foldingRange` - Code folding ranges
- `textDocument/semanticTokens` - Semantic highlighting

### File Locations

- **Server logic**: `src/python_lsp_mcp/server.py`
- **Integration tests**: `tests/test_integration.py`
- **Configuration**: `src/python_lsp_mcp/config.py`
- **LSP client**: `src/python_lsp_mcp/lsp_client.py`
- **Documentation**: `README.md`

### Useful Commands

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_integration.py::TestIntegration::test_feature -v

# Type check
mypy src/

# Lint
ruff check src/

# Format
ruff format src/

# Test with MCP CLI
python-lsp-mcp --config config.toml --verbose
```

---

**End of Development Plans v1.0.0**
