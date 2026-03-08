"""FastMCP server for AppDaemon.

Entry point:
    uv run appdaemon-mcp          (stdio, for IDE integrations)
    MCP_TRANSPORT=streamable-http uv run appdaemon-mcp

Environment variables:
    AD_URL          Required. AppDaemon base URL (e.g. http://192.168.1.20:5050)
    AD_API_KEY      Optional. API password (x-ad-access header)
    MCP_TRANSPORT   Optional. "stdio" (default) or "streamable-http"
"""

import logging
import os
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP

from .client import AppDaemonClient
from .tools import core, apps

# ---------------------------------------------------------------------------
# Logging & Server Configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("appdaemon_mcp")

mcp = FastMCP("AppDaemon")


class LifespanContext:
    """Stores shared resources for the server lifecycle."""

    def __init__(self, client: AppDaemonClient) -> None:
        self.client = client


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncGenerator[LifespanContext, None]:
    """Manages the lifecycle of the AppDaemon client session."""
    url = os.environ.get("AD_URL")
    if not url:
        logger.error("AD_URL environment variable is not set")
        sys.exit(1)

    key = os.environ.get("AD_API_KEY")
    client = AppDaemonClient(base_url=url, api_key=key)

    try:
        await client.connect()
        yield LifespanContext(client=client)
    finally:
        await client.disconnect()


# Configure the lifespan handler
mcp.lifespan = lifespan


# ---------------------------------------------------------------------------
# Register Tools
# ---------------------------------------------------------------------------

# Register Core Observation Tools
mcp.tool(name="ad_get_info")(core.ad_get_info)
mcp.tool(name="ad_get_state")(core.ad_get_state)
mcp.tool(name="ad_get_entity")(core.ad_get_entity)
mcp.tool(name="ad_get_logs")(core.ad_get_logs)

# Register App Management Tools
mcp.tool(name="ad_list_apps")(apps.ad_list_apps)
mcp.tool(name="ad_get_app_info")(apps.ad_get_app_info)
mcp.tool(name="ad_start_app")(apps.ad_start_app)
mcp.tool(name="ad_stop_app")(apps.ad_stop_app)
mcp.tool(name="ad_restart_app")(apps.ad_restart_app)
mcp.tool(name="ad_enable_app")(apps.ad_enable_app)
mcp.tool(name="ad_disable_app")(apps.ad_disable_app)
mcp.tool(name="ad_reload_apps")(apps.ad_reload_apps)
mcp.tool(name="ad_create_app")(apps.ad_create_app)
mcp.tool(name="ad_remove_app")(apps.ad_remove_app)


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the MCP server."""
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    logger.info("Starting AppDaemon MCP server (transport=%s)", transport)
    mcp.run(transport=transport)  # type: ignore[arg-type]


if __name__ == "__main__":
    main()
