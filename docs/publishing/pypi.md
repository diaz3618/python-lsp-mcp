# Publishing to PyPI

Distribute Python LSP-MCP via the Python Package Index (PyPI) for easy `pip install`.

## Overview

PyPI allows users to install with:
```bash
pip install python-lsp-mcp
```

## Prerequisites

- PyPI account: https://pypi.org/account/register/
- TestPyPI account (recommended): https://test.pypi.org/account/register/
- API tokens for authentication
- Package properly configured in `pyproject.toml`

## Initial Setup

### 1. Create PyPI Accounts

```bash
# Register on PyPI
# Visit: https://pypi.org/account/register/

# Register on TestPyPI (for testing)
# Visit: https://test.pypi.org/account/register/
```

### 2. Generate API Tokens

**PyPI**:
1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Name: "python-lsp-mcp-upload"
4. Scope: "Entire account" (or specific project after first upload)
5. Copy token (starts with `pypi-`)

**TestPyPI**:
1. Go to https://test.pypi.org/manage/account/token/
2. Follow same steps
3. Copy token

### 3. Configure pip

Create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-testpypi-token-here
```

**Security**: Keep this file private!

```bash
chmod 600 ~/.pypirc
```

## Package Configuration

### Verify pyproject.toml

Ensure complete metadata:

```toml
[project]
name = "python-lsp-mcp"
version = "0.1.0"
description = "MCP server for Python LSP integration"
readme = "README.md"
requires-python = ">=3.12"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
keywords = ["mcp", "lsp", "language-server", "model-context-protocol"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
]
dependencies = [
    "mcp>=1.0.0",
    "pygls>=2.0.0",
    "lsprotocol>=2025.0.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]

[project.urls]
Homepage = "https://github.com/yourusername/python-lsp-mcp"
Documentation = "https://github.com/yourusername/python-lsp-mcp/blob/main/README.md"
Repository = "https://github.com/yourusername/python-lsp-mcp"
Issues = "https://github.com/yourusername/python-lsp-mcp/issues"

[project.scripts]
python-lsp-mcp = "python_lsp_mcp.__main__:main"

[build-system]
requires = ["setuptools>=45", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"
```

### Validate Long Description

```bash
# Install twine
pip install twine

# Check README renders properly
python -m build
twine check dist/*
```

## Building Distribution

### Install Build Tools

```bash
pip install build twine
```

### Build Distributions

```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info

# Build source distribution and wheel
python -m build

# Output:
# dist/python_lsp_mcp-0.1.0.tar.gz
# dist/python_lsp_mcp-0.1.0-py3-none-any.whl
```

### Verify Build

```bash
# Check distributions
twine check dist/*

# Should output:
# Checking dist/python_lsp_mcp-0.1.0.tar.gz: PASSED
# Checking dist/python_lsp_mcp-0.1.0-py3-none-any.whl: PASSED
```

## Publishing

### Method 1: Test on TestPyPI First (Recommended)

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ --no-deps python-lsp-mcp

# Verify it works
python-lsp-mcp --help

# If successful, proceed to PyPI
```

### Method 2: Direct Upload to PyPI

```bash
# Upload to PyPI
python -m twine upload dist/*

# Output:
# Uploading distributions to https://upload.pypi.org/legacy/
# Uploading python_lsp_mcp-0.1.0.tar.gz
# 100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 
# Uploading python_lsp_mcp-0.1.0-py3-none-any.whl
# 100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# View on PyPI: https://pypi.org/project/python-lsp-mcp/
```

### Verify Installation

```bash
# Install from PyPI
pip install python-lsp-mcp

# Test
python-lsp-mcp --help
```

## Automated Publishing with GitHub Actions

### Create Workflow

`.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # For trusted publishing
      
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine
      
      - name: Build package
        run: python -m build
      
      - name: Check build
        run: twine check dist/*
      
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```

### Configure Secrets

1. Go to GitHub repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `PYPI_API_TOKEN`
4. Value: Your PyPI API token
5. Click "Add secret"

### Usage

```bash
# Create GitHub release (triggers workflow)
gh release create v0.1.0 --title "Release 0.1.0"

# Workflow automatically:
# 1. Builds distributions
# 2. Uploads to PyPI
```

## Trusted Publishers (Recommended)

More secure alternative to API tokens:

### Configure on PyPI

1. Go to https://pypi.org/manage/account/publishing/
2. Click "Add a new pending publisher"
3. Fill in:
   - PyPI Project Name: `python-lsp-mcp`
   - Owner: `yourusername`
   - Repository: `python-lsp-mcp`
   - Workflow: `publish.yml`
   - Environment: (leave blank)
4. Click "Add"

### Update Workflow

`.github/workflows/publish.yml`:

```yaml
- name: Publish to PyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  # No password needed with trusted publishing!
```

## Version Management

### Updating Versions

```bash
# 1. Update version in pyproject.toml
# From: version = "0.1.0"
# To:   version = "0.2.0"

# 2. Rebuild
rm -rf dist/
python -m build

# 3. Upload new version
twine upload dist/*
```

### Version Scheme

Follow [PEP 440](https://peps.python.org/pep-0440/):

- **Release**: `0.1.0`, `1.0.0`, `2.3.5`
- **Pre-release**: `0.1.0a1`, `0.1.0b2`, `0.1.0rc1`
- **Post-release**: `0.1.0.post1`
- **Dev release**: `0.1.0.dev1`

### Dynamic Versioning

Use `setuptools-scm` for git-based versioning:

```toml
[build-system]
requires = ["setuptools>=45", "setuptools-scm[toml]>=6.2"]

[tool.setuptools_scm]
write_to = "src/python_lsp_mcp/_version.py"
```

Version determined from git tags:

```bash
git tag v0.1.0
python -m build  # Uses v0.1.0 from tag
```

## Updating Existing Package

### Release New Version

```bash
# 1. Make changes, commit
git add .
git commit -m "feat: add new feature"

# 2. Update version
# Edit pyproject.toml: version = "0.2.0"

# 3. Create changelog entry
# Edit CHANGELOG.md

# 4. Commit version bump
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 0.2.0"

# 5. Tag and push
git tag v0.2.0
git push origin main --tags

# 6. Build and upload
rm -rf dist/
python -m build
twine check dist/*
twine upload dist/*
```

## Package Maintenance

### Yanking Releases

If a release has critical bugs:

```bash
# Yank from PyPI (still installable with specific version)
# Via web interface: pypi.org → Your project → Manage → Yank

# Or via API (requires package owner permissions)
```

### Deleting Releases

**Warning**: Cannot delete from PyPI, only yank!

- Yanked versions: Can still be installed with exact version
- Cannot upload same version again
- Use yanking for broken releases

## Best Practices

### Pre-release Checklist

- [ ] All tests passing: `pytest tests/`
- [ ] Code formatted: `black src/`
- [ ] Linting clean: `ruff check src/`
- [ ] Type checking: `mypy src/`
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in pyproject.toml
- [ ] Build succeeds: `python -m build`
- [ ] Distributions valid: `twine check dist/*`
- [ ] Test on TestPyPI first

### Post-release Checklist

- [ ] Verify package on PyPI: https://pypi.org/project/python-lsp-mcp/
- [ ] Test installation: `pip install python-lsp-mcp`
- [ ] Create GitHub release with same version
- [ ] Announce release (if applicable)
- [ ] Update documentation links

### Security

- **Never commit** `.pypirc` or API tokens
- Use **environment variables** for CI/CD
- **Rotate tokens** periodically
- Use **trusted publishing** when possible
- Enable **2FA** on PyPI account

## Troubleshooting

### Upload Fails

**Error**: `The user '...' isn't allowed to upload`

**Solution**: Check package name not already taken, or request access

---

**Error**: `File already exists`

**Solution**: Cannot re-upload same version. Bump version number.

---

**Error**: `Invalid distribution file`

**Solution**: Run `twine check dist/*` and fix issues

### Package Not Installing

**Error**: Dependency resolution fails

**Solution**: Check `requires-python` and `dependencies` in pyproject.toml

---

**Error**: Module not found after install

**Solution**: Verify package structure:
```
src/
  python_lsp_mcp/
    __init__.py
    (other files)
```

### README Not Rendering

**Solution**: 
```bash
# Validate markdown
python -m build
twine check dist/*

# Fix rendering issues in README.md
# Re-build and re-upload
```

## Monitoring

### PyPI Statistics

View download stats:
- PyPI project page: https://pypi.org/project/python-lsp-mcp/
- PyPI Stats: https://pypistats.org/packages/python-lsp-mcp

### Badge for README

```markdown
[![PyPI version](https://badge.fury.io/py/python-lsp-mcp.svg)](https://pypi.org/project/python-lsp-mcp/)
[![Downloads](https://pepy.tech/badge/python-lsp-mcp)](https://pepy.tech/project/python-lsp-mcp)
```

## Next Steps

- Read [GitHub Publishing](./github.md) for git-based distribution
- Check [Distribution Guide](./distribution.md) for additional methods
- Set up continuous deployment with GitHub Actions

## Support

- PyPI Help: https://pypi.org/help/
- Packaging Guide: https://packaging.python.org/
- PEP 517/518: https://peps.python.org/pep-0517/
