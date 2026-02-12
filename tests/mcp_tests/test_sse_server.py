"""Tests for SSE server CORS configuration."""

import os
from unittest.mock import patch

from git_sim_mcp.sse_server import get_cors_config


class TestCORSConfiguration:
    """Test CORS configuration functionality."""

    def test_default_cors_config(self):
        """Test default CORS configuration."""
        with patch.dict(os.environ, {}, clear=True):
            config = get_cors_config()
            
            assert config["allow_origins"] == ["*"]
            assert config["allow_methods"] == ["GET", "POST", "OPTIONS"]
            assert config["allow_headers"] == ["*"]
            assert config["allow_credentials"] is False

    def test_accept_all_cors_mode(self):
        """Test accept-all CORS mode with GIT_SIM_CORS_ACCEPT_ALL."""
        with patch.dict(os.environ, {"GIT_SIM_CORS_ACCEPT_ALL": "true"}):
            config = get_cors_config()
            
            assert config["allow_origins"] == ["*"]
            assert config["allow_methods"] == ["*"]
            assert config["allow_headers"] == ["*"]
            assert config["allow_credentials"] is False

    def test_accept_all_cors_mode_with_1(self):
        """Test accept-all CORS mode with value '1'."""
        with patch.dict(os.environ, {"GIT_SIM_CORS_ACCEPT_ALL": "1"}):
            config = get_cors_config()
            
            assert config["allow_origins"] == ["*"]
            assert config["allow_methods"] == ["*"]
            assert config["allow_headers"] == ["*"]

    def test_accept_all_cors_mode_with_yes(self):
        """Test accept-all CORS mode with value 'yes'."""
        with patch.dict(os.environ, {"GIT_SIM_CORS_ACCEPT_ALL": "yes"}):
            config = get_cors_config()
            
            assert config["allow_origins"] == ["*"]
            assert config["allow_methods"] == ["*"]

    def test_accept_all_overrides_individual_settings(self):
        """Test that accept-all mode overrides individual CORS settings."""
        with patch.dict(os.environ, {
            "GIT_SIM_CORS_ACCEPT_ALL": "true",
            "GIT_SIM_CORS_ALLOW_ORIGINS": "https://example.com",
            "GIT_SIM_CORS_ALLOW_METHODS": "GET",
            "GIT_SIM_CORS_ALLOW_HEADERS": "Content-Type",
            "GIT_SIM_CORS_ALLOW_CREDENTIALS": "true",
        }):
            config = get_cors_config()
            
            # Accept-all should override all individual settings
            assert config["allow_origins"] == ["*"]
            assert config["allow_methods"] == ["*"]
            assert config["allow_headers"] == ["*"]
            assert config["allow_credentials"] is False

    def test_custom_cors_config_without_accept_all(self):
        """Test custom CORS configuration when accept-all is not set."""
        with patch.dict(os.environ, {
            "GIT_SIM_CORS_ALLOW_ORIGINS": "https://example.com,https://app.example.com",
            "GIT_SIM_CORS_ALLOW_METHODS": "GET,POST",
            "GIT_SIM_CORS_ALLOW_HEADERS": "Content-Type,Authorization",
            "GIT_SIM_CORS_ALLOW_CREDENTIALS": "true",
        }):
            config = get_cors_config()
            
            assert config["allow_origins"] == ["https://example.com", "https://app.example.com"]
            assert config["allow_methods"] == ["GET", "POST"]
            assert config["allow_headers"] == ["Content-Type", "Authorization"]
            assert config["allow_credentials"] is True

    def test_accept_all_false_uses_individual_settings(self):
        """Test that accept-all=false uses individual settings."""
        with patch.dict(os.environ, {
            "GIT_SIM_CORS_ACCEPT_ALL": "false",
            "GIT_SIM_CORS_ALLOW_ORIGINS": "https://example.com",
        }):
            config = get_cors_config()
            
            # Should use individual settings, not accept-all
            assert config["allow_origins"] == ["https://example.com"]

    def test_single_origin(self):
        """Test CORS config with a single origin."""
        with patch.dict(os.environ, {
            "GIT_SIM_CORS_ALLOW_ORIGINS": "https://example.com",
        }):
            config = get_cors_config()
            
            assert config["allow_origins"] == ["https://example.com"]

    def test_wildcard_origin(self):
        """Test CORS config with wildcard origin."""
        with patch.dict(os.environ, {
            "GIT_SIM_CORS_ALLOW_ORIGINS": "*",
        }):
            config = get_cors_config()
            
            assert config["allow_origins"] == ["*"]


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
