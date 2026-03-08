"""Unit tests for services and events tools."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from appdaemon_mcp.tools.services import (
    ad_call_service,
    ad_fire_event,
    ad_list_services,
)


@pytest.fixture
def ctx():
    ctx = MagicMock()
    ctx.request_context.lifespan_context.client = AsyncMock()
    return ctx


async def test_ad_list_services(ctx):
    await ad_list_services(ctx)
    ctx.request_context.lifespan_context.client.get_services.assert_called_once()


async def test_ad_call_service(ctx):
    await ad_call_service(
        ctx,
        namespace="default",
        domain="light",
        service="turn_on",
        kwargs={"entity_id": "light.office"},
    )
    ctx.request_context.lifespan_context.client.call_service.assert_called_once_with(
        "default", "light", "turn_on", entity_id="light.office"
    )


async def test_ad_fire_event(ctx):
    await ad_fire_event(ctx, namespace="default", event="test_event", kwargs={"foo": "bar"})
    ctx.request_context.lifespan_context.client.fire_event.assert_called_once_with(
        "default", "test_event", foo="bar"
    )
