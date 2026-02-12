"""MCP Server implementation for git-sim with HTTP and SSE support."""

import asyncio
import json
import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
import mcp.server.stdio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("git-sim-mcp")

# Initialize MCP server
server = Server("git-sim-mcp")


# Tool parameter schema for git-sim commands
GIT_SIM_TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "command": {
            "type": "string",
            "description": "The git-sim subcommand to execute (e.g., 'log', 'merge', 'rebase', 'commit', 'branch', etc.)",
            "enum": [
                "add",
                "branch",
                "checkout",
                "cherry-pick",
                "clean",
                "clone",
                "commit",
                "config",
                "fetch",
                "init",
                "log",
                "merge",
                "mv",
                "pull",
                "push",
                "rebase",
                "remote",
                "reset",
                "restore",
                "revert",
                "rm",
                "stash",
                "status",
                "switch",
                "tag",
            ],
        },
        "args": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Positional arguments for the git-sim command (e.g., branch name, file names, commit refs)",
            "default": [],
        },
        "repo_path": {
            "type": "string",
            "description": "Path to the git repository. Defaults to current directory if not specified.",
            "default": ".",
        },
        "animate": {
            "type": "boolean",
            "description": "Generate an animated video (.mp4) instead of a static image",
            "default": False,
        },
        "n": {
            "type": "integer",
            "description": "Number of commits to display from each branch head",
            "default": 5,
        },
        "light_mode": {
            "type": "boolean",
            "description": "Use light mode with white background instead of dark mode",
            "default": False,
        },
        "img_format": {
            "type": "string",
            "description": "Output format for images (jpg or png)",
            "enum": ["jpg", "png"],
            "default": "jpg",
        },
        "video_format": {
            "type": "string",
            "description": "Output format for videos (mp4 or webm, requires --animate)",
            "enum": ["mp4", "webm"],
            "default": "mp4",
        },
        "low_quality": {
            "type": "boolean",
            "description": "Render video in low quality for faster generation (requires --animate)",
            "default": False,
        },
        "reverse": {
            "type": "boolean",
            "description": "Display commit history in reverse direction",
            "default": False,
        },
        "all": {
            "type": "boolean",
            "description": "Display all local branches in log output",
            "default": False,
        },
        "media_dir": {
            "type": "string",
            "description": "Custom output directory for generated media files",
            "default": None,
        },
        "output_only_path": {
            "type": "boolean",
            "description": "Only output the path to generated media file",
            "default": False,
        },
        "extra_flags": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Additional git-sim flags not covered by other parameters",
            "default": [],
        },
    },
    "required": ["command"],
}


def build_git_sim_command(
    command: str,
    args: List[str] = None,
    repo_path: str = ".",
    animate: bool = False,
    n: int = 5,
    light_mode: bool = False,
    img_format: str = "jpg",
    video_format: str = "mp4",
    low_quality: bool = False,
    reverse: bool = False,
    all_branches: bool = False,
    media_dir: Optional[str] = None,
    output_only_path: bool = False,
    extra_flags: List[str] = None,
) -> List[str]:
    """Build the git-sim command with all options."""
    cmd = ["git-sim"]

    # Add global options
    if animate:
        cmd.append("--animate")

    cmd.extend(["-n", str(n)])

    if light_mode:
        cmd.append("--light-mode")

    cmd.extend(["--img-format", img_format])

    if animate:
        cmd.extend(["--video-format", video_format])
        if low_quality:
            cmd.append("--low-quality")

    if reverse:
        cmd.append("--reverse")

    if all_branches:
        cmd.append("--all")

    if media_dir:
        cmd.extend(["--media-dir", media_dir])

    if output_only_path:
        cmd.append("--output-only-path")

    # Disable auto-opening of files
    cmd.append("-d")

    # Add extra flags if provided
    if extra_flags:
        cmd.extend(extra_flags)

    # Add the subcommand
    cmd.append(command)

    # Add positional arguments
    if args:
        cmd.extend(args)

    return cmd


