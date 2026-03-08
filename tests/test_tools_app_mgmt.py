"""Unit tests for app management tools."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from appdaemon_mcp.tools.apps import ad_start_app, ad_stop_app, ad_restart_app

@pytest.fixture
def ctx():
    ctx = MagicMock()
    ctx.request_context.lifespan_context.client = AsyncMock()
    return ctx

async def test_ad_start_app(ctx):
    await ad_start_app(ctx, app="test_app")
    ctx.request_context.lifespan_context.client.call_service.assert_called_once_with(
        "admin", "app", "start", app="test_app"
    )

async def test_ad_stop_app(ctx):
    await ad_stop_app(ctx, app="test_app")
    ctx.request_context.lifespan_context.client.call_service.assert_called_once_with(
        "admin", "app", "stop", app="test_app"
    )

async def test_ad_restart_app(ctx):
    await ad_restart_app(ctx, app="test_app")
    ctx.request_context.lifespan_context.client.call_service.assert_called_once_with(
        "admin", "app", "restart", app="test_app"
    )
