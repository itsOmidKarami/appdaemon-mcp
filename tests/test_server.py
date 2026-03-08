"""Unit tests for the MCP server entry point and lifespan."""

import os
from unittest.mock import AsyncMock, patch

import pytest
from mcp.server.fastmcp import FastMCP

from appdaemon_mcp.server import lifespan


@pytest.mark.asyncio
async def test_lifespan_success():
    """Test successful lifespan setup and teardown."""
    server = FastMCP("Test")

    with patch.dict(os.environ, {"AD_URL": "http://ad.local:5050", "AD_API_KEY": "secret"}):
        with patch("appdaemon_mcp.server.AppDaemonClient") as mock_client_class:
            mock_client_instance = mock_client_class.return_value
            mock_client_instance.connect = AsyncMock()
            mock_client_instance.disconnect = AsyncMock()

            async with lifespan(server) as context:
                assert context.client == mock_client_instance
                mock_client_instance.connect.assert_called_once()

            mock_client_instance.disconnect.assert_called_once()


@pytest.mark.asyncio
async def test_lifespan_no_url():
    """Test lifespan failure when AD_URL is missing."""
    server = FastMCP("Test")

    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(RuntimeError, match="AD_URL"):
            async with lifespan(server):
                pass


def test_main():
    """Test the main entry point function."""
    from appdaemon_mcp.server import main

    with patch("appdaemon_mcp.server.mcp.run") as mock_run:
        with patch.dict(os.environ, {"MCP_TRANSPORT": "stdio"}):
            main()
            mock_run.assert_called_once_with(transport="stdio")

        mock_run.reset_mock()
        with patch.dict(os.environ, {"MCP_TRANSPORT": "streamable-http"}):
            main()
            mock_run.assert_called_once_with(transport="streamable-http")
