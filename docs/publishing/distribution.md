# Alternative Distribution Methods

Additional ways to distribute and install Python LSP-MCP.

## Overview

Beyond GitHub and PyPI, several distribution methods exist:

1. **uv** - Fast Python package installer
2. **Docker** - Containerized distribution
3. **Conda** - Cross-platform package manager
4. **Homebrew** - macOS/Linux package manager
5. **Nix** - Reproducible package manager
6. **Snap** - Universal Linux packages
7. **Binary Executables** - Standalone binaries

## 1. uv Distribution

### Using uv for Installation

Users can install with uv:

```bash
# From PyPI
uv pip install python-lsp-mcp

# From GitHub
uv pip install git+https://github.com/yourusername/python-lsp-mcp.git

# From local source
cd python-lsp-mcp
uv pip install -e .
```

### uv.lock File

Provide lock file for reproducible installs:

```bash
# Generate lock file
uv lock

# Users install with exact versions
uv sync
```

### uv Tool Installation

Install as a tool (isolated environment):

```bash
# Install as tool
uv tool install python-lsp-mcp

# Run directly
python-lsp-mcp --help

# Update
uv tool update python-lsp-mcp
```

## 2. Docker Distribution

### Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install python-lsp-mcp
COPY . /app
WORKDIR /app
RUN pip install --no-cache-dir .

# Install LSP server
RUN pip install --no-cache-dir python-lsp-server

# Default workspace
VOLUME ["/workspace"]
WORKDIR /workspace

# Entry point
ENTRYPOINT ["python-lsp-mcp"]
CMD ["--lsp-command", "pylsp", "--workspace", "/workspace"]
```

### Build and Publish

```bash
# Build image
docker build -t yourusername/python-lsp-mcp:latest .
docker build -t yourusername/python-lsp-mcp:0.1.0 .

# Test locally
docker run -it --rm \
  -v /path/to/workspace:/workspace \
  yourusername/python-lsp-mcp:latest

# Push to Docker Hub
docker login
docker push yourusername/python-lsp-mcp:latest
docker push yourusername/python-lsp-mcp:0.1.0
```

### Users Install from Docker

```bash
# Pull image
docker pull yourusername/python-lsp-mcp:latest

# Run
docker run -it --rm \
  -v $(pwd):/workspace \
  yourusername/python-lsp-mcp:latest
```

### Docker Compose

Provide `docker-compose.yml`:

```yaml
version: '3.8'

services:
  python-lsp-mcp:
    image: yourusername/python-lsp-mcp:latest
    volumes:
      - ./:/workspace
    stdin_open: true
    tty: true
    command: ["--lsp-command", "pylsp", "--workspace", "/workspace"]
```

Usage:

```bash
docker-compose run python-lsp-mcp
```

## 3. Conda Distribution

### Create conda-forge Recipe

`meta.yaml`:

```yaml
{% set name = "python-lsp-mcp" %}
{% set version = "0.1.0" %}

package:
  name: {{ name|lower }}
  version: {{ version }}

source:
  url: https://pypi.io/packages/source/{{ name[0] }}/{{ name }}/{{ name }}-{{ version }}.tar.gz
  sha256: <checksum>

build:
  number: 0
  script: "{{ PYTHON }} -m pip install . -vv"
  entry_points:
    - python-lsp-mcp = python_lsp_mcp.__main__:main

requirements:
  host:
    - python >=3.12
    - pip
  run:
    - python >=3.12
    - mcp >=1.0.0
    - pygls >=2.0.0
    - lsprotocol >=2025.0.0
    - pydantic >=2.0.0

test:
  imports:
    - python_lsp_mcp
  commands:
    - python-lsp-mcp --help

about:
  home: https://github.com/yourusername/python-lsp-mcp
  license: MIT
  license_file: LICENSE.txt
  summary: 'MCP server for Python LSP integration'
  description: |
    Python LSP-MCP bridges LLMs with Language Server Protocol servers,
    enabling AI agents to obtain language-aware context from Python codebases.
```

### Submitting to conda-forge

1. Fork https://github.com/conda-forge/staged-recipes
2. Add recipe to `recipes/python-lsp-mcp/`
3. Submit pull request
4. After merge, package available via:

```bash
conda install -c conda-forge python-lsp-mcp
```

## 4. Homebrew Distribution

### Create Formula

`Formula/python-lsp-mcp.rb`:

```ruby
class PythonLspMcp < Formula
  include Language::Python::Virtualenv

  desc "MCP server for Python LSP integration"
  homepage "https://github.com/yourusername/python-lsp-mcp"
  url "https://github.com/yourusername/python-lsp-mcp/archive/v0.1.0.tar.gz"
  sha256 "<checksum>"
  license "MIT"

  depends_on "python@3.12"

  resource "mcp" do
    url "https://files.pythonhosted.org/packages/.../mcp-1.0.0.tar.gz"
    sha256 "<checksum>"
  end

  # Add other dependencies...

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/python-lsp-mcp", "--help"
  end
end
```

### Submitting to Homebrew

```bash
# Create tap
brew tap yourusername/python-lsp-mcp

# Install
brew install yourusername/python-lsp-mcp/python-lsp-mcp
```

Or submit to main Homebrew repository:

1. Fork https://github.com/Homebrew/homebrew-core
2. Add formula to `Formula/p/python-lsp-mcp.rb`
3. Test: `brew install --build-from-source python-lsp-mcp`
4. Submit pull request

## 5. Nix Package

### Create Nix Expression

`default.nix`:

```nix
{ lib, python3Packages, fetchFromGitHub }:

