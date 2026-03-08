"""App management tools.

Tools:
    ad_list_apps      — List all apps with their status
    ad_start_app      — Start a stopped app
    ad_stop_app       — Stop a running app
    ad_restart_app    — Restart a running app
    ad_enable_app     — Enable a disabled app
    ad_disable_app    — Disable a running app
    ad_reload_apps    — Reload all AppDaemon apps from disk
"""

import logging
from typing import Annotated, Any
from pydantic import Field
from mcp.server.fastmcp import Context
from ..models import AppEntity

logger = logging.getLogger(__name__)


async def ad_list_apps(ctx: Context) -> dict[str, AppEntity]:
    """List all AppDaemon apps with their current status.

    Returns a mapping of app names to their current state and attributes.
    """
    client = ctx.request_context.lifespan_context.client
    return await client.get_state(namespace="admin")


async def ad_start_app(
    ctx: Context,
    app: Annotated[str, Field(description="The name of the app to start")]
) -> dict[str, Any]:
    """Start a stopped AppDaemon app."""
    client = ctx.request_context.lifespan_context.client
    return await client.call_service("admin", "app", "start", app=app)


async def ad_stop_app(
    ctx: Context,
    app: Annotated[str, Field(description="The name of the app to stop")]
) -> dict[str, Any]:
    """Stop a running AppDaemon app."""
    client = ctx.request_context.lifespan_context.client
    return await client.call_service("admin", "app", "stop", app=app)


async def ad_restart_app(
    ctx: Context,
    app: Annotated[str, Field(description="The name of the app to restart")]
) -> dict[str, Any]:
    """Restart an AppDaemon app."""
    client = ctx.request_context.lifespan_context.client
    return await client.call_service("admin", "app", "restart", app=app)


async def ad_enable_app(
    ctx: Context,
    app: Annotated[str, Field(description="The name of the app to enable")]
) -> dict[str, Any]:
    """Enable a disabled AppDaemon app."""
    client = ctx.request_context.lifespan_context.client
    return await client.call_service("admin", "app", "enable", app=app)


async def ad_disable_app(
    ctx: Context,
    app: Annotated[str, Field(description="The name of the app to disable")]
) -> dict[str, Any]:
    """Disable a running AppDaemon app."""
    client = ctx.request_context.lifespan_context.client
    return await client.call_service("admin", "app", "disable", app=app)


async def ad_reload_apps(ctx: Context) -> dict[str, Any]:
    """Reload all AppDaemon apps from disk.

    This triggers a full reload of all app configurations and Python modules.
    """
    client = ctx.request_context.lifespan_context.client
    return await client.call_service("admin", "app", "reload")
