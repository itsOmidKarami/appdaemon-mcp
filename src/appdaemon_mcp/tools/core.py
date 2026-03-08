"""Core observation tools.

Tools:
    ad_get_info       — AppDaemon system information
    ad_list_apps      — List all apps with their status
    ad_get_state      — State for an entire namespace
    ad_get_entity     — State for a single entity
    ad_get_logs       — Recent AppDaemon log entries
"""

import logging
from typing import Annotated, Any

from pydantic import Field

from mcp.server.fastmcp import Context

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool: ad_get_info
# ---------------------------------------------------------------------------


async def ad_get_info(ctx: Context) -> dict[str, Any]:
    """Return AppDaemon system information.

    Retrieves the AppDaemon version, timezone, latitude/longitude, and other
    runtime metadata from the ``GET /api/appdaemon`` endpoint.
    """
    client = ctx.request_context.lifespan_context.client
    return await client.get_info()


# ---------------------------------------------------------------------------
# Tool: ad_list_apps
# ---------------------------------------------------------------------------


async def ad_list_apps(ctx: Context) -> dict[str, Any]:
    """List all AppDaemon apps with their current status.

    Queries ``GET /api/appdaemon/state/admin/`` which holds one entity per
    app.  Each entity includes ``state`` (running/stopped/disabled) and the
    app's configuration attributes.
    """
    client = ctx.request_context.lifespan_context.client
    return await client.get_state(namespace="admin")


# ---------------------------------------------------------------------------
# Tool: ad_get_state
# ---------------------------------------------------------------------------


async def ad_get_state(
    ctx: Context,
    namespace: Annotated[
        str, Field(description="The AppDaemon namespace to query (e.g. 'default')")
    ] = "default",
) -> dict[str, Any]:
    """Return all entity state within an AppDaemon namespace.

    Args:
        namespace: The namespace to query.  Common values are ``"default"``
                   (Home Assistant mirror) and ``"admin"`` (AD apps).
                   Defaults to ``"default"``.
    """
    client = ctx.request_context.lifespan_context.client
    return await client.get_state(namespace=namespace)


# ---------------------------------------------------------------------------
# Tool: ad_get_entity
# ---------------------------------------------------------------------------


async def ad_get_entity(
    ctx: Context,
    namespace: Annotated[str, Field(description="The AppDaemon namespace the entity belongs to")],
    entity_id: Annotated[
        str, Field(description="The entity ID to look up (e.g. 'light.living_room')")
    ],
) -> dict[str, Any]:
    """Return the state of a single entity in an AppDaemon namespace.

    Args:
        namespace: The namespace that owns the entity.
        entity_id: The entity identifier (e.g. ``"light.living_room"``).
    """
    client = ctx.request_context.lifespan_context.client
    return await client.get_state(namespace=namespace, entity=entity_id)


# ---------------------------------------------------------------------------
# Tool: ad_get_logs
# ---------------------------------------------------------------------------


async def ad_get_logs(
    ctx: Context,
    limit: Annotated[
        int, Field(description="Maximum number of log entries to return (0 = all)")
    ] = 100,
) -> list[dict[str, Any]]:
    """Retrieve recent AppDaemon log entries.

    Args:
        limit: How many entries to return, newest first.  Pass ``0`` to
               return all available entries.  Defaults to ``100``.
    """
    client = ctx.request_context.lifespan_context.client
    logs = await client.get_logs()
    if limit > 0:
        logs = logs[:limit]
    return logs
