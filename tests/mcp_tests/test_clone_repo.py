"""Tests for clone-repo tool functionality."""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock

from git_sim_mcp.server import (
    clone_repo,
    handle_clone_repo_tool,
    handle_list_tools,
    _cloned_repos,
    cleanup_cloned_repos,
)


@pytest.mark.asyncio
class TestCloneRepo:
    """Test repository cloning functionality."""

    @patch("asyncio.create_subprocess_exec")
    @patch("tempfile.mkdtemp")
    async def test_successful_clone(self, mock_mkdtemp, mock_subprocess):
        """Test successful repository clone."""
        # Setup mocks
        temp_dir = "/tmp/git-sim-clone-test123"
        mock_mkdtemp.return_value = temp_dir
        
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(
            return_value=(b"Cloning into '/tmp/git-sim-clone-test123'...\n", b"")
        )
        mock_process.returncode = 0
        mock_subprocess.return_value = mock_process

        # Execute clone
        result = await clone_repo(repo_url="https://github.com/user/repo.git")

        # Verify result
        assert result["success"] is True
        assert result["local_path"] == temp_dir
        assert result["repo_url"] == "https://github.com/user/repo.git"
        assert "cloned successfully" in result["message"].lower()

        # Verify subprocess was called correctly
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0]
        assert "git" in call_args
        assert "clone" in call_args
        assert "https://github.com/user/repo.git" in call_args

    @patch("asyncio.create_subprocess_exec")
    @patch("tempfile.mkdtemp")
    async def test_clone_with_branch(self, mock_mkdtemp, mock_subprocess):
        """Test cloning with specific branch."""
        temp_dir = "/tmp/git-sim-clone-test456"
        mock_mkdtemp.return_value = temp_dir
        
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(
            return_value=(b"Cloning into '/tmp/git-sim-clone-test456'...\n", b"")
        )
        mock_process.returncode = 0
        mock_subprocess.return_value = mock_process

        result = await clone_repo(
            repo_url="https://github.com/user/repo.git", branch="develop"
        )

        assert result["success"] is True
        
        # Verify branch argument was passed
        call_args = mock_subprocess.call_args[0]
        assert "-b" in call_args
        assert "develop" in call_args

    @patch("asyncio.create_subprocess_exec")
    @patch("tempfile.mkdtemp")
    async def test_failed_clone(self, mock_mkdtemp, mock_subprocess):
        """Test failed repository clone."""
        temp_dir = "/tmp/git-sim-clone-test789"
        mock_mkdtemp.return_value = temp_dir
        
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(
            return_value=(b"", b"fatal: repository 'https://github.com/user/invalid.git' not found\n")
        )
        mock_process.returncode = 128
        mock_subprocess.return_value = mock_process

        result = await clone_repo(repo_url="https://github.com/user/invalid.git")

        assert result["success"] is False
        assert "not found" in result["error"]
        assert result["return_code"] == 128

    @patch("asyncio.create_subprocess_exec")
    @patch("tempfile.mkdtemp")
    @patch("os.path.exists")
    async def test_already_cloned_repo(self, mock_exists, mock_mkdtemp, mock_subprocess):
        """Test that already cloned repo is not cloned again."""
        # Setup: simulate a previously cloned repo
        repo_url = "https://github.com/user/repo.git"
        existing_path = "/tmp/git-sim-clone-existing"
        
        _cloned_repos.clear()
        _cloned_repos[repo_url] = existing_path
        mock_exists.return_value = True

        result = await clone_repo(repo_url=repo_url)

        # Should return success without calling git clone
        assert result["success"] is True
        assert result["local_path"] == existing_path
        assert "already cloned" in result["message"].lower()
        
        # Git clone should not be called
        mock_subprocess.assert_not_called()
        
        # Cleanup
        _cloned_repos.clear()

    @patch("os.getenv")
    @patch("asyncio.create_subprocess_exec")
    @patch("tempfile.mkdtemp")
    async def test_ssh_host_key_checking_disabled(self, mock_mkdtemp, mock_subprocess, mock_getenv):
        """Test SSH host key checking can be disabled via env var."""
        temp_dir = "/tmp/git-sim-clone-ssh-test"
        mock_mkdtemp.return_value = temp_dir
        
        # Mock environment variable
        def getenv_side_effect(key, default=None):
            if key == "GIT_SIM_SSH_DISABLE_HOST_KEY_CHECKING":
                return "true"
            return os.environ.get(key, default)
        
        mock_getenv.side_effect = getenv_side_effect
        
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(
            return_value=(b"Cloning...\n", b"")
        )
        mock_process.returncode = 0
        mock_subprocess.return_value = mock_process

        result = await clone_repo(repo_url="git@github.com:user/repo.git")

        assert result["success"] is True
        
        # Verify that GIT_SSH_COMMAND was set in env
        call_kwargs = mock_subprocess.call_args[1]
        assert "env" in call_kwargs
        env = call_kwargs["env"]
        assert "GIT_SSH_COMMAND" in env
        assert "StrictHostKeyChecking=no" in env["GIT_SSH_COMMAND"]


