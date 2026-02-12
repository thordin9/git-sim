# git-sim MCP Server

A Model Context Protocol (MCP) server that provides a tool interface to git-sim, enabling AI agents and LLMs to generate visual simulations of Git operations.

## Overview

The git-sim MCP server exposes git-sim functionality through the MCP protocol, allowing AI agents to:
- Visualize Git commands before execution
- Generate educational content about Git operations
- Create visual documentation of Git workflows
- Debug and understand complex Git operations

## Features

- **Full git-sim support**: Access all git-sim commands (log, merge, rebase, commit, etc.)
- **Remote repository cloning**: Clone repositories to temporary locations for network-based access
- **Multiple transport protocols**: 
  - stdio (default) - for local integration
  - SSE (Server-Sent Events) - for HTTP-based communication with CORS support
- **Streaming support**: Real-time output streaming for long-running operations
- **Comprehensive tool schema**: Well-documented parameters for easy agent integration
- **Image and video generation**: Support for both static images and animated videos
- **Flexible output**: Returns both file paths and embedded image data
- **Session management**: Cloned repositories persist for the session lifecycle
- **Security features**: Configurable SSH host key checking and CORS settings

## Installation

### As a Python package

```bash
# Install from the git-sim repository
pip install -e ".[mcp]"
```

### Dependencies

The MCP server requires the following additional dependencies:
- `mcp` - Model Context Protocol SDK
- `starlette` - ASGI framework for SSE transport
- `uvicorn` - ASGI server for SSE transport

These are automatically installed with the `[mcp]` extra.

## Usage

### Starting the Server

#### stdio transport (default)

Use stdio transport for local integration with MCP clients:

```bash
# Run the MCP server with stdio transport
python -m git_sim_mcp

# Or using the entry point
git-sim-mcp
```

#### SSE transport

Use SSE transport for HTTP-based communication:

```bash
# Run with SSE on default port 8000
python -m git_sim_mcp --transport sse

# Specify custom host and port
python -m git_sim_mcp --transport sse --host 0.0.0.0 --port 8080
```

### Configuration for MCP Clients

#### Claude Desktop Configuration

Add to your Claude Desktop config file (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "git-sim": {
      "command": "python",
      "args": ["-m", "git_sim_mcp"],
      "env": {}
    }
  }
}
```

#### Cline Configuration

Add to your Cline MCP settings:

```json
{
  "git-sim": {
    "command": "git-sim-mcp",
    "args": [],
    "disabled": false
  }
}
```

#### SSE Client Configuration

For SSE-based clients:

```json
{
  "git-sim": {
    "url": "http://localhost:8000/sse",
    "transport": "sse"
  }
}
```

## Tool Schema

The server provides two tools:

### 1. clone-repo Tool

Clone a Git repository to a temporary location for the session. This is useful when the MCP server is accessed over a network and doesn't have direct access to the repository.

#### Required Parameters

- **repo_url** (string): The Git repository URL to clone (SSH or HTTPS)

#### Optional Parameters

- **branch** (string): Optional branch to checkout after cloning

#### Example

```json
{
  "repo_url": "https://github.com/user/repo.git",
  "branch": "main"
}
```

### 2. git-sim Tool

The server provides a tool called `git-sim` with the following parameters:

#### Required Parameters

- **command** (string): The git-sim subcommand to execute
  - Supported commands: `add`, `branch`, `checkout`, `cherry-pick`, `clean`, `clone`, `commit`, `config`, `fetch`, `init`, `log`, `merge`, `mv`, `pull`, `push`, `rebase`, `remote`, `reset`, `restore`, `revert`, `rm`, `stash`, `status`, `switch`, `tag`

#### Optional Parameters

- **args** (array of strings): Positional arguments for the command (e.g., branch names, file names)
- **repo_path** (string): Path to the git repository (default: current directory)
- **animate** (boolean): Generate animated video instead of static image (default: false)
- **n** (integer): Number of commits to display (default: 5)
- **light_mode** (boolean): Use light theme with white background (default: false)
- **img_format** (string): Output image format - `jpg` or `png` (default: jpg)
- **video_format** (string): Output video format - `mp4` or `webm` (default: mp4)
- **low_quality** (boolean): Render video in low quality for faster generation (default: false)
- **reverse** (boolean): Display commit history in reverse (default: false)
- **all** (boolean): Display all local branches (default: false)
- **media_dir** (string): Custom output directory for media files
- **output_only_path** (boolean): Only return the file path (default: false)
- **extra_flags** (array of strings): Additional git-sim flags

## Usage Examples for Agents

### Remote Repository Workflow

When the MCP server doesn't have direct access to a repository (e.g., network access), use the clone-repo tool first:

#### Example 1: Clone a repository and visualize it

Step 1 - Clone the repository:
```json
{
  "tool": "clone-repo",
  "arguments": {
    "repo_url": "https://github.com/user/repo.git"
  }
}
```

Response will include the local path, e.g., `/tmp/git-sim-clone-abc123`

Step 2 - Use the cloned repository with git-sim:
```json
{
  "tool": "git-sim",
  "arguments": {
    "command": "log",
    "n": 10,
    "repo_path": "/tmp/git-sim-clone-abc123"
  }
}
```

#### Example 2: Clone a specific branch

```json
{
  "tool": "clone-repo",
  "arguments": {
    "repo_url": "git@github.com:user/private-repo.git",
    "branch": "develop"
  }
}
```

### Local Repository Examples

For local repositories or when the server has direct access:

### Example 1: Visualize git log

```json
{
  "command": "log",
  "n": 10,
  "repo_path": "/path/to/repo"
}
```

### Example 2: Simulate a merge operation

```json
{
  "command": "merge",
  "args": ["feature-branch"],
  "repo_path": "/path/to/repo"
}
```

### Example 3: Create an animated rebase visualization

```json
{
  "command": "rebase",
  "args": ["main"],
  "animate": true,
  "low_quality": true,
  "repo_path": "/path/to/repo"
}
```

### Example 4: Show current repository status

```json
{
  "command": "status",
  "light_mode": true,
  "repo_path": "/path/to/repo"
}
```

### Example 5: Visualize branch creation

```json
{
  "command": "branch",
  "args": ["new-feature"],
  "repo_path": "/path/to/repo"
}
```

### Example 6: Cherry-pick visualization

```json
{
  "command": "cherry-pick",
  "args": ["abc123"],
  "repo_path": "/path/to/repo"
}
```

## Response Format

The tool returns a sequence of content items:

1. **Text Content**: Contains execution details
   - Success/failure status
   - Command executed
   - Output file path
   - Command output

2. **Image Content** (for image outputs): 
   - Base64-encoded image data
   - MIME type (image/jpeg or image/png)

Example successful response:
```
✓ git-sim log executed successfully

