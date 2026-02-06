# Python LSP-MCP

A Model Context Protocol (MCP) server that bridges LLMs with Language Server Protocol (LSP) servers for Python code analysis.

[![Tests](https://img.shields.io/badge/tests-28%20passed-brightgreen)](tests/)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE.txt)

## Features

- **Multi-LSP Support**: Connect to multiple LSP servers (pylsp, pyright, etc.)
- **Language-Aware Routing**: Automatic routing by file extension or language ID
- **MCP Tools**: Expose LSP methods as MCP tools for AI agents
- **Async Architecture**: Built on asyncio for efficient I/O
- **Comprehensive Testing**: 28 tests covering all functionality

## Available Tools

- `textDocument_hover`: Get type information and documentation for code elements
- `textDocument_definition`: Navigate to symbol definitions
- `textDocument_references`: Find all references to a symbol
- `textDocument_documentSymbol`: Get document structure (classes, functions, variables)
- `textDocument_completion`: Get code completion suggestions
- `lsp_info`: Query LSP server status and capabilities

## Installation

### From PyPI (Coming Soon)

```bash
pip install python-lsp-mcp
# or with uv
uv pip install python-lsp-mcp
```

### From GitHub

```bash
# Latest version
pip install git+https://github.com/yourusername/python-lsp-mcp.git

# Specific version
pip install git+https://github.com/yourusername/python-lsp-mcp.git@v0.1.0
```

### From Source

```bash
git clone https://github.com/yourusername/python-lsp-mcp.git
cd python-lsp-mcp
pip install -e .
```

### Install LSP Server

```bash
# pylsp (recommended)
pip install python-lsp-server

# or pyright
npm install -g pyright
```

## Quick Start

### With Configuration File

```bash
python-lsp-mcp --config configs/example.toml
```

### With Inline Command

```bash
python-lsp-mcp --lsp-command "pylsp" --workspace /path/to/project
```

### Configuration File Format

```toml
# configs/example.toml
workspace = "/path/to/your/python/project"

[[lsps]]
id = "pylsp"
command = "pylsp"
args = []
extensions = [".py", ".pyi"]
languages = ["python"]
```

## Setup for AI Clients

Configure Python LSP-MCP for your preferred AI assistant:

- MCP client (Claude Desktop, VS Code, Cursor, etc.)

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests (28 tests, 100% passing)
pytest tests/ -v

# Format code
black src/

# Lint
ruff check src/

# Type check
mypy src/
```

## Testing

Comprehensive test suite with 100% pass rate:

```Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Ensure all tests pass: `pytest tests/`
5. Format code: `black src/ tests/`
6. Commit: `git commit -m "feat: add amazing feature"`
7. Push: `git push origin feature/amazing-feature`
8. Open a pull request

## License

MIT License - see [LICENSE.txt](LICENSE.txt) for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/python-lsp-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/python-lsp-mcp/discussions)
- **MCP Documentation**: [Model Context Protocol](https://modelcontextprotocol.io)
- **LSP Specification**: [Language Server Protocol](https://microsoft.github.io/language-server-protocol/)

# Run with coverage
pytest tests/ --cov=python_lsp_mcp --cov-report=html

# Run specific test file
pytest tests/test_lsp_client.py -v

# Run integration tests (requires pylsp)
pytest tests/test_integration.py -v
```

**Test Coverage**:
- Configuration loading (6 tests)
- LSP client lifecycle (6 tests)
- LSP manager routing (10 tests)
- End-to-end integration (5 tests)
- Legacy compatibility (1 test)

Total: **28 tests, all passing** ✅rn how to distribute Python LSP-MCP:

- **[GitHub Publishing](docs/publishing/github.md)** - Releases, tags, git installation
- **[PyPI Publishing](docs/publishing/pypi.md)** - Python Package Index distribution
- **[Alternative Methods](docs/publishing/distribution.md)** - Docker, Conda, Homebrew, and more

## Requirements

- Python 3.12+
- An LSP server (e.g., pylsp, pyright)

## Development

```bash
# Run tests
pytest tests/

# Format code
black src/

# Lint
ruff check src/

# Type check
mypy src/
```

## Architecture

- **config.py**: Configuration loading with Pydantic models
- **lsp_client.py**: LSP client wrapper using pygls
- **lsp_manager.py**: Multi-LSP routing and management
- **server.py**: MCP server with tool registration
- **__main__.py**: CLI entry point

## License

See LICENSE.txt for details.
