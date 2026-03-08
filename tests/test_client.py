"""Unit tests for AppDaemonClient."""

import pytest
from aioresponses import aioresponses

from appdaemon_mcp.client import AppDaemonClient, AppDaemonError

BASE_URL = "http://ad.local:5050"


@pytest.fixture
async def client():
    c = AppDaemonClient(base_url=BASE_URL, api_key="secret", verify_ssl=False)
    await c.connect()
    yield c
    await c.disconnect()


# ---------------------------------------------------------------------------
# get_info
# ---------------------------------------------------------------------------


async def test_get_info_returns_data(client: AppDaemonClient):
    with aioresponses() as m:
        m.get(
            f"{BASE_URL}/api/appdaemon",
            payload={"data": {"version": "4.4.2", "timezone": "UTC"}},
        )
        result = await client.get_info()
    assert result.version == "4.4.2"


# ---------------------------------------------------------------------------
# get_namespaces
# ---------------------------------------------------------------------------


async def test_get_namespaces_list(client: AppDaemonClient):
    with aioresponses() as m:
        m.get(
            f"{BASE_URL}/api/appdaemon/state/",
            payload={"data": ["default", "admin"]},
        )
        result = await client.get_namespaces()
    assert "default" in result
    assert "admin" in result


# ---------------------------------------------------------------------------
# get_state — full namespace
# ---------------------------------------------------------------------------


async def test_get_state_namespace(client: AppDaemonClient):
    with aioresponses() as m:
        m.get(
            f"{BASE_URL}/api/appdaemon/state/default",
            payload={"data": {"light.kitchen": {"state": "on"}}},
        )
        result = await client.get_state("default")
    assert isinstance(result, dict)
    assert result["light.kitchen"].state == "on"


# ---------------------------------------------------------------------------
# get_state — single entity
# ---------------------------------------------------------------------------


async def test_get_state_entity(client: AppDaemonClient):
    with aioresponses() as m:
        m.get(
            f"{BASE_URL}/api/appdaemon/state/default/light.kitchen",
            payload={"data": {"state": "on", "attributes": {"brightness": 255}}},
        )
        result = await client.get_state("default", entity="light.kitchen")
    from appdaemon_mcp.models import AppEntity

    assert isinstance(result, AppEntity)
    assert result.state == "on"


# ---------------------------------------------------------------------------
# get_logs
# ---------------------------------------------------------------------------


async def test_get_logs_returns_list(client: AppDaemonClient):
    with aioresponses() as m:
        m.get(
            f"{BASE_URL}/api/appdaemon/logs",
            payload={"data": [{"ts": 1000, "type": "info", "message": "Started"}]},
        )
        result = await client.get_logs()
    assert isinstance(result, list)
    assert result[0].message == "Started"


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


async def test_http_error_raises_appdaemon_error(client: AppDaemonClient):
    with aioresponses() as m:
        m.get(f"{BASE_URL}/api/appdaemon", status=500, body="Error")
        with pytest.raises(AppDaemonError, match="500"):
            await client.get_info()


async def test_call_service(client: AppDaemonClient):
    with aioresponses() as m:
        m.post(
            f"{BASE_URL}/api/appdaemon/service/admin/app/restart",
            payload={"data": {"result": "ok"}},
        )
        result = await client.call_service("admin", "app", "restart", app="my_app")
    assert result["result"] == "ok"


async def test_fire_event(client: AppDaemonClient):
    with aioresponses() as m:
        m.post(
            f"{BASE_URL}/api/appdaemon/event/default/MY_EVENT",
            payload={"data": {"status": "fired"}},
        )
        result = await client.fire_event("default", "MY_EVENT", key="value")
    assert result["status"] == "fired"