python3Packages.buildPythonApplication rec {
  pname = "python-lsp-mcp";
  version = "0.1.0";

  src = fetchFromGitHub {
    owner = "yourusername";
    repo = "python-lsp-mcp";
    rev = "v${version}";
    sha256 = "<hash>";
  };

  propagatedBuildInputs = with python3Packages; [
    mcp
    pygls
    lsprotocol
    pydantic
  ];

  meta = with lib; {
    description = "MCP server for Python LSP integration";
    homepage = "https://github.com/yourusername/python-lsp-mcp";
    license = licenses.mit;
    maintainers = [ maintainers.yourusername ];
  };
}
```

### Usage with Nix

```bash
# Install
nix-env -iA nixpkgs.python-lsp-mcp

# Or in shell
nix-shell -p python-lsp-mcp

# Or with flakes
nix run github:yourusername/python-lsp-mcp
```

## 6. Snap Package

### Create snapcraft.yaml

```yaml
name: python-lsp-mcp
version: '0.1.0'
summary: MCP server for Python LSP integration
description: |
  Python LSP-MCP bridges LLMs with Language Server Protocol servers,
  enabling AI agents to obtain language-aware context from Python codebases.

grade: stable
confinement: strict
base: core22

apps:
  python-lsp-mcp:
    command: bin/python-lsp-mcp
    plugs: [home, network]

parts:
  python-lsp-mcp:
    plugin: python
    source: .
    python-packages:
      - .
    stage-packages:
      - python3-pip
```

### Build and Publish

```bash
# Install snapcraft
sudo snap install snapcraft --classic

# Build
snapcraft

# Test
sudo snap install python-lsp-mcp_0.1.0_amd64.snap --dangerous

# Publish to Snap Store
snapcraft login
snapcraft upload python-lsp-mcp_0.1.0_amd64.snap --release=stable
```

### Users Install

```bash
sudo snap install python-lsp-mcp
```

## 7. Binary Executables

### Using PyInstaller

```bash
# Install PyInstaller
pip install pyinstaller

# Create binary
pyinstaller --onefile \
  --name python-lsp-mcp \
  --add-data "src/python_lsp_mcp:python_lsp_mcp" \
  src/python_lsp_mcp/__main__.py

# Output: dist/python-lsp-mcp
```

### Using Nuitka

```bash
# Install Nuitka
pip install nuitka

# Compile to binary
python -m nuitka \
  --standalone \
  --onefile \
  --output-filename=python-lsp-mcp \
  src/python_lsp_mcp/__main__.py

# Output: python-lsp-mcp.bin
```

### Distribution

```bash
# Create releases for different platforms
# Linux
pyinstaller --onefile python-lsp-mcp.spec
mv dist/python-lsp-mcp dist/python-lsp-mcp-linux-amd64

# macOS (on macOS machine)
pyinstaller --onefile python-lsp-mcp.spec
mv dist/python-lsp-mcp dist/python-lsp-mcp-macos-arm64

# Attach to GitHub release
gh release upload v0.1.0 dist/python-lsp-mcp-*
```

## 8. Wheel Files

### Direct Wheel Distribution

```bash
# Build wheel
python -m build --wheel

# Users install directly
pip install python_lsp_mcp-0.1.0-py3-none-any.whl
```

### Platform-Specific Wheels

For binary extensions:

```bash
# Build for current platform
python -m build

# Output: python_lsp_mcp-0.1.0-cp312-cp312-linux_x86_64.whl
```

## 9. Git Submodules

Users can add as submodule:

```bash
# In their project
git submodule add https://github.com/yourusername/python-lsp-mcp.git vendor/python-lsp-mcp
cd vendor/python-lsp-mcp
pip install -e .
```

## 10. Direct Download

Provide direct download links:

```bash
# Download and install
curl -L https://github.com/yourusername/python-lsp-mcp/archive/v0.1.0.tar.gz | tar xz
cd python-lsp-mcp-0.1.0
pip install .
```

## Comparison Matrix

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **PyPI** | Easy `pip install`, discoverable | Requires PyPI account | General users |
| **GitHub** | Direct from source, bleeding edge | Requires git | Developers |
| **Docker** | Isolated, reproducible | Larger size, Docker required | Production |
| **Conda** | Cross-platform, popular in data science | Slower installation | Data scientists |
| **Homebrew** | Easy on macOS/Linux | macOS/Linux only | Mac users |
| **uv** | Fast, modern | Less known | Power users |
| **Snap** | Universal Linux | Linux only, confined | Linux users |
| **Binary** | No Python required | Platform-specific builds | End users |

## Recommendations

**For Maximum Reach**:
1. **PyPI** (primary) - Most Python users
2. **GitHub** - Developers and contributors
3. **Docker** - Production/enterprise users

**For Specific Audiences**:
- **Data Science**: Add Conda
- **macOS Users**: Add Homebrew
- **Linux Users**: Add Snap
- **Enterprise**: Add Docker + binary executables

## Automation

### Multi-Platform Publishing

`.github/workflows/release-all.yml`:

```yaml
name: Release All Platforms

on:
  release:
    types: [published]

jobs:
  pypi:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pypa/gh-action-pypi-publish@release/v1

  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: yourusername/python-lsp-mcp:latest

  # Add more jobs for other platforms...
```

## Next Steps

- Review [PyPI Guide](./pypi.md) for package registry details
- Check [GitHub Guide](./github.md) for git-based distribution
- Explore platform-specific documentation for each method

## Support

- PyPI: https://pypi.org
- Docker Hub: https://hub.docker.com
- conda-forge: https://conda-forge.org
- Homebrew: https://brew.sh