@pytest.mark.asyncio
class TestCloneRepoToolHandler:
    """Test clone-repo tool handler."""

    async def test_list_tools_includes_clone_repo(self):
        """Test that clone-repo tool is included in tool list."""
        tools = await handle_list_tools()

        # Should have both clone-repo and git-sim tools
        assert len(tools) == 2
        
        tool_names = [tool.name for tool in tools]
        assert "clone-repo" in tool_names
        assert "git-sim" in tool_names

    async def test_clone_repo_tool_schema(self):
        """Test clone-repo tool has correct schema."""
        tools = await handle_list_tools()
        clone_tool = next(t for t in tools if t.name == "clone-repo")

        schema = clone_tool.inputSchema
        assert "properties" in schema
        assert "repo_url" in schema["properties"]
        assert "branch" in schema["properties"]
        assert "required" in schema
        assert "repo_url" in schema["required"]

    @patch("git_sim_mcp.server.clone_repo")
    async def test_handle_clone_repo_tool_success(self, mock_clone):
        """Test successful clone-repo tool call."""
        mock_clone.return_value = {
            "success": True,
            "local_path": "/tmp/cloned-repo",
            "repo_url": "https://github.com/user/repo.git",
            "message": "Repository cloned successfully",
        }

        result = await handle_clone_repo_tool(
            arguments={"repo_url": "https://github.com/user/repo.git"}
        )

        assert len(result) == 1
        assert result[0].type == "text"
        assert "✓" in result[0].text
        assert "cloned successfully" in result[0].text.lower()
        assert "/tmp/cloned-repo" in result[0].text

    @patch("git_sim_mcp.server.clone_repo")
    async def test_handle_clone_repo_tool_failure(self, mock_clone):
        """Test failed clone-repo tool call."""
        mock_clone.return_value = {
            "success": False,
            "repo_url": "https://github.com/user/invalid.git",
            "error": "repository not found",
            "return_code": 128,
        }

        result = await handle_clone_repo_tool(
            arguments={"repo_url": "https://github.com/user/invalid.git"}
        )

        assert len(result) == 1
        assert result[0].type == "text"
        assert "✗" in result[0].text
        assert "failed" in result[0].text.lower()
        assert "not found" in result[0].text

    async def test_handle_clone_repo_tool_missing_url(self):
        """Test clone-repo tool without required repo_url."""
        result = await handle_clone_repo_tool(arguments={})

        assert len(result) == 1
        assert result[0].type == "text"
        assert "error" in result[0].text.lower()
        assert "required" in result[0].text.lower()


@pytest.mark.asyncio
class TestCleanup:
    """Test cleanup functionality."""

    @patch("shutil.rmtree")
    @patch("os.path.exists")
    def test_cleanup_cloned_repos(self, mock_exists, mock_rmtree):
        """Test that cleanup removes all cloned repos."""
        _cloned_repos.clear()
        _cloned_repos["https://github.com/user/repo1.git"] = "/tmp/repo1"
        _cloned_repos["https://github.com/user/repo2.git"] = "/tmp/repo2"
        
        mock_exists.return_value = True

        cleanup_cloned_repos()

        # Should have called rmtree for each repo
        assert mock_rmtree.call_count == 2
        
        # Repos dict should be cleared
        assert len(_cloned_repos) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
