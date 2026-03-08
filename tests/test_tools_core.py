"""Unit tests for core observation tools."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from mcp.server.fastmcp import Context

from appdaemon_mcp.models import AppEntity, AppInfo, LogEntry
from appdaemon_mcp.tools import core


@pytest.fixture
def mock_ctx():
    """Create a mock Context with a mocked AppDaemonClient."""
    ctx = MagicMock(spec=Context)
    client = AsyncMock()
    # Mock the lifespan context that our tools expect
    ctx.request_context.lifespan_context.client = client
    return ctx


async def test_ad_get_info(mock_ctx):
    info = AppInfo(version="4.4.2", timezone="UTC", latitude=0.0, longitude=0.0, elevation=0)
    mock_ctx.request_context.lifespan_context.client.get_info.return_value = info

    result = await core.ad_get_info(mock_ctx)

    assert result == info
    mock_ctx.request_context.lifespan_context.client.get_info.assert_called_once()


async def test_ad_get_state(mock_ctx):
    entities = {"light.test": AppEntity(state="on", attributes={})}
    mock_ctx.request_context.lifespan_context.client.get_state.return_value = entities

    result = await core.ad_get_state(mock_ctx, namespace="default")

    assert result == entities
    mock_ctx.request_context.lifespan_context.client.get_state.assert_called_once_with(
        namespace="default"
    )


async def test_ad_get_entity(mock_ctx):
    entity = AppEntity(state="on", attributes={})
    mock_ctx.request_context.lifespan_context.client.get_state.return_value = entity

    result = await core.ad_get_entity(mock_ctx, namespace="default", entity_id="light.test")

    assert result == entity
    mock_ctx.request_context.lifespan_context.client.get_state.assert_called_once_with(
        namespace="default", entity="light.test"
    )


async def test_ad_get_logs(mock_ctx):
    logs = [
        LogEntry(ts=1000, type="info", message="Log 1"),
        LogEntry(ts=2000, type="info", message="Log 2"),
    ]
    mock_ctx.request_context.lifespan_context.client.get_logs.return_value = logs

    # Test with limit
    result = await core.ad_get_logs(mock_ctx, limit=1)
    assert len(result) == 1
    assert result[0].message == "Log 1"

    # Test with limit 0 (all)
    result = await core.ad_get_logs(mock_ctx, limit=0)
    assert len(result) == 2
