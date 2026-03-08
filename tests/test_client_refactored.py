"""Unit tests for refactored AppDaemonClient."""

import pytest
from aioresponses import aioresponses

from appdaemon_mcp.client import ADAuthError, ADNotFoundError, AppDaemonClient
from appdaemon_mcp.models import AppEntity, AppInfo, LogEntry

BASE_URL = "http://ad.local:5050"


@pytest.fixture
async def client():
    c = AppDaemonClient(base_url=BASE_URL, api_key="secret")
    await c.connect()
    yield c
    await c.disconnect()


async def test_get_info_returns_appinfo(client: AppDaemonClient):
    with aioresponses() as m:
        m.get(
            f"{BASE_URL}/api/appdaemon", payload={"data": {"version": "4.4.2", "timezone": "UTC"}}
        )
        result = await client.get_info()
    assert isinstance(result, AppInfo)
    assert result.version == "4.4.2"


async def test_get_state_returns_appentity(client: AppDaemonClient):
    with aioresponses() as m:
        m.get(
            f"{BASE_URL}/api/appdaemon/state/default/light.kitchen",
            payload={"data": {"state": "on", "entity_id": "light.kitchen"}},
        )
        result = await client.get_state("default", entity="light.kitchen")
    assert isinstance(result, AppEntity)
    assert result.state == "on"


async def test_get_logs_returns_logentries(client: AppDaemonClient):
    with aioresponses() as m:
        m.get(
            f"{BASE_URL}/api/appdaemon/logs",
            payload={"data": [{"ts": 1000.0, "type": "INFO", "message": "Test"}]},
        )
        result = await client.get_logs()
    assert isinstance(result, list)
    assert isinstance(result[0], LogEntry)
    assert result[0].message == "Test"


async def test_auth_error_raises_adautherror(client: AppDaemonClient):
    with aioresponses() as m:
        m.get(f"{BASE_URL}/api/appdaemon", status=401)
        with pytest.raises(ADAuthError):
            await client.get_info()


async def test_not_found_raises_adnotfounderror(client: AppDaemonClient):
    with aioresponses() as m:
        m.get(f"{BASE_URL}/api/appdaemon/state/default/missing", status=404)
        with pytest.raises(ADNotFoundError):
            await client.get_state("default", entity="missing")
