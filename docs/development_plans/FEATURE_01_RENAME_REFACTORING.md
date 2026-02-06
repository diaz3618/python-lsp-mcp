# Feature: textDocument/rename - Safe Symbol Renaming

**Feature ID**: FEATURE_01  
**Priority**: HIGH  
**Complexity**: MEDIUM  
**Estimated Time**: 3-4 hours  
**Implementation Status**: ❌ NOT STARTED  
**Reference Implementation**: `repos/python_lsp_mcp-0.3.0/src/rope_mcp/tools/rename.py`

---

## Overview

Enable safe, workspace-wide symbol renaming using Rope refactoring library. This provides accurate renaming that respects Python scoping rules and updates all references across the codebase.

**Why Critical**: Essential refactoring feature for maintaining code quality during AI-assisted development. Prevents breaking changes from manual find-replace operations.

---

## Current State Analysis

### What We Have ✅
- MCP server framework (`src/python_lsp_mcp/server.py`)
- LSP client with `send_request()` (`src/python_lsp_mcp/lsp_client.py`)
- Pattern for tool implementation (5 existing tools)
- Integration test framework (`tests/test_integration.py`)

### What We Need ⚠️
- Rope library integration (new dependency)
- Refactoring utilities module
- LSP rename capability checking
- Workspace-wide file modification logic

### Gaps from Reference Implementation 🔍

**From `repos/python_lsp_mcp-0.3.0/src/rope_mcp/tools/rename.py`**:
- Uses Rope's `Rename` refactoring class
- Workspace/project management
- File resource handling
- Change application logic
- Preview mode support

---

## Implementation Strategy

### Phase 1: Add Rope Dependency

**File**: `pyproject.toml`

**Action**: Add rope to dependencies:
```toml
dependencies = [
    # ... existing dependencies
    "rope>=1.13.0",
]
```

**Run after**:
```bash
pip install -e ".[dev]"
# or
uv pip install -e ".[dev]"
```

---

### Phase 2: Create Refactoring Utilities Module

**File**: `src/python_lsp_mcp/refactoring/__init__.py` (NEW)

**Purpose**: Wrapper around Rope for refactoring operations

**Implementation**:
```python
"""Refactoring utilities using Rope library."""

import os
from pathlib import Path
from typing import Optional

import rope.base.project
from rope.base.resources import File
from rope.refactor.rename import Rename


class RopeRefactoring:
    """Wrapper for Rope refactoring operations."""

    def __init__(self):
        self._projects: dict[str, rope.base.project.Project] = {}

    def get_project(self, workspace: str) -> rope.base.project.Project:
        """Get or create a Rope project for workspace."""
        workspace = os.path.abspath(workspace)

        if workspace not in self._projects:
            # Create project with caching disabled (use .ropeproject if needed)
            project = rope.base.project.Project(
                workspace,
                ropefolder=None,  # Disable .ropeproject caching
            )
            self._projects[workspace] = project

        return self._projects[workspace]

    def get_resource(self, project: rope.base.project.Project, file_path: str) -> File:
        """Get Rope resource for a file."""
        abs_path = os.path.abspath(file_path)
        project_root = project.root.real_path

        if abs_path.startswith(project_root):
            rel_path = os.path.relpath(abs_path, project_root)
        else:
            rel_path = abs_path

        return project.get_file(rel_path)

    def rename_symbol(
        self,
        file_path: str,
        offset: int,
        new_name: str,
        workspace: Optional[str] = None,
    ) -> dict:
        """Rename a symbol at the given offset.

        Args:
            file_path: Absolute path to the Python file
            offset: Character offset in the file
            new_name: New name for the symbol
            workspace: Workspace root (defaults to file's parent directory)

        Returns:
            Dict with:
                - success: bool
                - changes: List of {file, old_content, new_content}
                - files_modified: List of modified file paths
                - error: Optional error message
        """
        try:
            # Determine workspace
            if workspace is None:
                workspace = str(Path(file_path).parent)

            # Get Rope project and resource
            project = self.get_project(workspace)
            resource = self.get_resource(project, file_path)

            # Create rename refactoring
            rename = Rename(project, resource, offset)

            # Get changes
            changes = rename.get_changes(new_name, docs=True)

            # Collect change details
            change_list = []
            files_modified = set()

            for change in changes.changes:
                change_resource = change.resource
                old_content = change_resource.read()
                new_content = change.get_new_contents()

                change_list.append({
                    "file": change_resource.real_path,
                    "old_content": old_content,
                    "new_content": new_content,
                })
                files_modified.add(change_resource.real_path)

            return {
                "success": True,
                "changes": change_list,
                "files_modified": list(files_modified),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "changes": [],
                "files_modified": [],
            }

    def apply_changes(self, changes_dict: dict) -> dict:
        """Apply changes to files.

        Args:
            changes_dict: Output from rename_symbol() with success=True

        Returns:
            Dict with success status and files written
        """
        if not changes_dict.get("success"):
            return {"success": False, "error": "No changes to apply"}

        try:
            files_written = []

            for change in changes_dict["changes"]:
                file_path = change["file"]
                new_content = change["new_content"]

                # Write new content
                Path(file_path).write_text(new_content, encoding="utf-8")
                files_written.append(file_path)

            return {
                "success": True,
                "files_written": files_written,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def close_all(self):
        """Close all Rope projects."""
        for project in self._projects.values():
            project.close()
        self._projects.clear()


# Global instance
_refactoring: Optional[RopeRefactoring] = None


def get_refactoring() -> RopeRefactoring:
    """Get global refactoring instance."""
    global _refactoring
    if _refactoring is None:
        _refactoring = RopeRefactoring()
    return _refactoring
```