Command: git-sim -n 5 --img-format jpg -d --output-only-path log
Output file: /path/to/repo/git-sim_media/git-sim-log_01-01-24_12-00-00.jpg

[Image data embedded]
```

## Health Check (SSE mode only)

When running in SSE mode, the server exposes a health check endpoint:

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "service": "git-sim-mcp",
  "transport": "sse"
}
```

## Command-Line Options

```
usage: git-sim-mcp [-h] [--version] [--transport {stdio,sse}] 
                   [--host HOST] [--port PORT]
                   [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]

options:
  -h, --help            Show this help message and exit
  --version             Show version and exit
  --transport {stdio,sse}
                        Transport protocol (default: stdio)
  --host HOST           Host for SSE transport (default: 127.0.0.1)
  --port PORT           Port for SSE transport (default: 8000)
  --log-level LEVEL     Logging level (default: INFO)
```

## Environment Variables

### Git-sim Configuration

You can configure git-sim behavior using environment variables (same as regular git-sim):

```bash
export git_sim_media_dir=~/Desktop/git-visualizations
export git_sim_light_mode=true
export git_sim_animate=false
```

### Remote Repository Cloning Configuration

When using the `clone-repo` tool, you can configure SSH and Git behavior:

- **GIT_SIM_SSH_DISABLE_HOST_KEY_CHECKING**: Set to `true` to disable SSH host key checking (useful for automated environments with trusted hosts)

```bash
export GIT_SIM_SSH_DISABLE_HOST_KEY_CHECKING=true
```

### CORS Configuration (SSE Transport Only)

When running the server with SSE transport, you can configure CORS settings:

- **GIT_SIM_CORS_ALLOW_ORIGINS**: Comma-separated list of allowed origins (default: `*`)
- **GIT_SIM_CORS_ALLOW_METHODS**: Comma-separated list of allowed HTTP methods (default: `GET,POST,OPTIONS`)
- **GIT_SIM_CORS_ALLOW_HEADERS**: Comma-separated list of allowed headers (default: `*`)
- **GIT_SIM_CORS_ALLOW_CREDENTIALS**: Set to `true` to allow credentials (default: `false`)

```bash
export GIT_SIM_CORS_ALLOW_ORIGINS="https://example.com,https://app.example.com"
export GIT_SIM_CORS_ALLOW_METHODS="GET,POST,OPTIONS"
export GIT_SIM_CORS_ALLOW_HEADERS="Content-Type,Authorization"
export GIT_SIM_CORS_ALLOW_CREDENTIALS=true
```

## Troubleshooting

### Server won't start

1. Check that git-sim is installed and accessible:
   ```bash
   git-sim --version
   ```

2. Verify MCP dependencies are installed:
   ```bash
   pip install mcp starlette uvicorn
   ```

3. Check logs with verbose output:
   ```bash
   python -m git_sim_mcp --log-level DEBUG
   ```

### Tool execution fails

1. Verify the repository path is correct
2. Check that git-sim can run directly:
   ```bash
   cd /path/to/repo
   git-sim log
   ```
3. Review the error message in the tool response

### Images not displaying

1. Check the generated file path in the response
2. Verify file permissions
3. For SSE mode, ensure the server has access to the repository

## Development

### Running Tests

```bash
# Run all MCP server tests
pytest tests/mcp_tests/

# Run with verbose output
pytest -v tests/mcp_tests/

# Run specific test file
pytest tests/mcp_tests/test_server.py
```

### Project Structure

```
src/git_sim_mcp/
├── __init__.py          # Package initialization
├── __main__.py          # CLI entry point
├── server.py            # Core MCP server implementation
└── sse_server.py        # SSE transport server
```

## Contributing

Contributions are welcome! Please see the main [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## License

This MCP server follows the same license as git-sim: GPL-2.0

## Related Links

- [git-sim Repository](https://github.com/initialcommit-com/git-sim)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

## Support

For issues specific to the MCP server, please open an issue on the [git-sim repository](https://github.com/initialcommit-com/git-sim/issues) with the `mcp` label.
