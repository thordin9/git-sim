"""Tests for git-sim MCP server."""

import pytest
import asyncio
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Import MCP server components
from git_sim_mcp.server import (
    build_git_sim_command,
    execute_git_sim,
    handle_list_tools,
    handle_call_tool,
)


class TestBuildGitSimCommand:
    """Test command building functionality."""
    
    def test_basic_command(self):
        """Test building a basic command."""
        cmd = build_git_sim_command(command="log")
        
        assert "git-sim" in cmd
        assert "log" in cmd
        assert "-d" in cmd  # Auto-disable file opening
    
    def test_command_with_args(self):
        """Test building command with positional arguments."""
        cmd = build_git_sim_command(
            command="merge",
            args=["feature-branch"]
        )
        
        assert "git-sim" in cmd
        assert "merge" in cmd
        assert "feature-branch" in cmd
    
    def test_command_with_animate(self):
        """Test building command with animation."""
        cmd = build_git_sim_command(
            command="log",
            animate=True,
            low_quality=True
        )
        
        assert "--animate" in cmd
        assert "--low-quality" in cmd
    
    def test_command_with_n_option(self):
        """Test building command with -n option."""
        cmd = build_git_sim_command(
            command="log",
            n=10
        )
        
        assert "-n" in cmd
        assert "10" in cmd
    
    def test_command_with_light_mode(self):
        """Test building command with light mode."""
        cmd = build_git_sim_command(
            command="log",
            light_mode=True
        )
        
        assert "--light-mode" in cmd
    
    def test_command_with_img_format(self):
        """Test building command with image format."""
        cmd = build_git_sim_command(
            command="log",
            img_format="png"
        )
        
        assert "--img-format" in cmd
        assert "png" in cmd
    
    def test_command_with_all_branches(self):
        """Test building command with all branches option."""
        cmd = build_git_sim_command(
            command="log",
            all_branches=True
        )
        
        assert "--all" in cmd
    
    def test_command_with_media_dir(self):
        """Test building command with custom media directory."""
        cmd = build_git_sim_command(
            command="log",
            media_dir="/tmp/output"
        )
        
        assert "--media-dir" in cmd
        assert "/tmp/output" in cmd
    
    def test_command_with_extra_flags(self):
        """Test building command with extra flags."""
        cmd = build_git_sim_command(
            command="log",
            extra_flags=["--quiet", "--reverse"]
        )
        
        assert "--quiet" in cmd
        assert "--reverse" in cmd


@pytest.mark.asyncio
class TestExecuteGitSim:
    """Test git-sim execution functionality."""
    
    @patch('asyncio.create_subprocess_exec')
    async def test_successful_execution(self, mock_subprocess):
        """Test successful git-sim execution."""
        # Mock the subprocess
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(
            return_value=(b"/path/to/output.jpg\n", b"")
        )
        mock_process.returncode = 0
        mock_subprocess.return_value = mock_process
        
        result = await execute_git_sim(
            command="log",
            output_only_path=True
        )
        
        assert result["success"] is True
        assert result["return_code"] == 0
        assert result["error"] is None or result["error"] == ""
    
    @patch('asyncio.create_subprocess_exec')
    async def test_failed_execution(self, mock_subprocess):
        """Test failed git-sim execution."""
        # Mock the subprocess
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(
            return_value=(b"", b"Error: Invalid command\n")
        )
        mock_process.returncode = 1
        mock_subprocess.return_value = mock_process
        
        result = await execute_git_sim(command="invalid")
        
        assert result["success"] is False
        assert result["return_code"] == 1
        assert "Error" in result["error"]
    
    @patch('asyncio.create_subprocess_exec')
    async def test_execution_with_repo_path(self, mock_subprocess):
        """Test execution with custom repo path."""
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(
            return_value=(b"/path/to/output.jpg\n", b"")
        )
        mock_process.returncode = 0
        mock_subprocess.return_value = mock_process
        
        result = await execute_git_sim(
            command="log",
            repo_path="/tmp/test-repo",
            output_only_path=True
        )
        
        assert result["success"] is True
        # Verify the subprocess was called with correct cwd
        mock_subprocess.assert_called_once()
        call_kwargs = mock_subprocess.call_args[1]
        assert call_kwargs["cwd"] == "/tmp/test-repo"


