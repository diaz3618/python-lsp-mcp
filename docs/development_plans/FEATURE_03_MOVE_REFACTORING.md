# Feature: Move Refactoring - Relocate Functions/Classes

**Feature ID**: FEATURE_03  
**Priority**: MEDIUM  
**Complexity**: HIGH  
**Estimated Time**: 5-7 hours  
**Implementation Status**: ❌ NOT STARTED  
**Reference Implementation**: `repos/python_lsp_mcp-0.3.0/src/rope_mcp/tools/move.py`

---

## Overview

Enable moving functions, classes, and methods to different modules while automatically updating all imports across the codebase. Uses Rope's move refactoring to ensure safety and correctness.

**Why Useful**: Critical for code organization and refactoring. Allows AI agents to restructure code without manually tracking import changes.

---

## Current State Analysis

### What We Have ✅
- MCP server framework
- Rope integration (from FEATURE_01)
- Refactoring utilities base

### What We Need ⚠️
- Move refactoring logic
- Destination module resolution
- Import update tracking
- Preview mode for non-destructive inspection

### Reference Architecture 🔍

**From `repos/python_lsp_mcp-0.3.0/src/rope_mcp/tools/move.py`**:
```python
from rope.refactor.move import create_move

def do_move(file: str, line: int, column: int, 
            destination: str, resources_only: bool) -> dict:
    # Get project and resource
    # Calculate offset
    # Create move refactoring
    # Get changes
    # Apply if not preview
```

**Key Concepts**:
- **Destination**: Can be module path (`mypackage.utils`) or file path (`utils.py`)
- **Resources**: Affected files (source + all importers)
- **Preview**: Show changes without applying (resources_only=True)

---

## Implementation Strategy

### Phase 1: Extend Refactoring Module

**File**: `src/python_lsp_mcp/refactoring/__init__.py`

**Add to `RopeRefactoring` class**:
```python
    def move_symbol(
        self,
        file_path: str,
        offset: int,
        destination: str,
        workspace: Optional[str] = None,
    ) -> dict:
        """Move a function/class to another module.

        Args:
            file_path: Source file path
            offset: Character offset of symbol
            destination: Target module ('package.module' or 'file.py')
            workspace: Workspace root

        Returns:
            Dict with success, changes, files_modified, or error
        """
        try:
            from rope.refactor.move import create_move

            if workspace is None:
                workspace = str(Path(file_path).parent)

            project = self.get_project(workspace)
            resource = self.get_resource(project, file_path)

            # Parse destination
            if destination.endswith('.py'):
                # File path - convert to module path
                dest_path = Path(destination)
                if dest_path.is_absolute():
                    rel_dest = dest_path.relative_to(workspace)
                else:
                    rel_dest = dest_path
                dest_resource = project.get_file(str(rel_dest))
            else:
                # Module path - find resource
                # Convert 'package.module' to 'package/module.py'
                module_path = destination.replace('.', '/') + '.py'
                dest_resource = project.get_file(module_path)

            # Create move refactoring
            mover = create_move(project, resource, offset)

            # Get changes
            changes = mover.get_changes(dest_resource)

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
                "destination": destination,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "changes": [],
                "files_modified": [],
            }
```

---

### Phase 2: Add MCP Tool

**File**: `src/python_lsp_mcp/server.py`

**Add Input Model** (after `RenameInput`):
```python
class MoveInput(BaseModel):
    """Input for textDocument_move tool."""

    file: str = Field(..., description="Path to source Python file")
    line: int = Field(..., description="Line number of symbol (0-indexed)")
    character: int = Field(..., description="Character position (0-indexed)")
    destination: str = Field(
        ...,
        description="Destination module path (e.g., 'mypackage.utils') or file path ('utils.py')"
    )
    preview: bool = Field(
        False,
        description="If True, show changes without applying"
    )
    workspace: str | None = Field(
        None,
        description="Workspace root (auto-detected if not provided)"
    )
```

**Add Tool Handler**:
```python
    # Tool: textDocument_move
    @server.call_tool()
    async def textDocument_move(arguments: dict[str, Any]) -> list[Any]:
        """Move a function or class to another module.

        Automatically updates all imports across the workspace.
        Uses Rope refactoring for safety and correctness.
        """
        input_data = MoveInput(**arguments)
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

            # Perform move refactoring
            refactoring = get_refactoring()
            result = refactoring.move_symbol(
                file_path=str(file_path),
                offset=offset,
                destination=input_data.destination,
                workspace=input_data.workspace,
            )

            if not result["success"]:
                return [{"type": "text", "text": f"Error: {result['error']}"}]

            # Format preview or apply changes
            if input_data.preview:
                # Show preview
                result_lines = [
                    f"Move Preview: {len(result['files_modified'])} file(s) would be modified",
                    f"Destination: {result['destination']}",
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
                    f"✓ Moved symbol to '{input_data.destination}'",
                    f"✓ Modified {len(apply_result['files_written'])} file(s):",
                    ""
                ]

                for file in apply_result["files_written"]:
                    file_name = Path(file).name
                    result_lines.append(f"  - {file_name}")

                return [{"type": "text", "text": "\n".join(result_lines)}]

        except Exception as e:
            logger.error(f"Error in textDocument_move: {e}", exc_info=True)
            return [{"type": "text", "text": f"Error moving symbol: {e}"}]
```

