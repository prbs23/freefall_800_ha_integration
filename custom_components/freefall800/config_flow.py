"""Config flow for the FreeFall 800 integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_MAC, CONF_PORT
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import format_mac

from .api import FreeFall800Client, FreeFall800ConnectionError
from .const import DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): vol.Coerce(int),
    }
)


class FreeFall800ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for FreeFall 800."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask for the device's host/IP and verify it's reachable."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]

            client = FreeFall800Client(async_get_clientsession(self.hass), host, port)
            try:
                await client.get_status()
                config = await client.get_config()
            except FreeFall800ConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error validating FreeFall 800 connection")
                errors["base"] = "unknown"
            else:
                mac = format_mac(config["mac_address"])
                await self.async_set_unique_id(mac)
                # Same device (MAC) re-added at a new IP: update the
                # existing entry's host/port instead of creating a duplicate.
                self._abort_if_unique_id_configured(updates={CONF_HOST: host, CONF_PORT: port})
                return self.async_create_entry(
                    title=f"FreeFall 800 ({host})",
                    data={CONF_HOST: host, CONF_PORT: port, CONF_MAC: mac},
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
