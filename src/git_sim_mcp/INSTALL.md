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

## Systemd Setup (Linux)

For production deployments on Linux systems, you can run the MCP server as a systemd service. This allows automatic startup on boot, automatic restart on failure, and centralized logging.

### Prerequisites

1. Install git-sim with MCP support:

**Recommended approach** - Install to user directory (no sudo required):

```bash
pip install --user git-sim[mcp]
# Ensure ~/.local/bin is in your PATH
export PATH="$HOME/.local/bin:$PATH"
```

Alternative approaches:

```bash
# Option 2: System-wide installation (requires sudo, may conflict with system packages)
sudo pip install git-sim[mcp]

# Option 3: Install from source for development
cd /path/to/git-sim
pip install --user -e ".[mcp]"
# or with sudo for system-wide
sudo pip install -e ".[mcp]"
```

**Note**: Installing packages with `sudo pip` can conflict with system package managers. For production use, consider using a virtual environment (see instructions below) or containerization. The systemd service can be configured to use a virtual environment by modifying the `ExecStart` path.

2. Verify the installation:

```bash
which git-sim-mcp
# Expected output for user installation: /home/username/.local/bin/git-sim-mcp
# Expected output for system installation: /usr/local/bin/git-sim-mcp
```

### Setup Steps

1. **Create a dedicated user for the service** (recommended for security):

```bash
sudo useradd --system --no-create-home --shell /bin/false git-sim
```

2. **Create the working directory**:

```bash
sudo mkdir -p /var/lib/git-sim/media
sudo chown -R git-sim:git-sim /var/lib/git-sim
```

3. **Copy the service file**:

```bash
sudo cp src/git_sim_mcp/git-sim-mcp.service /etc/systemd/system/
```

Or create it manually:

```bash
sudo nano /etc/systemd/system/git-sim-mcp.service
```

4. **Edit the service file** to match your setup:

```bash
sudo nano /etc/systemd/system/git-sim-mcp.service
```

Key settings to configure:
- `User` and `Group`: Change if using a different user
- `WorkingDirectory`: Change if using a different location
- `ExecStart`: Adjust path to git-sim-mcp if installed elsewhere (see note below for virtual environments)
- `--host` and `--port`: Configure network binding
- Environment variables: Uncomment and set as needed

**Using a virtual environment**: To use git-sim-mcp from a virtual environment, modify the `ExecStart` line:

```ini
ExecStart=/path/to/venv/bin/git-sim-mcp --transport sse --host 0.0.0.0 --port 8000 --log-level INFO
```

5. **Reload systemd and enable the service**:

```bash
sudo systemctl daemon-reload
sudo systemctl enable git-sim-mcp.service
```

6. **Start the service**:

```bash
sudo systemctl start git-sim-mcp.service
```

7. **Check the service status**:

```bash
sudo systemctl status git-sim-mcp.service
```

### Managing the Service

#### View logs:

```bash
# Follow logs in real-time
sudo journalctl -u git-sim-mcp.service -f

# View recent logs
sudo journalctl -u git-sim-mcp.service -n 100

# View logs since boot
sudo journalctl -u git-sim-mcp.service -b
```

#### Stop the service:

```bash
sudo systemctl stop git-sim-mcp.service
```

#### Restart the service:

```bash
sudo systemctl restart git-sim-mcp.service
```

#### Disable auto-start on boot:

```bash
sudo systemctl disable git-sim-mcp.service
```

### Configuration

The service file includes several environment variables that can be configured:

```ini
# Enable CORS for all origins (useful for web clients)
Environment="GIT_SIM_CORS_ACCEPT_ALL=true"

# Disable SSH host key checking (use with caution)
Environment="GIT_SIM_SSH_DISABLE_HOST_KEY_CHECKING=false"

# Set custom media output directory
Environment="git_sim_media_dir=/var/lib/git-sim/media"

# Enable light mode
Environment="git_sim_light_mode=false"
```

Uncomment and modify these in `/etc/systemd/system/git-sim-mcp.service`, then reload:

```bash
sudo systemctl daemon-reload
sudo systemctl restart git-sim-mcp.service
```

### Security Considerations

The provided service file includes security hardening options:

- `NoNewPrivileges=true`: Prevents privilege escalation
- `PrivateTmp=true`: Uses private /tmp directory
- `ProtectSystem=strict`: Makes most of the filesystem read-only
- `ProtectHome=true`: Makes /home inaccessible
- `ReadWritePaths=/var/lib/git-sim`: Allows writes only to working directory

For additional security, consider:

1. **Using a firewall** to restrict access to the service port:

```bash
sudo ufw allow from 192.168.1.0/24 to any port 8000
```

2. **Using a reverse proxy** (nginx, Apache) with SSL/TLS for HTTPS

3. **Configuring specific CORS origins** instead of accepting all

### Troubleshooting

#### Service fails to start

Check the logs:

```bash
sudo journalctl -u git-sim-mcp.service -n 50
```

Common issues:
- **Permission denied**: Ensure the user has access to `/var/lib/git-sim`
- **Command not found**: Verify `git-sim-mcp` is installed and path is correct
- **Port already in use**: Change the port in the service file

#### Service crashes

The service is configured to automatically restart on failure. Check logs to identify the issue:

```bash
sudo journalctl -u git-sim-mcp.service --since "1 hour ago"
```

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
