"""AppDaemon REST API async client."""

import logging
from typing import Any

import aiohttp
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .models import AppEntity, AppInfo, LogEntry

logger = logging.getLogger(__name__)


class AppDaemonError(Exception):
    """Base exception for AppDaemon client errors."""


class ADAuthError(AppDaemonError):
    """Raised when authentication fails (401/403)."""


class ADConnectionError(AppDaemonError):
    """Raised when the client cannot connect to AppDaemon."""


class ADServerError(AppDaemonError):
    """Raised when AppDaemon returns a 5xx error."""


class ADNotFoundError(AppDaemonError):
    """Raised when a requested resource is not found (404)."""


class AppDaemonClient:
    """Async client for the AppDaemon REST API.

    Args:
        base_url: Base URL of the AppDaemon instance, e.g. ``http://192.168.1.20:5050``.
        api_key:  Optional API password (sent as ``x-ad-access`` header).
        verify_ssl: Whether to verify SSL certificates (default: True).
    """

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        verify_ssl: bool = True,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.verify_ssl = verify_ssl
        self._session: aiohttp.ClientSession | None = None

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    async def connect(self) -> None:
        """Create the underlying aiohttp session."""
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(ssl=self.verify_ssl)
            self._session = aiohttp.ClientSession(
                connector=connector,
                headers=self._auth_headers(),
            )
            logger.debug("AppDaemonClient: session opened → %s", self.base_url)

    async def disconnect(self) -> None:
        """Close the underlying aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
            logger.debug("AppDaemonClient: session closed")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _auth_headers(self) -> dict[str, str]:
        if self.api_key:
            return {"x-ad-access": self.api_key}
        return {}

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    @retry(
        retry=retry_if_exception_type(
            (
                aiohttp.ClientConnectorError,
                aiohttp.ServerDisconnectedError,
                aiohttp.ClientOSError,
                ADServerError,
            )
        ),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        before_sleep=lambda retry_state: logger.warning(
            "Retrying AppDaemon request (attempt %s) after error: %s",
            retry_state.attempt_number,
            retry_state.outcome.exception(),
        ),
        reraise=True,
    )
    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Make an HTTP request and return the parsed JSON body.

        Raises:
            ADAuthError: If 401 or 403 is returned.
            ADNotFoundError: If 404 is returned.
            AppDaemonError: If other 4xx status is returned.
            ADConnectionError: If a connection error occurs or 5xx after retries.
            RuntimeError: If the client session has not been opened yet.
        """
        if self._session is None or self._session.closed:
            raise RuntimeError("Client session is not open. Call connect() first.")

        url = self._url(path)
        logger.debug("%s %s  params=%s  body=%s", method, url, params, json)

        try:
            async with self._session.request(method, url, json=json, params=params) as resp:
                if resp.status in (401, 403):
                    text = await resp.text()
                    raise ADAuthError(f"Authentication failed ({resp.status}): {text}")
                if resp.status == 404:
                    text = await resp.text()
                    raise ADNotFoundError(f"Resource not found: {path}")
                if resp.status >= 500:
                    text = await resp.text()
                    raise ADServerError(f"AppDaemon Server Error {resp.status}: {text}")
                if resp.status >= 400:
                    text = await resp.text()
                    raise AppDaemonError(
                        f"AppDaemon API error {resp.status} for {method} {url}: {text}"
                    )
                data = await resp.json(content_type=None)
        except (aiohttp.ClientConnectorError, aiohttp.ClientOSError) as exc:
            raise ADConnectionError(f"Could not connect to AppDaemon at {url}") from exc

        # AppDaemon typically wraps responses in {"data": ...} or {"state": ...} or {"logs": ...}
        if isinstance(data, dict):
            if "data" in data:
                return data["data"]
            if "state" in data:
                return data["state"]
            if "logs" in data:
                return data["logs"]
        return data

    # ------------------------------------------------------------------
    # System info
    # ------------------------------------------------------------------

    async def get_info(self) -> AppInfo:
        """Return AppDaemon system overview (GET /api/appdaemon)."""
        data = await self._request("GET", "/api/appdaemon")
        return AppInfo.model_validate(data)

    # ------------------------------------------------------------------
    # State / namespaces
    # ------------------------------------------------------------------

    async def get_namespaces(self) -> list[str]:
        """Return all available namespaces (GET /api/appdaemon/state/)."""
        result = await self._request("GET", "/api/appdaemon/state/")
        if isinstance(result, list):
            return result
        # Some versions return a dict; pick sensible keys
        return list(result.keys()) if isinstance(result, dict) else []

    async def get_state(
        self,
        namespace: str = "default",
        entity: str | None = None,
    ) -> AppEntity | dict[str, AppEntity]:
        """Return state for an entire namespace or a single entity.

        Args:
            namespace: The AD namespace (e.g. ``"default"``, ``"admin"``).
            entity:    Optional entity ID to narrow the result.
        """
        if entity:
            path = f"/api/appdaemon/state/{namespace}/{entity}"
            data = await self._request("GET", path)
            return AppEntity.model_validate(data)
        else:
            path = f"/api/appdaemon/state/{namespace}"
            data = await self._request("GET", path)
            if not isinstance(data, dict):
                return {}
            return {eid: AppEntity.model_validate(val) for eid, val in data.items()}

    # ------------------------------------------------------------------
    # Services
    # ------------------------------------------------------------------

    async def get_services(self) -> dict[str, Any]:
        """Return available services (GET /api/appdaemon/service/)."""
        return await self._request("GET", "/api/appdaemon/service/")

    async def call_service(
        self,
        namespace: str,
        domain: str,
        service: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Call an AppDaemon service.

        Args:
            namespace: The AD namespace (e.g. ``"admin"``).
            domain:    Service domain (e.g. ``"app"``).
            service:   Service name (e.g. ``"start"``).
            **kwargs:  Additional service parameters sent as JSON body.
        """
        path = f"/api/appdaemon/service/{namespace}/{domain}/{service}"
        return await self._request("POST", path, json=kwargs or None)

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    async def fire_event(
        self,
        namespace: str,
        event: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Fire an AppDaemon event.

        Args:
            namespace: The AD namespace.
            event:     Event name.
            **kwargs:  Optional event data sent as JSON body.
        """
        path = f"/api/appdaemon/event/{namespace}/{event}"
        return await self._request("POST", path, json=kwargs or None)

    # ------------------------------------------------------------------
    # Logs
    # ------------------------------------------------------------------

    async def get_logs(self) -> list[LogEntry]:
        """Return recent AppDaemon logs (GET /api/appdaemon/logs)."""
        result = await self._request("GET", "/api/appdaemon/logs")
        if isinstance(result, list):
            return [LogEntry.model_validate(entry) for entry in result]
        # Wrap in list if a single dict is returned
        if isinstance(result, dict):
            return [LogEntry.model_validate(result)]
        return []

    # ------------------------------------------------------------------
    # Custom app endpoints
    # ------------------------------------------------------------------

    async def call_endpoint(
        self,
        endpoint: str,
        method: str = "GET",
        data: dict[str, Any] | None = None,
    ) -> Any:
        """Call a custom app endpoint.

        Args:
            endpoint: Endpoint name as registered by the app.
            method:   HTTP method (``"GET"`` or ``"POST"``).
            data:     Optional JSON body for POST requests.
        """
        path = f"/api/appdaemon/{endpoint}"
        return await self._request(method.upper(), path, json=data)
