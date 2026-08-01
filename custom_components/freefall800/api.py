"""Thin HTTP client for the FreeFall 800's local REST API."""

from __future__ import annotations

from typing import Any

import aiohttp

from .const import REQUEST_TIMEOUT_SECONDS


class FreeFall800Error(Exception):
    """Base error for the FreeFall 800 client."""


class FreeFall800ConnectionError(FreeFall800Error):
    """Raised when the device can't be reached or returns an error."""


class FreeFall800Client:
    """Talks to a FreeFall 800's /api/status and /api/control endpoints."""

    def __init__(self, session: aiohttp.ClientSession, host: str, port: int) -> None:
        self._session = session
        self._base_url = f"http://{host}:{port}"
        self._timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SECONDS)

    async def get_status(self) -> dict[str, Any]:
        """Fetch /api/status (temps, fan, power, lid switch, timer remaining)."""
        return await self._get("/api/status")

    async def get_control(self) -> dict[str, Any]:
        """Fetch /api/control (current setpoints)."""
        return await self._get("/api/control")

    async def get_config(self) -> dict[str, Any]:
        """Fetch /api/config (calibration, WiFi, mac_address, build info)."""
        return await self._get("/api/config")

    async def set_control(self, payload: dict[str, Any]) -> None:
        """POST a partial update to /api/control.

        Fields omitted from payload are left untouched by the device;
        fields explicitly set to None clear that setpoint.
        """
        await self._post("/api/control", payload)

    async def _get(self, path: str) -> dict[str, Any]:
        try:
            async with self._session.get(
                f"{self._base_url}{path}", timeout=self._timeout
            ) as resp:
                resp.raise_for_status()
                return await resp.json(content_type=None)
        except (TimeoutError, aiohttp.ClientError) as err:
            raise FreeFall800ConnectionError(
                f"Error fetching {path} from {self._base_url}: {err}"
            ) from err

    async def _post(self, path: str, payload: dict[str, Any]) -> None:
        try:
            async with self._session.post(
                f"{self._base_url}{path}", json=payload, timeout=self._timeout
            ) as resp:
                resp.raise_for_status()
        except (TimeoutError, aiohttp.ClientError) as err:
            raise FreeFall800ConnectionError(
                f"Error posting {path} to {self._base_url}: {err}"
            ) from err
