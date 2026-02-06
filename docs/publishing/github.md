# Publishing to GitHub

Distribute Python LSP-MCP via GitHub releases and git installation.

## Prerequisites

- GitHub account
- Git installed and configured
- Repository created on GitHub

## Initial Setup

### 1. Create GitHub Repository

```bash
# On GitHub, create new repository: python-lsp-mcp

# Initialize locally (if not done)
cd /path/to/python-lsp-mcp
git init
git add .
git commit -m "Initial commit"

# Add remote and push
git remote add origin https://github.com/yourusername/python-lsp-mcp.git
git branch -M main
git push -u origin main
```

### 2. Prepare Repository

**Essential Files**:
- `README.md`: Project overview, installation, usage
- `LICENSE.txt`: Software license
- `pyproject.toml`: Package metadata
- `.gitignore`: Ignore patterns
- `CHANGELOG.md`: Version history

**Create CHANGELOG.md**:

```bash
cat > CHANGELOG.md << 'EOF'
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-02-05

### Added
- Initial release
- MCP server for Python LSP integration
- Support for pylsp and pyright
- 6 MCP tools: hover, definition, references, symbols, completion, lsp_info
- Configuration via TOML files
- Multi-LSP support

[Unreleased]: https://github.com/yourusername/python-lsp-mcp/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/python-lsp-mcp/releases/tag/v0.1.0
EOF
```

## Version Management

### Semantic Versioning

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0): Incompatible API changes
- **MINOR** (0.1.0): New features, backwards compatible
- **PATCH** (0.0.1): Bug fixes, backwards compatible

### Update Version

Edit `pyproject.toml`:

```toml
[project]
name = "python-lsp-mcp"
version = "0.1.0"  # Update this
```

Or use dynamic versioning with setuptools-scm:

```toml
[build-system]
requires = ["setuptools>=45", "setuptools-scm[toml]>=6.2"]

[tool.setuptools_scm]
write_to = "src/python_lsp_mcp/_version.py"
```

## Creating Releases

### Method 1: GitHub Web Interface

1. Go to repository on GitHub
2. Click "Releases" → "Create a new release"
3. Click "Choose a tag" → Type new version (e.g., `v0.1.0`)
4. Title: "Release 0.1.0"
5. Description: Copy from CHANGELOG.md
6. Click "Publish release"

### Method 2: Git Command Line

```bash
# 1. Update version in pyproject.toml
# 2. Update CHANGELOG.md
# 3. Commit changes
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 0.1.0"

# 4. Create and push tag
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin main
git push origin v0.1.0
```

### Method 3: GitHub CLI

```bash
# Install GitHub CLI
# macOS: brew install gh
# Linux: Follow instructions at https://cli.github.com/

# Login
gh auth login

# Create release
gh release create v0.1.0 \
  --title "Release 0.1.0" \
  --notes "$(cat CHANGELOG.md | sed -n '/## \[0.1.0\]/,/## \[/p' | head -n -1)"
```

## Installation from GitHub

### Users Can Install Directly

```bash
# Latest from main branch
pip install git+https://github.com/yourusername/python-lsp-mcp.git

# Specific tag/version
pip install git+https://github.com/yourusername/python-lsp-mcp.git@v0.1.0

# Specific branch
pip install git+https://github.com/yourusername/python-lsp-mcp.git@develop

# With uv
uv pip install git+https://github.com/yourusername/python-lsp-mcp.git
```

### Development Installation

```bash
# Clone and install editable
git clone https://github.com/yourusername/python-lsp-mcp.git
cd python-lsp-mcp
pip install -e .
```

## Distribution Files

### Create Distribution Archives

```bash
# Build source and wheel distributions
python -m build

# Output in dist/:
# - python_lsp_mcp-0.1.0.tar.gz (source)
# - python_lsp_mcp-0.1.0-py3-none-any.whl (wheel)
```

### Attach to GitHub Release

```bash
# Manual upload via web interface:
# 1. Go to release
# 2. Edit release
# 3. Drag and drop dist/*.tar.gz and dist/*.whl

# Or via GitHub CLI
gh release upload v0.1.0 dist/*
```

## Automated Releases with GitHub Actions

