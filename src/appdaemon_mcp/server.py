"""FastMCP server for AppDaemon.

Entry point:
    uv run appdaemon-mcp          (stdio, for IDE integrations)
    MCP_TRANSPORT=streamable-http uv run appdaemon-mcp

Environment variables:
    AD_URL          Required. AppDaemon base URL (e.g. http://192.168.1.20:5050)
    AD_API_KEY      Optional. API password (sent as x-ad-access header)
    AD_APPS_DIR     Optional. Path to apps/ directory (enables dev tools)
    AD_CONFIG_DIR   Optional. Path to AD config directory (enables config resources)
    AD_VERIFY_SSL   Optional. Verify SSL certs (default: true)
    MCP_TRANSPORT   Optional. Transport type: stdio (default) or streamable-http
"""

import logging
import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator

from mcp.server.fastmcp import FastMCP

from appdaemon_mcp.client import AppDaemonClient
from appdaemon_mcp.tools.core import (
    ad_get_entity,
    ad_get_info,
    ad_get_logs,
    ad_get_state,
    ad_list_apps,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan context — holds shared resources for the server lifetime
# ---------------------------------------------------------------------------


@dataclass
class AppContext:
    """Resources available to every MCP tool via ``ctx.request_context.lifespan_context``."""

    client: AppDaemonClient
    apps_dir: str | None
    config_dir: str | None


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Open / close the AppDaemon client around the server's lifetime."""
    ad_url = os.environ.get("AD_URL", "").strip()
    if not ad_url:
        raise RuntimeError(
            "AD_URL environment variable is required. "
            "Set it to your AppDaemon URL, e.g. http://192.168.1.20:5050"
        )

    verify_ssl_raw = os.environ.get("AD_VERIFY_SSL", "true").lower()
    verify_ssl = verify_ssl_raw not in ("false", "0", "no")

    client = AppDaemonClient(
        base_url=ad_url,
        api_key=os.environ.get("AD_API_KEY") or None,
        verify_ssl=verify_ssl,
    )

    logger.info("Connecting to AppDaemon at %s …", ad_url)
    await client.connect()
    logger.info("AppDaemon client connected.")

    try:
        yield AppContext(
            client=client,
            apps_dir=os.environ.get("AD_APPS_DIR") or None,
            config_dir=os.environ.get("AD_CONFIG_DIR") or None,
        )
    finally:
        await client.disconnect()
        logger.info("AppDaemon client disconnected.")


# ---------------------------------------------------------------------------
# FastMCP server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "AppDaemon",
    instructions=(
        "MCP server for observing and managing AppDaemon home-automation apps. "
        "Wraps the AppDaemon REST API so AI assistants can list apps, inspect "
        "entity state, read logs, call services, and (with filesystem access) "
        "read and write app code."
    ),
    lifespan=app_lifespan,
)

# ---------------------------------------------------------------------------
# Register tools
# ---------------------------------------------------------------------------

mcp.tool()(ad_get_info)
mcp.tool()(ad_list_apps)
mcp.tool()(ad_get_state)
mcp.tool()(ad_get_entity)
mcp.tool()(ad_get_logs)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the MCP server (called by the ``appdaemon-mcp`` CLI script)."""
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    logger.info("Starting AppDaemon MCP server (transport=%s)", transport)
    mcp.run(transport=transport)  # type: ignore[arg-type]


if __name__ == "__main__":
    main()