---

### Phase 3: Add MCP Tool

**File**: `src/python_lsp_mcp/server.py`

**Location**: After `textDocument_completion` tool (~line 520)

**Step 3.1: Add Input Model** (after existing input models ~line 65)

```python
class RenameInput(BaseModel):
    """Input for textDocument_rename tool."""

    file: str = Field(..., description="Path to the Python file")
    line: int = Field(..., description="Line number (0-indexed)")
    character: int = Field(..., description="Character position (0-indexed)")
    new_name: str = Field(..., description="New name for the symbol")
    preview: bool = Field(
        False,
        description="If True, show changes without applying them"
    )
    workspace: str | None = Field(
        None,
        description="Workspace root directory (auto-detected if not provided)"
    )
```

**Step 3.2: Add Tool Handler** (after `textDocument_completion` ~line 520)

```python
    # Tool: textDocument_rename
    @server.call_tool()
    async def textDocument_rename(arguments: dict[str, Any]) -> list[Any]:
        """Rename a symbol across the entire workspace.

        Uses Rope refactoring to safely rename symbols while respecting
        Python scoping rules and updating all references.
        """
        input_data = RenameInput(**arguments)
        file_path = Path(input_data.file)

        # Validate file exists
        is_valid, error_msg = validate_file(file_path)
        if not is_valid:
            return [{"type": "text", "text": f"Error: {error_msg}"}]

        try:
            # Import refactoring module
            from .refactoring import get_refactoring

            # Read file to calculate offset
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            # Calculate character offset
            offset = sum(len(line) + 1 for line in lines[:input_data.line])
            offset += input_data.character

            # Perform rename refactoring
            refactoring = get_refactoring()
            result = refactoring.rename_symbol(
                file_path=str(file_path),
                offset=offset,
                new_name=input_data.new_name,
                workspace=input_data.workspace,
            )

            if not result["success"]:
                return [{"type": "text", "text": f"Error: {result['error']}"}]

            # Format preview or apply changes
            if input_data.preview:
                # Show preview of changes
                result_lines = [
                    f"Rename Preview: {len(result['files_modified'])} file(s) would be modified:",
                    ""
                ]

                for change in result["changes"]:
                    file_name = Path(change["file"]).name
                    result_lines.append(f"📄 {file_name}")

                result_lines.append("")
                result_lines.append("To apply changes, call again with preview=false")

                return [{"type": "text", "text": "\n".join(result_lines)}]

            else:
                # Apply changes
                apply_result = refactoring.apply_changes(result)

                if not apply_result["success"]:
                    return [{"type": "text", "text": f"Error applying changes: {apply_result['error']}"}]

                result_lines = [
                    f"✓ Renamed symbol to '{input_data.new_name}'",
                    f"✓ Modified {len(apply_result['files_written'])} file(s):",
                    ""
                ]

                for file in apply_result["files_written"]:
                    file_name = Path(file).name
                    result_lines.append(f"  - {file_name}")

                return [{"type": "text", "text": "\n".join(result_lines)}]

        except Exception as e:
            logger.error(f"Error in textDocument_rename: {e}", exc_info=True)
            return [{"type": "text", "text": f"Error renaming symbol: {e}"}]
```

---

### Phase 4: Add Integration Test

**File**: `tests/test_integration.py`

**Location**: After existing tests (~line 200)

```python
@pytest.mark.asyncio
async def test_rename_symbol(self, workspace_dir, sample_python_file):
    """Test symbol renaming with Rope."""
    config = create_test_config(workspace_dir)
    config.workspace = workspace_dir

    # Create a second file that imports from the first
    second_file = workspace_dir / "test_import.py"
    second_file.write_text(
        "from sample import greet\n\n"
        "result = greet('World')\n"
    )

    server, manager = create_server(config)

    try:
        # Preview rename
        arguments = {
            "file": str(sample_python_file),
            "line": 5,  # Line with 'greet' function definition
            "character": 4,
            "new_name": "say_hello",
            "preview": True,
        }

        result = await server.call_tool("textDocument_rename", arguments)

        # Verify preview format
        assert isinstance(result, list)
        assert len(result) > 0
        text = result[0]["text"]
        assert "preview" in text.lower()
        assert "file(s) would be modified" in text.lower()

        # Apply rename
        arguments["preview"] = False
        result = await server.call_tool("textDocument_rename", arguments)

        # Verify success
        assert isinstance(result, list)
        text = result[0]["text"]
        assert "renamed" in text.lower() or "modified" in text.lower()

        # Verify files were actually modified
        new_content = sample_python_file.read_text()
        assert "say_hello" in new_content
        assert "greet" not in new_content or "greet" in "# greet"  # Allow in comments

        second_content = second_file.read_text()
        assert "say_hello" in second_content

    finally:
        await manager.shutdown_all()
```

