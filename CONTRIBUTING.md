# Contributing to Python LSP-MCP

Thank you for your interest in contributing to Python LSP-MCP.

## How to Contribute

### 1. Fork the Repository

Fork the repository to your GitHub account:

```bash
# Click the "Fork" button on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/python-lsp-mcp.git
cd python-lsp-mcp
```

### 2. Set Up Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Or with uv
uv pip install -e ".[dev]"
```

### 3. Create a Feature Branch

```bash
git checkout -b feature/amazing-feature
```

Use descriptive branch names:
- `feature/` for new features
- `fix/` for bug fixes
- `docs/` for documentation updates
- `refactor/` for code refactoring
- `test/` for test improvements

### 4. Make Your Changes

Write clean, well-documented code following the project's style:

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write comprehensive docstrings
- Keep functions focused and single-purpose

### 5. Add Tests

Ensure your changes are covered by tests:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_your_feature.py -v

# Run with coverage
pytest tests/ --cov=python_lsp_mcp --cov-report=html
```

All tests must pass before submitting a pull request.

### 6. Format and Lint Your Code

```bash
# Format code with ruff
ruff format src/ tests/

# Lint code
ruff check src/ tests/

# Type check
mypy src/

# Or format with black (alternative)
black src/ tests/
```

Ensure no linting or type errors remain.

### 7. Commit Your Changes

Write clear, descriptive commit messages following conventional commits:

```bash
git commit -m "feat: add support for multiple workspaces"
git commit -m "fix: resolve race condition in LSP client startup"
git commit -m "docs: update installation instructions"
git commit -m "test: add integration tests for pyright"
```

**Commit message format:**
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for test additions/changes
- `refactor:` for code refactoring
- `chore:` for maintenance tasks

### 8. Push to Your Fork

```bash
git push origin feature/amazing-feature
```

### 9. Open a Pull Request

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your fork and branch
4. Fill out the PR template with:
   - Clear description of changes
   - Related issue numbers (if applicable)
   - Testing performed
   - Screenshots (if UI changes)

## Code Quality Standards

### Testing Requirements

- All new features must include tests
- Bug fixes should include regression tests
- Maintain or improve code coverage
- Tests must pass on all supported Python versions (3.12+)

### Code Style

- **Line length**: 100 characters maximum
- **Type hints**: Required for all public functions
- **Docstrings**: Google or NumPy style for all public APIs
- **Imports**: Organized and sorted (use `ruff` or `isort`)

### Documentation

- Update README.md if adding features or changing usage
- Add docstrings to all public functions and classes
- Update ARCHITECTURE.md for significant architectural changes
- Include code examples for new features

## Development Workflow

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_lsp_client.py -v

# Integration tests (requires pylsp)
pytest tests/test_integration.py -v

# With coverage report
pytest tests/ --cov=python_lsp_mcp --cov-report=html
open htmlcov/index.html
```

### Code Quality Checks

```bash
# Run all checks
ruff check src/ tests/
ruff format src/ tests/
mypy src/
pytest tests/

# Quick pre-commit check
make check  # if Makefile exists
```

### Building Distribution

```bash
# Build source and wheel distributions
python -m build

# Validate distributions
twine check dist/*
```

## Project Structure

```
python-lsp-mcp/
├── src/python_lsp_mcp/    # Main source code
│   ├── __init__.py
│   ├── __main__.py         # CLI entry point
│   ├── config.py           # Configuration loading
│   ├── lsp_client.py       # LSP client wrapper
│   ├── lsp_manager.py      # Multi-LSP management
│   ├── server.py           # MCP server implementation
│   └── tools/              # MCP tool definitions
├── tests/                  # Test suite
│   ├── test_config.py
│   ├── test_lsp_client.py
│   ├── test_lsp_manager.py
│   └── test_integration.py
├── configs/                # Example configurations
├── docs/                   # Documentation
└── pyproject.toml          # Project metadata
```

## Reporting Issues

### Bug Reports

When reporting bugs, include:

1. **Python version**: `python --version`
2. **Package version**: `pip show python-lsp-mcp`
3. **LSP server**: Which LSP server (pylsp, pyright, etc.)
4. **Minimal reproduction**: Code to reproduce the issue
5. **Expected behavior**: What should happen
6. **Actual behavior**: What actually happens
7. **Error messages**: Full traceback if applicable
8. **Configuration**: Your TOML config file (sanitized)

### Feature Requests

For feature requests, describe:

1. **Use case**: Why is this feature needed?
2. **Proposed solution**: How should it work?
3. **Alternatives**: What alternatives have you considered?
4. **Additional context**: Any other relevant information

## Review Process

### What to Expect

1. **Initial review**: Within 1-3 days (if work and family permits)
2. **Feedback**: Suggestions for improvements
3. **Iteration**: Make requested changes
4. **Approval**: Once all checks pass and code is reviewed
5. **Merge**: Your contribution is merged!

### Review Criteria

Pull requests are evaluated on:

- **Code quality**: Clean, readable, well-documented
- **Tests**: Comprehensive test coverage
- **Performance**: No significant performance regressions
- **Compatibility**: Works with supported Python versions
- **Documentation**: Clear and complete
- **Style**: Follows project conventions

### Getting Help

- **Questions**: Use [GitHub Discussions](https://github.com/diaz3618/python-lsp-mcp/discussions)
- **Bugs**: Open an [Issue](https://github.com/diaz3618/python-lsp-mcp/issues)

## License

By contributing to Python LSP-MCP, you agree that your contributions will be licensed under the MIT License.
