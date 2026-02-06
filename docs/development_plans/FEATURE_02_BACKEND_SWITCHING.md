# Feature: Runtime Backend Switching (Rope vs Pyright)

**Feature ID**: FEATURE_02  
**Priority**: MEDIUM  
**Complexity**: MEDIUM-HIGH  
**Estimated Time**: 4-6 hours  
**Implementation Status**: ❌ NOT STARTED  
**Reference Implementation**: `repos/python_lsp_mcp-0.3.0/src/rope_mcp/config.py` & `server.py`

---

## Overview

Enable dynamic switching between Rope (fast, local analysis) and Pyright (accurate, type-aware) backends for shared tools like hover, definition, references, completions, and symbols. Users can choose the appropriate backend based on their needs (speed vs accuracy).

**Why Important**: Different use cases require different backends. CI/CD needs speed (Rope), type-heavy projects need accuracy (Pyright). Runtime switching eliminates need for multiple server configurations.

---

## Current State Analysis

### What We Have ✅
- LSP client supporting Pyright/pylsp
- Tools: hover, definition, references, symbols, completion
- Single backend per tool (no switching)
- Configuration loading from TOML

### What We Need ⚠️
- Dual implementation for each shared tool (Rope + Pyright paths)
- Configuration system for backend selection
- Runtime backend switching mechanism
- Rope library integration (same as FEATURE_01)
- Backend status/info tool

### Architecture from Reference 🔍

**From `repos/python_lsp_mcp-0.3.0`**:
```
src/rope_mcp/
├── config.py           # Backend enum, config class, switching logic
├── rope_client.py      # Rope-based analysis
├── lsp/
│   └── client.py       # Pyright LSP client
├── tools/
│   ├── hover.py        # Rope implementation
│   ├── definition.py   # Rope implementation
│   └── ...
└── server.py           # Dual-path dispatch per tool
```

**Key Design**:
- `Backend` enum: `ROPE | PYRIGHT`
- Per-tool backend configuration
- `get_effective_backend(tool, backend?)` resolver
- Tool functions check backend, dispatch to appropriate implementation

---

## Implementation Strategy

### Phase 1: Backend Configuration System

**File**: `src/python_lsp_mcp/config.py`

**Add Backend Enum**:
```python
from enum import Enum

class Backend(str, Enum):
    """Backend options for code analysis."""
    ROPE = "rope"
    PYRIGHT = "pyright"
    PYLSP = "pylsp"  # Existing LSP backend


SHARED_TOOLS = {
    "hover",
    "definition",
    "references",
    "completions",
    "symbols",
}


class BackendConfig:
    """Manages backend selection for tools."""

    def __init__(self, default_backend: Backend = Backend.PYLSP):
        self.default_backend = default_backend
        self._tool_backends: dict[str, Backend] = {}

    def get_backend_for(self, tool: str) -> Backend:
        """Get backend for a specific tool."""
        return self._tool_backends.get(tool, self.default_backend)

    def set_backend(self, backend: Backend, tool: str | None = None):
        """Set backend for a tool or all tools."""
        if tool:
            if tool not in SHARED_TOOLS:
                raise ValueError(f"Unknown tool: {tool}")
            self._tool_backends[tool] = backend
        else:
            # Set default for all shared tools
            self.default_backend = backend
            self._tool_backends.clear()

    def get_all_backends(self) -> dict[str, str]:
        """Get backend mapping for all tools."""
        return {
            tool: self.get_backend_for(tool).value
            for tool in SHARED_TOOLS
        }
```

**Update Config Class**:
```python
@dataclass
class Config:
    """Configuration for Python LSP-MCP server."""

    workspace: str
    lsps: list[LSPConfig]
    eager_init: bool = False
    backend_config: BackendConfig = field(default_factory=BackendConfig)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Config":
        """Create config from dict (TOML file)."""
        # ... existing parsing
        
        # Parse backend config
        backend_str = data.get("default_backend", "pylsp")
        try:
            default_backend = Backend(backend_str.lower())
        except ValueError:
            default_backend = Backend.PYLSP
        
        backend_config = BackendConfig(default_backend)
        
        return cls(
            workspace=workspace,
            lsps=lsps,
            eager_init=eager_init,
            backend_config=backend_config,
        )
```

---

### Phase 2: Rope Client Integration

**File**: `src/python_lsp_mcp/rope_client.py` (NEW)

**Purpose**: Wrapper around Rope for code analysis operations