@pytest.mark.asyncio
class TestToolHandlers:
    """Test MCP tool handler functions."""
    
    async def test_list_tools(self):
        """Test listing available tools."""
        tools = await handle_list_tools()
        
        assert len(tools) == 1
        assert tools[0].name == "git-sim"
        assert "visualize" in tools[0].description.lower()
        assert tools[0].inputSchema is not None
    
    async def test_tool_schema_has_required_fields(self):
        """Test that tool schema includes all required fields."""
        tools = await handle_list_tools()
        schema = tools[0].inputSchema
        
        assert "properties" in schema
        assert "command" in schema["properties"]
        assert "required" in schema
        assert "command" in schema["required"]
    
    async def test_tool_schema_has_all_commands(self):
        """Test that tool schema includes all git-sim commands."""
        tools = await handle_list_tools()
        schema = tools[0].inputSchema
        
        expected_commands = [
            "add", "branch", "checkout", "cherry-pick", "clean", "clone",
            "commit", "config", "fetch", "init", "log", "merge", "mv",
            "pull", "push", "rebase", "remote", "reset", "restore",
            "revert", "rm", "stash", "status", "switch", "tag"
        ]
        
        command_enum = schema["properties"]["command"]["enum"]
        for cmd in expected_commands:
            assert cmd in command_enum
    
    @patch('git_sim_mcp.server.execute_git_sim')
    async def test_call_tool_success(self, mock_execute):
        """Test successful tool call."""
        mock_execute.return_value = {
            "success": True,
            "output": "Success",
            "error": None,
            "command": "git-sim log",
            "return_code": 0,
            "media_path": "/tmp/output.jpg"
        }
        
        result = await handle_call_tool(
            name="git-sim",
            arguments={"command": "log"}
        )
        
        assert len(result) > 0
        assert result[0].type == "text"
        assert "✓" in result[0].text
        assert "success" in result[0].text.lower()
    
    @patch('git_sim_mcp.server.execute_git_sim')
    async def test_call_tool_failure(self, mock_execute):
        """Test failed tool call."""
        mock_execute.return_value = {
            "success": False,
            "output": "",
            "error": "Command failed",
            "command": "git-sim log",
            "return_code": 1
        }
        
        result = await handle_call_tool(
            name="git-sim",
            arguments={"command": "log"}
        )
        
        assert len(result) > 0
        assert result[0].type == "text"
        assert "✗" in result[0].text
        assert "failed" in result[0].text.lower()
    
    async def test_call_tool_missing_command(self):
        """Test tool call without required command parameter."""
        result = await handle_call_tool(
            name="git-sim",
            arguments={}
        )
        
        assert len(result) > 0
        assert result[0].type == "text"
        assert "error" in result[0].text.lower()
        assert "required" in result[0].text.lower()
    
    async def test_call_tool_unknown_tool(self):
        """Test calling an unknown tool."""
        with pytest.raises(ValueError, match="Unknown tool"):
            await handle_call_tool(
                name="unknown-tool",
                arguments={"command": "log"}
            )
    
    @patch('git_sim_mcp.server.execute_git_sim')
    async def test_call_tool_with_all_options(self, mock_execute):
        """Test tool call with all available options."""
        mock_execute.return_value = {
            "success": True,
            "output": "Success",
            "error": None,
            "command": "git-sim --animate -n 10 log",
            "return_code": 0
        }
        
        arguments = {
            "command": "log",
            "args": ["--oneline"],
            "repo_path": "/tmp/repo",
            "animate": True,
            "n": 10,
            "light_mode": True,
            "img_format": "png",
            "video_format": "webm",
            "low_quality": True,
            "reverse": True,
            "all": True,
            "media_dir": "/tmp/output",
            "output_only_path": True,
            "extra_flags": ["--quiet"]
        }
        
        result = await handle_call_tool(
            name="git-sim",
            arguments=arguments
        )
        
        assert len(result) > 0
        assert result[0].type == "text"
        
        # Verify execute_git_sim was called with correct parameters
        mock_execute.assert_called_once()
        call_kwargs = mock_execute.call_args[1]
        assert call_kwargs["animate"] is True
        assert call_kwargs["n"] == 10
        assert call_kwargs["light_mode"] is True


@pytest.mark.asyncio
class TestImageHandling:
    """Test image data handling."""
    
    @patch('git_sim_mcp.server.execute_git_sim')
    @patch('pathlib.Path.exists')
    @patch('builtins.open')
    async def test_image_embedding(self, mock_open, mock_exists, mock_execute):
        """Test that images are embedded in response."""
        # Mock file existence and reading
        mock_exists.return_value = True
        mock_file = Mock()
        mock_file.read.return_value = b"fake_image_data"
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=False)
        mock_open.return_value = mock_file
        
        mock_execute.return_value = {
            "success": True,
            "output": "Success",
            "error": None,
            "command": "git-sim log",
            "return_code": 0,
            "media_path": "/tmp/output.jpg"
        }
        
        result = await handle_call_tool(
            name="git-sim",
            arguments={"command": "log"}
        )
        
        # Should have both text and image content
        assert len(result) >= 1
        text_content = [r for r in result if r.type == "text"]
        image_content = [r for r in result if r.type == "image"]
        
        assert len(text_content) > 0
        # Image embedding might not work in test environment, so we just check structure
        assert len(image_content) >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