### Create Workflow File

`.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'  # Trigger on version tags

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write  # For creating releases
      
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install build dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build
      
      - name: Build distributions
        run: python -m build
      
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: dist/*
          body: |
            See [CHANGELOG.md](https://github.com/${{ github.repository }}/blob/main/CHANGELOG.md) for details.
          draft: false
          prerelease: false
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Usage

```bash
# Create and push tag
git tag -a v0.1.0 -m "Release 0.1.0"
git push origin v0.1.0

# GitHub Actions automatically:
# 1. Builds distributions
# 2. Creates GitHub release
# 3. Uploads distribution files
```

## README Badge

Add installation badge to README.md:

```markdown
## Installation

[![GitHub release](https://img.shields.io/github/v/release/yourusername/python-lsp-mcp)](https://github.com/yourusername/python-lsp-mcp/releases)

```bash
pip install git+https://github.com/yourusername/python-lsp-mcp.git
```
```

## Documentation Hosting

### GitHub Pages

Host documentation on GitHub Pages:

```bash
# Create docs branch
git checkout --orphan gh-pages
git rm -rf .

# Add documentation
echo "# Python LSP-MCP Documentation" > index.md
git add index.md
git commit -m "Initial documentation"
git push origin gh-pages

# Enable in GitHub Settings:
# Settings → Pages → Source: gh-pages branch
```

### README Links

Link to setup documentation in README:

```markdown
## Setup Guides

- [Claude Desktop](docs/setup/claude-desktop.md)
- [VS Code](docs/setup/vscode.md)
- [Cursor](docs/setup/cursor.md)
- [Gemini](docs/setup/gemini.md)
- [Codex](docs/setup/codex.md)
- [Generic](docs/setup/generic.md)
```

## Release Checklist

Before each release:

- [ ] Update version in `pyproject.toml`
- [ ] Update `CHANGELOG.md` with changes
- [ ] Run tests: `pytest tests/`
- [ ] Update documentation if needed
- [ ] Commit version bump
- [ ] Create and push git tag
- [ ] Build distributions: `python -m build`
- [ ] Create GitHub release
- [ ] Upload distribution files
- [ ] Verify installation works
- [ ] Announce release (if applicable)

## Repository Settings

### Branch Protection

Protect main branch:

1. Go to Settings → Branches
2. Add rule for `main`
3. Enable:
   - Require pull request reviews
   - Require status checks to pass
   - Require branches to be up to date

### Topics

Add repository topics for discoverability:

```
mcp
model-context-protocol
lsp
language-server-protocol
python
code-analysis
ai-tools
```

## Advanced: Pre-release Versions

### Alpha/Beta Releases

```bash
# Alpha version
git tag -a v0.1.0-alpha.1 -m "Alpha release"
git push origin v0.1.0-alpha.1

# Beta version
git tag -a v0.1.0-beta.1 -m "Beta release"
git push origin v0.1.0-beta.1

# Mark as pre-release on GitHub
gh release create v0.1.0-alpha.1 --prerelease
```

Users install with:

```bash
pip install git+https://github.com/yourusername/python-lsp-mcp.git@v0.1.0-alpha.1
```

## Maintenance

### Security Advisories

Report security issues:

1. Go to Security → Advisories
2. Click "New draft security advisory"
3. Fill in details
4. Publish when fixed

### Issue Templates

Create `.github/ISSUE_TEMPLATE/bug_report.md`:

```markdown
---
name: Bug Report
about: Report a bug
title: "[BUG] "
labels: bug
---

**Describe the bug**
A clear description of the bug.

**To Reproduce**
Steps to reproduce:
1. Install python-lsp-mcp
2. Run command '...'
3. See error

**Expected behavior**
What should happen.

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.12]
- LSP server: [e.g., pylsp 1.14.0]

**Additional context**
Any other relevant information.
```

## Next Steps

- Check [PyPI Publishing](./pypi.md) for package registry distribution
- Review [Distribution Guide](./distribution.md) for alternative methods
- Set up CI/CD with GitHub Actions

## Support

- GitHub Docs: https://docs.github.com
- Semantic Versioning: https://semver.org
- Keep a Changelog: https://keepachangelog.com