**Implementation**:
```python
"""Rope client for Python code analysis."""

import os
from pathlib import Path
from typing import Optional

import rope.base.project
from rope.base.resources import File
from rope.contrib.codeassist import code_assist, sorted_proposals
from rope.contrib.findit import find_definition, find_occurrences


class RopeClient:
    """Provides Rope-based code analysis."""

    def __init__(self):
        self._projects: dict[str, rope.base.project.Project] = {}

    def get_project(self, workspace: str) -> rope.base.project.Project:
        """Get or create Rope project."""
        workspace = os.path.abspath(workspace)

        if workspace not in self._projects:
            project = rope.base.project.Project(
                workspace,
                ropefolder=None,  # Disable caching
            )
            self._projects[workspace] = project

        return self._projects[workspace]

    def get_resource(self, project: rope.base.project.Project, file_path: str) -> File:
        """Get Rope file resource."""
        abs_path = os.path.abspath(file_path)
        project_root = project.root.real_path

        if abs_path.startswith(project_root):
            rel_path = os.path.relpath(abs_path, project_root)
        else:
            rel_path = abs_path

        return project.get_file(rel_path)

    def hover(self, file_path: str, line: int, character: int) -> dict:
        """Get hover information using Rope.
        
        Args:
            file_path: Absolute file path
            line: 1-based line number
            character: 1-based character position
        
        Returns:
            Dict with contents or error
        """
        try:
            workspace = str(Path(file_path).parent)
            project = self.get_project(workspace)
            resource = self.get_resource(project, file_path)

            # Read file and calculate offset
            content = resource.read()
            lines = content.split("\n")
            offset = sum(len(l) + 1 for l in lines[:line-1]) + (character - 1)

            # Get documentation
            doc = rope.contrib.codeassist.get_doc(project, content, offset, resource)

            if doc:
                return {"contents": doc}
            else:
                return {"contents": None, "message": "No hover info"}

        except Exception as e:
            return {"error": str(e)}

    def definition(self, file_path: str, line: int, character: int) -> dict:
        """Find definition using Rope."""
        try:
            workspace = str(Path(file_path).parent)
            project = self.get_project(workspace)
            resource = self.get_resource(project, file_path)

            # Calculate offset
            content = resource.read()
            lines = content.split("\n")
            offset = sum(len(l) + 1 for l in lines[:line-1]) + (character - 1)

            # Find definition
            location = find_definition(project, content, offset, resource)

            if location:
                return {
                    "file": location.resource.real_path,
                    "line": location.lineno,
                    "column": location.offset,
                }
            else:
                return {"file": None, "message": "No definition found"}

        except Exception as e:
            return {"error": str(e)}

    def references(self, file_path: str, line: int, character: int) -> dict:
        """Find all references using Rope."""
        try:
            workspace = str(Path(file_path).parent)
            project = self.get_project(workspace)
            resource = self.get_resource(project, file_path)

            # Calculate offset
            content = resource.read()
            lines = content.split("\n")
            offset = sum(len(l) + 1 for l in lines[:line-1]) + (character - 1)

            # Find occurrences
            occurrences = find_occurrences(project, resource, offset)

            refs = []
            for occurrence in occurrences:
                refs.append({
                    "file": occurrence.resource.real_path,
                    "line": occurrence.lineno,
                    "column": occurrence.offset,
                })

            return {"references": refs, "count": len(refs)}

        except Exception as e:
            return {"error": str(e)}

    def completions(self, file_path: str, line: int, character: int) -> dict:
        """Get completions using Rope."""
        try:
            workspace = str(Path(file_path).parent)
            project = self.get_project(workspace)
            resource = self.get_resource(project, file_path)

            # Calculate offset
            content = resource.read()
            lines = content.split("\n")
            offset = sum(len(l) + 1 for l in lines[:line-1]) + (character - 1)

            # Get proposals
            proposals = code_assist(project, content, offset, resource)
            sorted_proposals_list = sorted_proposals(proposals)

            items = []
            for proposal in sorted_proposals_list[:50]:  # Limit to 50
                items.append({
                    "label": proposal.name,
                    "kind": proposal.type,
                    "detail": getattr(proposal, "scope", ""),
                })

            return {"completions": items, "count": len(items)}

        except Exception as e:
            return {"error": str(e)}

    def symbols(self, file_path: str, query: Optional[str] = None) -> dict:
        """Get document symbols using Rope."""
        try:
            workspace = str(Path(file_path).parent)
            project = self.get_project(workspace)
            resource = self.get_resource(project, file_path)

            # Use Rope's AST parsing
            import ast
            content = resource.read()
            tree = ast.parse(content)

            symbols = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    name = node.name
                    if query and query.lower() not in name.lower():
                        continue

                    symbols.append({
                        "name": name,
                        "kind": "function" if isinstance(node, ast.FunctionDef) else "class",
                        "line": node.lineno,
                    })

            return {"symbols": symbols, "count": len(symbols), "file": file_path}

        except Exception as e:
            return {"error": str(e)}

    def close_all(self):
        """Close all projects."""
        for project in self._projects.values():
            project.close()
        self._projects.clear()


# Global instance
_rope_client: Optional[RopeClient] = None


def get_rope_client() -> RopeClient:
    """Get global Rope client instance."""
    global _rope_client
    if _rope_client is None:
        _rope_client = RopeClient()
    return _rope_client
```

