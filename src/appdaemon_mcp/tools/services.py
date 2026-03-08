"""Services and events tools.

Tools:
    ad_list_services  — List available AppDaemon services
    ad_call_service   — Call an AppDaemon service
    ad_fire_event     — Fire an AppDaemon event
"""

import logging
from typing import Annotated, Any

from mcp.server.fastmcp import Context
from pydantic import Field

logger = logging.getLogger(__name__)


async def ad_list_services(ctx: Context) -> dict[str, Any]:
    """List all available AppDaemon services across all namespaces."""
    client = ctx.request_context.lifespan_context.client
    return await client.get_services()


async def ad_call_service(
    ctx: Context,
    namespace: Annotated[
        str, Field(description="The AppDaemon namespace (e.g. 'default', 'admin')")
    ],
    domain: Annotated[str, Field(description="The service domain (e.g. 'light', 'notify')")],
    service: Annotated[
        str, Field(description="The service name (e.g. 'turn_on', 'send_notification')")
    ],
    kwargs: Annotated[
        dict[str, Any] | None, Field(description="Optional service parameters")
    ] = None,
) -> dict[str, Any]:
    """Call an AppDaemon service."""
    client = ctx.request_context.lifespan_context.client
    return await client.call_service(namespace, domain, service, **(kwargs or {}))


async def ad_fire_event(
    ctx: Context,
    namespace: Annotated[str, Field(description="The AppDaemon namespace")],
    event: Annotated[str, Field(description="The event name to fire")],
    kwargs: Annotated[dict[str, Any] | None, Field(description="Optional event data")] = None,
) -> dict[str, Any]:
    """Fire an AppDaemon event."""
    client = ctx.request_context.lifespan_context.client
    return await client.fire_event(namespace, event, **(kwargs or {}))