---

## Testing Plan

### Unit Tests

**File**: `tests/test_refactoring.py` (NEW)

```python
"""Unit tests for Rope refactoring utilities."""

import pytest
from pathlib import Path
from src.python_lsp_mcp.refactoring import get_refactoring


def test_rename_simple_function(tmp_path):
    """Test renaming a simple function."""
    # Create test file
    test_file = tmp_path / "test.py"
    test_file.write_text(
        "def old_name():\n"
        "    return 'hello'\n"
        "\n"
        "result = old_name()\n"
    )

    # Calculate offset for function name (line 0, char 4)
    offset = 4

    # Perform rename
    refactoring = get_refactoring()
    result = refactoring.rename_symbol(
        file_path=str(test_file),
        offset=offset,
        new_name="new_name",
    )

    # Verify
    assert result["success"]
    assert len(result["changes"]) == 1
    assert "new_name" in result["changes"][0]["new_content"]
    assert "old_name" not in result["changes"][0]["new_content"]


def test_rename_across_files(tmp_path):
    """Test renaming a symbol referenced across multiple files."""
    # Create module file
    module_file = tmp_path / "mymodule.py"
    module_file.write_text(
        "def utility_func():\n"
        "    return 42\n"
    )

    # Create file that imports it
    import_file = tmp_path / "main.py"
    import_file.write_text(
        "from mymodule import utility_func\n"
        "\n"
        "value = utility_func()\n"
    )

    # Calculate offset for function name in module_file
    offset = 4  # "def utility_func()"

    # Perform rename
    refactoring = get_refactoring()
    result = refactoring.rename_symbol(
        file_path=str(module_file),
        offset=offset,
        new_name="helper_func",
        workspace=str(tmp_path),
    )

    # Verify both files are in changes
    assert result["success"]
    assert len(result["files_modified"]) == 2

    # Apply changes
    apply_result = refactoring.apply_changes(result)
    assert apply_result["success"]

    # Verify both files were updated
    module_content = module_file.read_text()
    assert "helper_func" in module_content

    import_content = import_file.read_text()
    assert "helper_func" in import_content
    assert "utility_func" not in import_content
```

### Integration Test (Already covered in Phase 4 above)

---

## Verification Checklist

Before marking complete:

- [ ] Rope dependency added to `pyproject.toml`
- [ ] Refactoring module created with `RopeRefactoring` class
- [ ] `RenameInput` model added to `server.py`
- [ ] `textDocument_rename` tool implemented
- [ ] Preview mode works correctly
- [ ] Apply mode modifies files
- [ ] Unit tests pass for simple and cross-file renaming
- [ ] Integration test passes
- [ ] Error handling works (invalid symbol, file not found)
- [ ] README.md updated with new tool documentation
- [ ] Type hints pass `mypy src/`
- [ ] Linting passes `ruff check src/`
- [ ] Format passes `ruff format src/`

---

## Integration Points

### With Existing Tools
- Shares file validation with other tools (`validate_file()`)
- Can use `lsp_manager` to find workspace root
- Error handling pattern matches existing tools

### With Rope Library
- Creates `.ropeproject` cache in workspace (optional)
- Manages project lifecycle per workspace
- Handles file resources via Rope's abstraction

### With MCP Protocol
- Returns structured text content
- Supports preview mode before destructive changes
- Provides clear success/failure feedback

---

## Error Handling

**Cases to Handle**:
1. **Symbol not found**: "No symbol found at position"
2. **Invalid new name**: "Invalid Python identifier"
3. **Rope error**: "Refactoring failed: {rope_error}"
4. **File write error**: "Error applying changes: {io_error}"
5. **Workspace not found**: "Could not determine workspace root"

**Pattern**:
```python
try:
    # ... refactoring logic
except Exception as e:
    logger.error(f"Error in textDocument_rename: {e}", exc_info=True)
    return [{"type": "text", "text": f"Error renaming symbol: {e}"}]
```

---

## Future Enhancements

1. **LSP-based rename**: Add alternative using `textDocument/rename` LSP method
2. **Undo support**: Track changes for rollback
3. **Conflict detection**: Warn about name collisions
4. **Incremental preview**: Show diffs for each file
5. **Batch rename**: Rename multiple symbols at once

---

## References

- **Rope Documentation**: https://github.com/python-rope/rope
- **Reference Implementation**: `repos/python_lsp_mcp-0.3.0/src/rope_mcp/tools/rename.py`
- **LSP Rename Spec**: https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_rename
- **Python Refactoring Patterns**: https://refactoring.guru/refactoring/python

---

**Ready to Implement**: All prerequisites identified, reference implementation available, clear step-by-step plan provided.
