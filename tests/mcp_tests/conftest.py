"""Pytest configuration for MCP tests."""

import pytest
import sys
from pathlib import Path

# Add src directory to path for imports
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (may require git-sim installed)"
    )
    config.addinivalue_line(
        "markers", "asyncio: mark test as async test"
    )
