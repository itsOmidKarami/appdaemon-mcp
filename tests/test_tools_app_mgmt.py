"""Unit tests for app management tools."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from appdaemon_mcp.tools.apps import (
    ad_start_app,
    ad_stop_app,
    ad_restart_app,
    ad_enable_app,
    ad_disable_app,
    ad_reload_apps,
    ad_create_app,
    ad_remove_app,
    ad_get_app_info,
)


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


async def test_ad_enable_app(ctx):
    await ad_enable_app(ctx, app="test_app")
    ctx.request_context.lifespan_context.client.call_service.assert_called_once_with(
        "admin", "app", "enable", app="test_app"
    )


async def test_ad_disable_app(ctx):
    await ad_disable_app(ctx, app="test_app")
    ctx.request_context.lifespan_context.client.call_service.assert_called_once_with(
        "admin", "app", "disable", app="test_app"
    )


async def test_ad_reload_apps(ctx):
    await ad_reload_apps(ctx)
    ctx.request_context.lifespan_context.client.call_service.assert_called_once_with(
        "admin", "app", "reload"
    )


async def test_ad_create_app(ctx):
    await ad_create_app(ctx, app="new_app", module="m", class_name="C", args={"x": 1})
    ctx.request_context.lifespan_context.client.call_service.assert_called_once_with(
        "admin", "app", "create", app="new_app", module="m", **{"class": "C", "x": 1}
    )


async def test_ad_remove_app(ctx):
    await ad_remove_app(ctx, app="old_app")
    ctx.request_context.lifespan_context.client.call_service.assert_called_once_with(
        "admin", "app", "remove", app="old_app"
    )


async def test_ad_get_app_info(ctx):
    await ad_get_app_info(ctx, app="test_app")
    ctx.request_context.lifespan_context.client.get_state.assert_called_once_with(
        namespace="admin", entity="test_app"
    )
