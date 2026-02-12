# Git-Sim Setup Guide with uv

This guide provides instructions for setting up git-sim and the MCP server using virtual environments with [uv](https://github.com/astral-sh/uv), a fast Python package installer and resolver.

## Why use uv?

`uv` is a modern, fast Python package installer that's significantly faster than pip. It's especially useful for creating and managing virtual environments and installing dependencies quickly.

## Prerequisites

1. **Python 3.9 or higher**
2. **uv** - Install it with:
   ```bash
   # On macOS and Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # On Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # Or with pip
   pip install uv
   ```

3. **Manim dependencies** (for full git-sim functionality)
   - See the [Manim installation guide](https://docs.manim.community/en/stable/installation.html) for your platform

## Quick Start

### Option 1: Install git-sim only (Core Functionality)

```bash
# Create a virtual environment with uv
uv venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install git-sim dependencies
uv pip install -r requirements.txt

# Verify installation
python -m git_sim --version
```

### Option 2: Install with MCP Server Support

```bash
# Create a virtual environment with uv
uv venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install git-sim with MCP server dependencies
uv pip install -r requirements-mcp.txt

# Verify installation
python -m git_sim --version
python -m git_sim_mcp --version
```

### Option 3: Install for Development

```bash
# Create a virtual environment with uv
uv venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install all dependencies including dev tools
uv pip install -r requirements-dev.txt

# Install git-sim in editable mode
uv pip install -e .

# Verify installation
git-sim --version
git-sim-mcp --version
```

## Alternative: System-wide Installation with uv

If you prefer not to use a virtual environment:

```bash
# Install git-sim globally using uv
uv pip install --system git-sim

# Or with MCP support
uv pip install --system "git-sim[mcp]"
```

**Note:** System-wide installation may conflict with other Python packages. Virtual environments are recommended.

## Using the MCP Server

After installing with MCP support, you can start the server:

```bash
# stdio mode (for local MCP clients like Claude Desktop)
python -m git_sim_mcp

# SSE mode (for HTTP-based clients)
python -m git_sim_mcp --transport sse --port 8000
```

For detailed MCP server configuration and usage, see [src/git_sim_mcp/INSTALL.md](src/git_sim_mcp/INSTALL.md).

## Requirements Files

This repository provides three requirements files:

- **requirements.txt** - Core git-sim dependencies
- **requirements-mcp.txt** - Includes core + MCP server dependencies
- **requirements-dev.txt** - Includes core + MCP + development tools (black, pytest, etc.)

## Updating Dependencies

To update all dependencies to their latest compatible versions:

```bash
# Update with uv
uv pip install --upgrade -r requirements-mcp.txt

# Or if using regular pip
pip install --upgrade -r requirements-mcp.txt
```

## Troubleshooting

### uv is not found after installation

Make sure uv is in your PATH. On macOS/Linux, add this to your `~/.bashrc` or `~/.zshrc`:

```bash
export PATH="$HOME/.cargo/bin:$PATH"
```

Then reload your shell or run `source ~/.bashrc` (or `~/.zshrc`).

### Virtual environment activation issues on Windows

If you get an error about execution policies on Windows, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Manim installation issues

If you encounter issues with Manim installation, refer to the platform-specific guides:
- [Windows](https://docs.manim.community/en/stable/installation/windows.html)
- [macOS](https://docs.manim.community/en/stable/installation/macos.html)
- [Linux](https://docs.manim.community/en/stable/installation/linux.html)

## Alternative Installation Methods

### Using pip instead of uv

All the commands above work with `pip` as well. Just replace `uv pip` with `pip`:

```bash
# Create venv with standard Python
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install with pip
pip install -r requirements-mcp.txt
```

### Using pyproject.toml

You can also install directly from pyproject.toml:

```bash
# Install with uv
uv pip install -e ".[mcp]"

# Install with pip
pip install -e ".[mcp]"
```

This is equivalent to using requirements-mcp.txt.

## Next Steps

- Read the [main README](README.md) for usage examples and features
- Check out the [MCP server documentation](src/git_sim_mcp/README.md) for AI agent integration
- See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
