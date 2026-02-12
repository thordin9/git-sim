# git-sim MCP Server Installation and Quick Start

## Overview

The git-sim MCP (Model Context Protocol) server enables AI agents and LLMs to generate visual simulations of Git operations using git-sim.

## Installation

### Prerequisites

Before installing the MCP server, ensure you have:

1. **Python 3.9 or higher**
2. **git-sim and its dependencies** (if you want full functionality)
   - See [git-sim installation guide](../../README.md#installation)
   - For MCP server testing without full git-sim, you can skip this

### Install the MCP Server

#### Option 1: With full git-sim support (recommended)

```bash
# Clone the repository
git clone https://github.com/initialcommit-com/git-sim.git
cd git-sim

# Install git-sim with MCP support
pip install -e ".[mcp]"

# Verify installation
git-sim-mcp --version
```

#### Option 2: Development installation

```bash
# Install only MCP dependencies for server development
pip install mcp starlette uvicorn httpx

# Run server with PYTHONPATH
PYTHONPATH=src python -m git_sim_mcp --version
```

## Quick Start

### 1. Start the Server

#### stdio mode (for local MCP clients)

```bash
git-sim-mcp
# or
python -m git_sim_mcp
```

#### SSE mode (for HTTP-based clients)

```bash
git-sim-mcp --transport sse --port 8000
# or
python -m git_sim_mcp --transport sse --port 8000
```

### 2. Configure Your MCP Client

#### For Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "git-sim": {
      "command": "git-sim-mcp"
    }
  }
}
```

#### For Cline (VS Code Extension)

Add to Cline MCP settings:

```json
{
  "git-sim": {
    "command": "git-sim-mcp",
    "args": []
  }
}
```

### 3. Use the Tool

Ask your AI assistant to:
- "Visualize the git log for this repository"
- "Show me what happens when I merge the feature branch"
- "Create a diagram of the current branch structure"

The assistant will use the git-sim MCP tool to generate visualizations.

## Testing

### Run Unit Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/mcp_tests/test_server.py -v
```

### Run Integration Tests

```bash
# Requires git-sim to be fully installed
pytest tests/mcp_tests/test_integration.py -v -m integration
```

### Run All Tests

```bash
pytest tests/mcp_tests/ -v
```

## Documentation

- **[MCP Server README](README.md)** - Complete server documentation
- **[Examples](EXAMPLES.md)** - Detailed usage examples
- **[git-sim README](../../README.md)** - Main git-sim documentation

## Troubleshooting

### "git-sim-mcp: command not found"

The package wasn't installed correctly. Try:

```bash
pip install -e ".[mcp]"
# or add to PATH manually
export PATH="$PATH:~/.local/bin"
```

### "No module named 'mcp'"

Install MCP dependencies:

```bash
pip install mcp starlette uvicorn
```

### "git-sim command not found" when running tools

Install git-sim:

```bash
pip install git-sim
```

See the [git-sim installation guide](../../README.md#installation) for system dependencies.

## Development

### Project Structure

```
src/git_sim_mcp/
├── __init__.py          # Package initialization
├── __main__.py          # CLI entry point
├── server.py            # Core MCP server (stdio)
├── sse_server.py        # SSE/HTTP server
├── README.md            # Full documentation
├── EXAMPLES.md          # Usage examples
└── INSTALL.md           # This file

tests/mcp_tests/
├── __init__.py
├── conftest.py          # Pytest configuration
├── test_server.py       # Unit tests
└── test_integration.py  # Integration tests
```

### Running from Source

```bash
# Set PYTHONPATH and run
export PYTHONPATH=/path/to/git-sim/src:$PYTHONPATH
python -m git_sim_mcp --help
```

### Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for contribution guidelines.

## License

GPL-2.0 - Same as git-sim

## Support

- [GitHub Issues](https://github.com/initialcommit-com/git-sim/issues)
- Tag issues with `mcp` label for MCP-specific problems
- [git-sim Discord](#) (if available)

## Related Links

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [git-sim Project](https://initialcommit.com/tools/git-sim)