async def execute_git_sim(
    command: str, args: List[str] = None, repo_path: str = ".", **options
) -> Dict[str, Any]:
    """
    Execute a git-sim command and return the result.

    Returns:
        Dictionary containing:
        - success: bool indicating if command succeeded
        - output: stdout from command
        - error: stderr from command (if any)
        - media_path: path to generated media file (if any)
        - media_data: base64-encoded media data (for images)
    """
    try:
        # Build the command
        cmd = build_git_sim_command(
            command=command, args=args or [], repo_path=repo_path, **options
        )

        logger.info(f"Executing command: {' '.join(cmd)}")

        # Execute the command
        result = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=repo_path,
        )

        stdout, stderr = await result.communicate()

        stdout_str = stdout.decode("utf-8", errors="ignore")
        stderr_str = stderr.decode("utf-8", errors="ignore")

        success = result.returncode == 0

        response = {
            "success": success,
            "output": stdout_str,
            "error": stderr_str if stderr_str else None,
            "command": " ".join(cmd),
            "return_code": result.returncode,
        }

        # Try to extract the media file path from output
        if success and stdout_str:
            # When output_only_path is used, stdout contains just the path
            if options.get("output_only_path", False):
                media_path = stdout_str.strip()
                if media_path and Path(media_path).exists():
                    response["media_path"] = media_path
            else:
                # Try to find the path in the output
                for line in stdout_str.split("\n"):
                    if "git-sim_media" in line or line.endswith(
                        (".jpg", ".png", ".mp4", ".webm")
                    ):
                        # Extract path from output
                        parts = line.strip().split()
                        for part in parts:
                            if Path(part).exists() and part.endswith(
                                (".jpg", ".png", ".mp4", ".webm")
                            ):
                                response["media_path"] = part
                                break

        return response

    except Exception as e:
        logger.error(f"Error executing git-sim: {e}", exc_info=True)
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "command": " ".join(cmd) if "cmd" in locals() else None,
        }


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="git-sim",
            description="""Execute git-sim to visualize Git operations.

git-sim generates visual simulations of Git commands as images or videos. This is useful for:
- Understanding how Git commands work before executing them
- Creating visual documentation of Git workflows
- Learning and teaching Git concepts
- Debugging complex Git operations

The tool supports all major Git commands including: log, branch, merge, rebase, commit, 
cherry-pick, reset, revert, stash, and many more.

USAGE INSTRUCTIONS FOR AGENTS:
1. Specify the 'command' parameter with the git-sim subcommand (e.g., 'log', 'merge', 'branch')
2. Use 'args' array for positional arguments (e.g., branch names, file names)
3. Set 'repo_path' to the target repository (defaults to current directory)
4. Use optional parameters to customize the visualization:
   - 'animate': Generate video instead of static image
   - 'n': Number of commits to show (default: 5)
   - 'light_mode': Use white background
   - 'img_format': Choose 'jpg' or 'png'
   - And many more options...

EXAMPLES:
1. Visualize git log:
   {"command": "log", "n": 10}

2. Simulate a merge:
   {"command": "merge", "args": ["feature-branch"]}

3. Show branch creation:
   {"command": "branch", "args": ["new-feature"]}

4. Visualize rebase with animation:
   {"command": "rebase", "args": ["main"], "animate": true, "low_quality": true}

5. Show commit status:
   {"command": "status"}

The tool returns the path to generated visualization file and command output.""",
            inputSchema=GIT_SIM_TOOL_SCHEMA,
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any]
) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool execution requests."""
    if name != "git-sim":
        raise ValueError(f"Unknown tool: {name}")

    try:
        # Extract parameters
        command = arguments.get("command")
        if not command:
            return [
                TextContent(type="text", text="Error: 'command' parameter is required")
            ]

        args = arguments.get("args", [])
        repo_path = arguments.get("repo_path", ".")

        # Extract options
        options = {
            "animate": arguments.get("animate", False),
            "n": arguments.get("n", 5),
            "light_mode": arguments.get("light_mode", False),
            "img_format": arguments.get("img_format", "jpg"),
            "video_format": arguments.get("video_format", "mp4"),
            "low_quality": arguments.get("low_quality", False),
            "reverse": arguments.get("reverse", False),
            "all_branches": arguments.get("all", False),
            "media_dir": arguments.get("media_dir"),
            "output_only_path": arguments.get(
                "output_only_path", True
            ),  # Enable by default for easier parsing
            "extra_flags": arguments.get("extra_flags", []),
        }

        # Execute git-sim
        result = await execute_git_sim(
            command=command, args=args, repo_path=repo_path, **options
        )

        # Build response
        response_parts = []

        if result["success"]:
            response_text = f"✓ git-sim {command} executed successfully\n\n"
            response_text += f"Command: {result['command']}\n"

            if result.get("media_path"):
                response_text += f"Output file: {result['media_path']}\n"

            if result.get("output"):
                response_text += f"\nOutput:\n{result['output']}\n"

            response_parts.append(TextContent(type="text", text=response_text))

            # Try to include the image data if it's an image file
            media_path = result.get("media_path")
            if media_path and Path(media_path).exists():
                file_ext = Path(media_path).suffix.lower()
                if file_ext in [".jpg", ".jpeg", ".png"]:
                    try:
                        import base64

                        with open(media_path, "rb") as f:
                            image_data = base64.b64encode(f.read()).decode("utf-8")

                        mime_type = (
                            "image/jpeg"
                            if file_ext in [".jpg", ".jpeg"]
                            else "image/png"
                        )

                        response_parts.append(
                            ImageContent(
                                type="image", data=image_data, mimeType=mime_type
                            )
                        )
                    except Exception as e:
                        logger.warning(f"Could not read image file: {e}")
        else:
            error_text = f"✗ git-sim {command} failed\n\n"
            error_text += f"Command: {result.get('command', 'unknown')}\n"
            error_text += f"Return code: {result.get('return_code', 'unknown')}\n"

            if result.get("error"):
                error_text += f"\nError:\n{result['error']}\n"

            if result.get("output"):
                error_text += f"\nOutput:\n{result['output']}\n"

            response_parts.append(TextContent(type="text", text=error_text))

        return response_parts

    except Exception as e:
        logger.error(f"Error in tool execution: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error executing git-sim: {str(e)}")]


async def main():
    """Main entry point for the MCP server."""
    logger.info("Starting git-sim MCP server")

    # Run the server using stdio transport
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="git-sim-mcp",
                server_version=__version__,
                capabilities=server.get_capabilities(
                    notification_options=None, experimental_capabilities={}
                ),
            ),
        )


if __name__ == "__main__":
    import sys

    # Import version from package
    from git_sim_mcp import __version__

    # Run the server
    asyncio.run(main())
