"""Smoke tests for MCP server - basic functionality checks."""

import subprocess
import sys
from pathlib import Path


def test_server_import():
    """Test that the server module can be imported."""
    result = subprocess.run(
        [sys.executable, "-c", "from git_sim_mcp import server; print('OK')"],
        cwd=Path(__file__).parent.parent.parent,
        env={"PYTHONPATH": str(Path(__file__).parent.parent.parent / "src")},
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Import failed: {result.stderr}"
    assert "OK" in result.stdout


def test_server_version():
    """Test that the server version can be retrieved."""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from git_sim_mcp import __version__; print(__version__)",
        ],
        cwd=Path(__file__).parent.parent.parent,
        env={"PYTHONPATH": str(Path(__file__).parent.parent.parent / "src")},
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Version check failed: {result.stderr}"
    assert "0.1.0" in result.stdout


def test_help_output():
    """Test that help output works."""
    result = subprocess.run(
        [sys.executable, "-m", "git_sim_mcp", "--help"],
        cwd=Path(__file__).parent.parent.parent,
        env={"PYTHONPATH": str(Path(__file__).parent.parent.parent / "src")},
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Help failed: {result.stderr}"
    assert "git-sim MCP Server" in result.stdout
    assert "--transport" in result.stdout


def test_version_output():
    """Test that version output works."""
    result = subprocess.run(
        [sys.executable, "-m", "git_sim_mcp", "--version"],
        cwd=Path(__file__).parent.parent.parent,
        env={"PYTHONPATH": str(Path(__file__).parent.parent.parent / "src")},
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Version output failed: {result.stderr}"
    assert "0.1.0" in result.stdout


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
