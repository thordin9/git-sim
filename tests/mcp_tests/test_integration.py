"""Integration tests for git-sim MCP server with actual git-sim commands."""

import pytest
import tempfile
import shutil
from pathlib import Path
import subprocess

from git_sim_mcp.server import execute_git_sim, build_git_sim_command

pytestmark = pytest.mark.integration


@pytest.fixture
def temp_git_repo():
    """Create a temporary git repository for testing."""
    temp_dir = tempfile.mkdtemp()

    # Initialize git repo
    subprocess.run(["git", "init"], cwd=temp_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=temp_dir,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=temp_dir,
        check=True,
        capture_output=True,
    )

    # Create initial commit
    test_file = Path(temp_dir) / "test.txt"
    test_file.write_text("Initial content\n")
    subprocess.run(
        ["git", "add", "test.txt"], cwd=temp_dir, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=temp_dir,
        check=True,
        capture_output=True,
    )

    # Create a few more commits
    for i in range(3):
        test_file.write_text(f"Content {i+1}\n")
        subprocess.run(
            ["git", "add", "test.txt"], cwd=temp_dir, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", f"Commit {i+1}"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

    yield temp_dir

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.asyncio
@pytest.mark.skipif(shutil.which("git-sim") is None, reason="git-sim not installed")
class TestIntegration:
    """Integration tests with actual git-sim execution."""

    async def test_execute_log_command(self, temp_git_repo):
        """Test executing git-sim log command."""
        result = await execute_git_sim(
            command="log", repo_path=temp_git_repo, n=3, output_only_path=True
        )

        assert result["success"] is True
        assert result["return_code"] == 0

        # Check that media path is returned
        if result.get("media_path"):
            assert Path(result["media_path"]).exists()
            assert result["media_path"].endswith(".jpg") or result[
                "media_path"
            ].endswith(".png")

    async def test_execute_status_command(self, temp_git_repo):
        """Test executing git-sim status command."""
        # Create a modified file
        test_file = Path(temp_git_repo) / "test.txt"
        test_file.write_text("Modified content\n")

        result = await execute_git_sim(
            command="status", repo_path=temp_git_repo, output_only_path=True
        )

        assert result["success"] is True
        assert result["return_code"] == 0

    async def test_execute_branch_command(self, temp_git_repo):
        """Test executing git-sim branch command."""
        result = await execute_git_sim(
            command="branch",
            args=["new-feature"],
            repo_path=temp_git_repo,
            output_only_path=True,
        )

        assert result["success"] is True
        assert result["return_code"] == 0

    async def test_with_light_mode(self, temp_git_repo):
        """Test executing command with light mode."""
        result = await execute_git_sim(
            command="log",
            repo_path=temp_git_repo,
            n=2,
            light_mode=True,
            output_only_path=True,
        )

        assert result["success"] is True
        assert result["return_code"] == 0

    async def test_with_png_format(self, temp_git_repo):
        """Test executing command with PNG format."""
        result = await execute_git_sim(
            command="log",
            repo_path=temp_git_repo,
            n=2,
            img_format="png",
            output_only_path=True,
        )

        assert result["success"] is True
        if result.get("media_path"):
            assert result["media_path"].endswith(".png")

    async def test_error_handling_invalid_repo(self):
        """Test error handling with invalid repository path."""
        result = await execute_git_sim(
            command="log", repo_path="/nonexistent/path", output_only_path=True
        )

        # Should either fail or git-sim should handle it gracefully
        # We just check that we get a result
        assert "success" in result
        assert "return_code" in result


class TestCommandBuilding:
    """Test command building with various options."""

    def test_build_command_for_merge(self):
        """Test building merge command."""
        cmd = build_git_sim_command(
            command="merge", args=["feature-branch"], n=10, light_mode=True
        )

        assert "git-sim" in cmd
        assert "-n" in cmd
        assert "10" in cmd
        assert "--light-mode" in cmd
        assert "merge" in cmd
        assert "feature-branch" in cmd

    def test_build_command_for_rebase(self):
        """Test building rebase command."""
        cmd = build_git_sim_command(command="rebase", args=["main"], reverse=True)

        assert "git-sim" in cmd
        assert "--reverse" in cmd
        assert "rebase" in cmd
        assert "main" in cmd

    def test_build_animated_command(self):
        """Test building animated command."""
        cmd = build_git_sim_command(
            command="log", animate=True, low_quality=True, video_format="webm"
        )

        assert "--animate" in cmd
        assert "--low-quality" in cmd
        assert "--video-format" in cmd
        assert "webm" in cmd


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
