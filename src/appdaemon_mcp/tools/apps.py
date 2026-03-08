"""App management tools.

Tools:
    ad_list_apps      — List all apps with their status
    ad_get_app_info   — Detailed status for a single app
    ad_start_app      — Start a stopped app
    ad_stop_app       — Stop a running app
    ad_restart_app    — Restart a running app
    ad_enable_app     — Enable a disabled app
    ad_disable_app    — Disable a running app
    ad_reload_apps    — Reload all AppDaemon apps from disk
    ad_create_app     — Create a new AppDaemon app
    ad_remove_app     — Remove an existing AppDaemon app
"""

import logging
from typing import Annotated, Any

from mcp.server.fastmcp import Context
from pydantic import Field

from ..models import AppEntity

logger = logging.getLogger(__name__)


async def ad_list_apps(ctx: Context) -> dict[str, AppEntity]:
    """List all AppDaemon apps with their current status.

    Returns a mapping of app names to their current state and attributes.
    """
    client = ctx.request_context.lifespan_context.client
    return await client.get_state(namespace="admin")


async def ad_get_app_info(
    ctx: Context, app: Annotated[str, Field(description="The name of the app to query")]
) -> AppEntity:
    """Get detailed status and configuration for a single AppDaemon app."""
    client = ctx.request_context.lifespan_context.client
    return await client.get_state(namespace="admin", entity=app)


async def ad_start_app(
    ctx: Context, app: Annotated[str, Field(description="The name of the app to start")]
) -> dict[str, Any]:
    """Start a stopped AppDaemon app."""
    client = ctx.request_context.lifespan_context.client
    return await client.call_service("admin", "app", "start", app=app)


async def ad_stop_app(
    ctx: Context, app: Annotated[str, Field(description="The name of the app to stop")]
) -> dict[str, Any]:
    """Stop a running AppDaemon app."""
    client = ctx.request_context.lifespan_context.client
    return await client.call_service("admin", "app", "stop", app=app)


async def ad_restart_app(
    ctx: Context, app: Annotated[str, Field(description="The name of the app to restart")]
) -> dict[str, Any]:
    """Restart an AppDaemon app."""
    client = ctx.request_context.lifespan_context.client
    return await client.call_service("admin", "app", "restart", app=app)


async def ad_enable_app(
    ctx: Context, app: Annotated[str, Field(description="The name of the app to enable")]
) -> dict[str, Any]:
    """Enable a disabled AppDaemon app."""
    client = ctx.request_context.lifespan_context.client
    return await client.call_service("admin", "app", "enable", app=app)


async def ad_disable_app(
    ctx: Context, app: Annotated[str, Field(description="The name of the app to disable")]
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


async def ad_create_app(
    ctx: Context,
    app: Annotated[str, Field(description="The name of the app to create")],
    module: Annotated[str, Field(description="The Python module name (e.g. 'hello')")],
    class_name: Annotated[str, Field(description="The class name (e.g. 'HelloWorld')")],
    args: Annotated[dict[str, Any] | None, Field(description="Optional app arguments")] = None,
) -> dict[str, Any]:
    """Create a new AppDaemon app.

    Note: This creates the app configuration. The Python module must already exist
    in the apps directory unless file-based dev tools are used.
    """
    client = ctx.request_context.lifespan_context.client
    service_args = {"app": app, "module": module, "class": class_name}
    if args:
        service_args.update(args)
    return await client.call_service("admin", "app", "create", **service_args)


async def ad_remove_app(
    ctx: Context, app: Annotated[str, Field(description="The name of the app to remove")]
) -> dict[str, Any]:
    """Remove an AppDaemon app."""
    client = ctx.request_context.lifespan_context.client
    return await client.call_service("admin", "app", "remove", app=app)