---

### Phase 3: Integration Testing

**File**: `tests/test_refactoring.py`

**Add Test**:
```python
def test_move_function_to_new_module(tmp_path):
    """Test moving a function to a new module."""
    # Create source module
    source = tmp_path / "source.py"
    source.write_text(
        "def utility():\n"
        "    return 42\n"
        "\n"
        "def another():\n"
        "    return utility()\n"
    )

    # Create destination module
    dest = tmp_path / "utils.py"
    dest.write_text("# Utils module\n")

    # Create file that imports from source
    main = tmp_path / "main.py"
    main.write_text(
        "from source import utility, another\n"
        "\n"
        "result = utility()\n"
    )

    # Calculate offset for 'utility' function (line 0, char 4)
    offset = 4

    # Perform move
    refactoring = get_refactoring()
    result = refactoring.move_symbol(
        file_path=str(source),
        offset=offset,
        destination="utils.py",
        workspace=str(tmp_path),
    )

    # Verify
    assert result["success"]
    assert len(result["files_modified"]) >= 2  # source.py and main.py

    # Apply changes
    apply_result = refactoring.apply_changes(result)
    assert apply_result["success"]

    # Verify source no longer has utility
    source_content = source.read_text()
    assert "def utility()" not in source_content
    assert "def another()" in source_content  # another() should remain

    # Verify destination has utility
    dest_content = dest.read_text()
    assert "def utility()" in dest_content

    # Verify imports were updated in main
    main_content = main.read_text()
    assert "from utils import utility" in main_content
    assert "from source import another" in main_content
```

---

## Usage Examples

### Move Function to Existing Module
```python
# Move 'helper_function' from myapp/views.py to myapp/utils.py
textDocument_move(
    file="/path/to/myapp/views.py",
    line=45,
    character=4,
    destination="myapp.utils",  # or "myapp/utils.py"
    preview=False
)

# Result: Function moved, all imports updated across codebase
```

### Preview Move
```python
# Preview moving a class
textDocument_move(
    file="/path/to/models.py",
    line=10,
    character=6,
    destination="models/user.py",
    preview=True
)

# Output:
# Move Preview: 5 file(s) would be modified
# Destination: models/user.py
#
# 📄 models.py (source)
# 📄 views.py (imports)
# 📄 serializers.py (imports)
# ...
```

---

## Error Handling

**Common Errors**:
1. **Symbol not found**: "No movable symbol at position"
2. **Destination not found**: "Destination module not found: {path}"
3. **Circular imports**: "Moving would create circular import"
4. **Name collision**: "Symbol with same name exists in destination"

**Pattern**:
```python
try:
    # ... move logic
except rope.base.exceptions.RefactoringError as e:
    return {"success": False, "error": f"Refactoring error: {e}"}
except Exception as e:
    logger.error(f"Error in move: {e}", exc_info=True)
    return {"success": False, "error": str(e)}
```

---

## Verification Checklist

- [ ] `move_symbol()` method added to `RopeRefactoring`
- [ ] Destination module resolution works (both path formats)
- [ ] `MoveInput` model defined
- [ ] `textDocument_move` tool implemented
- [ ] Preview mode works correctly
- [ ] Apply mode moves symbol and updates imports
- [ ] Unit tests pass for single-file and cross-file moves
- [ ] Integration test verifies end-to-end functionality
- [ ] Error handling covers all edge cases
- [ ] README.md updated with move tool documentation

---

## Future Enhancements

1. **Multi-symbol move**: Move multiple functions/classes at once
2. **Smart destination**: Suggest best destination module based on usage
3. **Dependency graph**: Show affected files before moving
4. **Rollback**: Undo move operation

---

## References

- **Rope Move Docs**: https://rope.readthedocs.io/en/latest/overview.html#move
- **Reference Implementation**: `repos/python_lsp_mcp-0.3.0/src/rope_mcp/tools/move.py`

---

**Ready to Implement**: Build on FEATURE_01 refactoring foundation, clear implementation path defined.
