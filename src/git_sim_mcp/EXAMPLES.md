# git-sim MCP Server Examples

This document provides detailed examples of using the git-sim MCP server with various MCP clients.

## Table of Contents

1. [Basic Examples](#basic-examples)
2. [Advanced Usage](#advanced-usage)
3. [Client Integration Examples](#client-integration-examples)
4. [Troubleshooting](#troubleshooting)

## Basic Examples

### Example 1: Simple Log Visualization

Visualize the git log for the current repository:

```json
{
  "command": "log",
  "n": 5
}
```

**Response:**
- Image file showing the last 5 commits
- Embedded image data (if image format)
- File path to the generated visualization

### Example 2: Merge Simulation

Simulate merging a feature branch into the current branch:

```json
{
  "command": "merge",
  "args": ["feature-branch"],
  "repo_path": "/path/to/repo"
}
```

### Example 3: Animated Rebase

Create an animated video of a rebase operation:

```json
{
  "command": "rebase",
  "args": ["main"],
  "animate": true,
  "low_quality": true,
  "video_format": "mp4"
}
```

**Note:** Animation rendering can take time. Use `low_quality: true` for faster generation during testing.

## Advanced Usage

### Multi-Branch Visualization

Visualize all branches in the repository:

```json
{
  "command": "log",
  "all": true,
  "n": 10,
  "light_mode": true
}
```

### Cherry-Pick Visualization

Visualize a cherry-pick operation:

```json
{
  "command": "cherry-pick",
  "args": ["abc123def"],
  "repo_path": "/path/to/repo"
}
```

### Status with Custom Output

Check repository status with custom output directory:

```json
{
  "command": "status",
  "media_dir": "/tmp/git-visualizations",
  "img_format": "png"
}
```

### Branch Creation

Visualize creating a new branch:

```json
{
  "command": "branch",
  "args": ["new-feature"],
  "light_mode": true,
  "img_format": "png"
}
```

## Client Integration Examples

### Claude Desktop Integration

1. **Install the MCP server:**
   ```bash
   pip install -e ".[mcp]"
   ```

2. **Configure Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
   ```json
   {
     "mcpServers": {
       "git-sim": {
         "command": "python",
         "args": ["-m", "git_sim_mcp"],
         "env": {
           "PATH": "/usr/local/bin:/usr/bin:/bin"
         }
       }
     }
   }
   ```

3. **Use in Claude:**
   - "Can you visualize the git log for the last 10 commits?"
   - "Show me what happens when I merge the feature branch"
   - "Create a visualization of the current repository status"

### Cline Integration

1. **Configure Cline MCP settings:**
   ```json
   {
     "git-sim": {
       "command": "git-sim-mcp",
       "args": [],
       "disabled": false
     }
   }
   ```

2. **Use in Cline:**
   - Ask Cline to visualize git operations before making changes
   - Request visualizations to understand repository state
   - Generate documentation with visual git diagrams

### SSE Client Example (HTTP-based)

For HTTP-based clients using SSE transport:

1. **Start the SSE server:**
   ```bash
   python -m git_sim_mcp --transport sse --host 0.0.0.0 --port 8000
   ```

2. **Connect from your client:**
   ```javascript
   const eventSource = new EventSource('http://localhost:8000/sse');
   
   eventSource.onmessage = (event) => {
     const data = JSON.parse(event.data);
     // Handle MCP messages
   };
   ```

3. **Send tool requests:**
   ```javascript
   fetch('http://localhost:8000/messages', {
     method: 'POST',
     headers: {
       'Content-Type': 'application/json'
     },
     body: JSON.stringify({
       jsonrpc: '2.0',
       id: 1,
       method: 'tools/call',
       params: {
         name: 'git-sim',
         arguments: {
           command: 'log',
           n: 5
         }
       }
     })
   });
   ```

## Common Use Cases

### Documentation Generation

Generate visual documentation for your Git workflow:

```json
{
  "command": "log",
  "all": true,
  "n": 20,
  "light_mode": true,
  "img_format": "png",
  "media_dir": "/path/to/docs/images"
}
```

### Teaching Git Concepts

Create animations to teach Git operations:

```json
{
  "command": "rebase",
  "args": ["main"],
  "animate": true,
  "low_quality": false,
  "video_format": "mp4"
}
```

### Pre-Commit Visualization

Visualize what a commit will look like before actually committing:

```json
{
  "command": "commit",
  "args": ["-m", "Add new feature"],
  "repo_path": "/path/to/repo"
}
```

### Merge Conflict Preview

Preview merge operations to understand potential conflicts:

```json
{
  "command": "merge",
  "args": ["feature-branch"],
  "repo_path": "/path/to/repo"
}
```

## Parameter Reference

### Common Parameters

- **command** (required): Git command to simulate
- **args** (optional): Command arguments (branch names, file names, etc.)
- **repo_path** (optional): Repository path (defaults to current directory)
- **n** (optional): Number of commits to show (default: 5)

### Output Parameters

- **img_format**: `"jpg"` or `"png"` (default: `"jpg"`)
- **video_format**: `"mp4"` or `"webm"` (default: `"mp4"`)
- **media_dir**: Custom output directory
- **output_only_path**: Return only file path (default: `false`)

### Visual Parameters

- **light_mode**: Use white background (default: `false`)
- **animate**: Generate video instead of image (default: `false`)
- **low_quality**: Fast rendering for testing (default: `false`)
- **reverse**: Reverse commit order (default: `false`)
- **all**: Show all branches (default: `false`)

### Advanced Parameters

- **extra_flags**: Additional git-sim flags as array of strings

## Troubleshooting

### Issue: "git-sim command not found"

**Solution:**
```bash
# Install git-sim
pip install git-sim

# Verify installation
git-sim --version
```

### Issue: Server won't start

**Solution:**
```bash
# Check Python version (requires 3.7+)
python --version

# Install MCP dependencies
pip install -e ".[mcp]"

# Run with debug logging
python -m git_sim_mcp --log-level DEBUG
```

### Issue: Images not displaying

**Solution:**
- Check file permissions on the output directory
- Verify the `media_path` in the response
- For SSE mode, ensure server has access to repository

### Issue: Slow animation rendering

**Solution:**
```json
{
  "command": "log",
  "animate": true,
  "low_quality": true  // Much faster rendering
}
```

### Issue: Repository not found

**Solution:**
- Verify `repo_path` is correct
- Ensure it's a valid Git repository
- Check file permissions

## Best Practices

### 1. Use output_only_path for better parsing

```json
{
  "command": "log",
  "output_only_path": true
}
```

This makes it easier to extract the file path from the output.

### 2. Start with low quality for animations

```json
{
  "command": "rebase",
  "args": ["main"],
  "animate": true,
  "low_quality": true  // Test first
}
```

Once satisfied, remove `low_quality` for final output.

### 3. Use appropriate n values

```json
{
  "command": "log",
  "n": 5  // Small for quick overview
}
```

Larger values (20+) provide more context but take longer to render.

### 4. Specify repo_path explicitly

```json
{
  "command": "status",
  "repo_path": "/full/path/to/repo"
}
```

This avoids ambiguity and makes the code more maintainable.

### 5. Use light mode for documentation

```json
{
  "command": "log",
  "light_mode": true,  // Better for docs
  "img_format": "png"  // Better quality
}
```

Light mode with PNG format is ideal for documentation.

## Additional Resources

- [git-sim Documentation](../../README.md)
- [MCP Server README](../git_sim_mcp/README.md)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [git-sim GitHub Repository](https://github.com/initialcommit-com/git-sim)

## Contributing Examples

Have a useful example or integration? Please contribute!

1. Fork the repository
2. Add your example to this file
3. Submit a pull request

We especially welcome examples for:
- New MCP clients
- Interesting use cases
- Integration patterns
- Troubleshooting scenarios