---

### Phase 3: Dual-Path Tool Implementation

**File**: `src/python_lsp_mcp/server.py`

**Pattern**: Each shared tool checks backend, dispatches to Rope or LSP

**Example for `textDocument_hover`**:

```python
@server.call_tool()
async def textDocument_hover(arguments: dict[str, Any]) -> list[Any]:
    """Get hover information for a symbol.

    Supports both Rope and Pyright/pylsp backends.
    """
    input_data = HoverInput(**arguments)
    file_path = Path(input_data.file)

    # Validate file
    is_valid, error_msg = validate_file(file_path)
    if not is_valid:
        return [{"type": "text", "text": f"Error: {error_msg}"}]

    # Determine backend
    backend = config.backend_config.get_backend_for("hover")

    try:
        if backend == Backend.ROPE:
            # Rope implementation
            from .rope_client import get_rope_client

            rope_client = get_rope_client()
            result = rope_client.hover(
                str(file_path),
                input_data.line + 1,  # Rope uses 1-based
                input_data.character + 1,
            )

            if "error" in result:
                return [{"type": "text", "text": f"Error: {result['error']}"}]

            contents = result.get("contents")
            if contents:
                return [{"type": "text", "text": f"[Rope] {contents}"}]
            else:
                return [{"type": "text", "text": "No hover information available"}]

        else:  # PYRIGHT or PYLSP (LSP backends)
            # Existing LSP implementation
            lsp_client = lsp_manager.get_lsp_by_extension(file_path)

            if not lsp_client.is_started():
                await lsp_client.start()

            cap_error = await check_capability(lsp_client, "hoverProvider", "hover")
            if cap_error:
                return cap_error

            await lsp_client.notify_document_open(str(file_path.absolute()), "python")

            from lsprotocol.types import HoverParams, Position, TextDocumentIdentifier

            params = HoverParams(
                text_document=TextDocumentIdentifier(uri=file_path.as_uri()),
                position=Position(line=input_data.line, character=input_data.character),
            )

            response = await lsp_client.send_request("textDocument/hover", params)

            if response and response.contents:
                # ... existing formatting logic
                text = format_hover_contents(response.contents)
                return [{"type": "text", "text": f"[{backend.value.upper()}] {text}"}]

            return [{"type": "text", "text": "No hover information available"}]

    except Exception as e:
        logger.error(f"Error in textDocument_hover: {e}", exc_info=True)
        return [{"type": "text", "text": f"Error getting hover information: {e}"}]
```

**Repeat for**: `textDocument_definition`, `textDocument_references`, `textDocument_completion`, `textDocument_documentSymbol`

---

### Phase 4: Backend Switching Tool

**File**: `src/python_lsp_mcp/server.py`

**Add Input Model**:
```python
class SetBackendInput(BaseModel):
    """Input for set_backend tool."""

    backend: str = Field(..., description="Backend to use: 'rope', 'pyright', or 'pylsp'")
    tool: str | None = Field(
        None,
        description="Specific tool to set backend for (hover, definition, etc.). If None, sets default for all."
    )
```

**Add Tool**:
```python
@server.call_tool()
async def set_backend(arguments: dict[str, Any]) -> list[Any]:
    """Switch backend for code analysis tools at runtime.

    Allows choosing between Rope (fast, local) and Pyright/pylsp (accurate, type-aware).
    """
    input_data = SetBackendInput(**arguments)

    try:
        backend_enum = Backend(input_data.backend.lower())
    except ValueError:
        return [{"type": "text", "text": f"Invalid backend: {input_data.backend}. Must be 'rope', 'pyright', or 'pylsp'."}]

    try:
        if input_data.tool:
            config.backend_config.set_backend(backend_enum, input_data.tool)
            return [{"type": "text", "text": f"✓ Backend for '{input_data.tool}' set to '{input_data.backend}'"}]
        else:
            config.backend_config.set_backend(backend_enum)
            return [{"type": "text", "text": f"✓ Default backend set to '{input_data.backend}' for all shared tools"}]

    except ValueError as e:
        return [{"type": "text", "text": f"Error: {e}"}]
    except Exception as e:
        logger.error(f"Error in set_backend: {e}", exc_info=True)
        return [{"type": "text", "text": f"Error setting backend: {e}"}]
```

---

### Phase 5: Backend Status Tool

**File**: `src/python_lsp_mcp/server.py`

