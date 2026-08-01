"""The FreeFall 800 integration."""

from __future__ import annotations

import logging

from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import FreeFall800Client, FreeFall800ConnectionError
from .coordinator import FreeFall800ConfigEntry, FreeFall800Coordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.CLIMATE,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SWITCH,
    Platform.BUTTON,
]


async def async_setup_entry(hass: HomeAssistant, entry: FreeFall800ConfigEntry) -> bool:
    """Set up FreeFall 800 from a config entry."""
    client = FreeFall800Client(
        async_get_clientsession(hass), entry.data[CONF_HOST], entry.data[CONF_PORT]
    )
    coordinator = FreeFall800Coordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()

    # Fetched once per setup/reload rather than on the coordinator's poll
    # loop - /api/config also returns the plaintext WiFi password, which
    # shouldn't be re-fetched every 10 seconds just to keep this current.
    try:
        config = await client.get_config()
    except FreeFall800ConnectionError:
        _LOGGER.warning("Could not fetch firmware version for %s", entry.title)
    else:
        coordinator.sw_version = config.get("version")

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: FreeFall800ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