```python
@server.call_tool()
async def backend_status(arguments: dict[str, Any]) -> list[Any]:
    """Get current backend configuration and status.

    Shows which backend is active for each tool and backend availability.
    """
    try:
        from .rope_client import get_rope_client

        # Check Rope availability
        rope_available = True
        try:
            get_rope_client()
        except ImportError:
            rope_available = False

        # Get backend mapping
        backends = config.backend_config.get_all_backends()

        result_lines = [
            "Backend Configuration:",
            f"Default: {config.backend_config.default_backend.value}",
            "",
            "Tool Backends:",
        ]

        for tool in SHARED_TOOLS:
            backend = backends[tool]
            result_lines.append(f"  {tool}: {backend}")

        result_lines.extend([
            "",
            "Backend Availability:",
            f"  Rope: {'✓' if rope_available else '✗ (not installed)'}",
            f"  Pyright/pylsp: ✓ (via LSP)",
        ])

        return [{"type": "text", "text": "\n".join(result_lines)}]

    except Exception as e:
        logger.error(f"Error in backend_status: {e}", exc_info=True)
        return [{"type": "text", "text": f"Error getting backend status: {e}"}]
```

---

## Testing Plan

### Integration Tests

**File**: `tests/test_backend_switching.py` (NEW)

```python
"""Tests for backend switching functionality."""

import pytest
from pathlib import Path
from src.python_lsp_mcp.config import Backend, BackendConfig


def test_backend_config():
    """Test backend configuration."""
    config = BackendConfig(default_backend=Backend.ROPE)

    # Test default
    assert config.get_backend_for("hover") == Backend.ROPE

    # Test per-tool override
    config.set_backend(Backend.PYRIGHT, "hover")
    assert config.get_backend_for("hover") == Backend.PYRIGHT
    assert config.get_backend_for("definition") == Backend.ROPE

    # Test set all
    config.set_backend(Backend.PYLSP)
    assert config.get_backend_for("hover") == Backend.PYLSP
    assert config.get_backend_for("definition") == Backend.PYLSP


@pytest.mark.asyncio
async def test_switch_backend_runtime(workspace_dir, sample_python_file):
    """Test switching backend at runtime."""
    config = create_test_config(workspace_dir)
    server, manager = create_server(config)

    try:
        # Start with default backend
        hover_args = {
            "file": str(sample_python_file),
            "line": 5,
            "character": 4,
        }

        result1 = await server.call_tool("textDocument_hover", hover_args)
        assert isinstance(result1, list)

        # Switch to Rope
        switch_args = {"backend": "rope", "tool": "hover"}
        switch_result = await server.call_tool("set_backend", switch_args)
        assert "set to 'rope'" in switch_result[0]["text"].lower()

        # Test hover with Rope backend
        result2 = await server.call_tool("textDocument_hover", hover_args)
        assert isinstance(result2, list)
        # Should include [Rope] prefix
        assert "[rope]" in result2[0]["text"].lower() or "rope" in result2[0]["text"].lower()

    finally:
        await manager.shutdown_all()
```

---

## Verification Checklist

- [ ] Rope dependency added to `pyproject.toml`
- [ ] `Backend` enum and `BackendConfig` class implemented
- [ ] `RopeClient` with hover/definition/references/completions/symbols
- [ ] All 5 shared tools support dual-path dispatch
- [ ] `set_backend` tool implemented and working
- [ ] `backend_status` tool shows current configuration
- [ ] Backend config persists across tool calls
- [ ] Tests pass for both Rope and LSP backends
- [ ] README.md updated with backend switching documentation
- [ ] Configuration file example includes `default_backend`

---

## Configuration Example

**File**: `configs/example.toml`

```toml
workspace = "/path/to/workspace"

# Backend selection: 'rope' (fast) or 'pyright'/'pylsp' (accurate)
default_backend = "rope"

[[lsps]]
id = "pylsp"
command = "pylsp"
extensions = [".py"]
languages = ["python"]
```

---

## Usage Examples

### Switch Default Backend
```python
# Use Rope for all tools (fast, local analysis)
set_backend(backend="rope")

# Use Pyright for all tools (accurate, type-aware)
set_backend(backend="pyright")
```

### Per-Tool Backend
```python
# Fast hover with Rope, accurate definitions with Pyright
set_backend(backend="rope", tool="hover")
set_backend(backend="pyright", tool="definition")
```

### Check Status
```python
backend_status()
# Output:
# Backend Configuration:
# Default: rope
# Tool Backends:
#   hover: rope
#   definition: pyright
#   references: rope
#   ...
```

---

## References

- **Reference Implementation**: `repos/python_lsp_mcp-0.3.0/src/rope_mcp/`
- **Rope Documentation**: https://github.com/python-rope/rope
- **Backend Comparison**: Fast local (Rope) vs accurate type-aware (Pyright)

---

**Ready to Implement**: Complete design documented, reference implementation available, clear testing strategy defined.
