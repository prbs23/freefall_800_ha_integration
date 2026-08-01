"""Base entity for FreeFall 800 entities."""

from __future__ import annotations

from homeassistant.const import CONF_HOST, CONF_MAC, CONF_PORT
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import FreeFall800Coordinator


class FreeFall800Entity(CoordinatorEntity[FreeFall800Coordinator]):
    """Common device info for all FreeFall 800 entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: FreeFall800Coordinator, unique_id_suffix: str) -> None:
        super().__init__(coordinator)
        entry = coordinator.config_entry
        self._attr_unique_id = f"{entry.entry_id}_{unique_id_suffix}"
        host = entry.data[CONF_HOST]
        port = entry.data[CONF_PORT]
        mac = entry.data.get(CONF_MAC)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            connections={(CONNECTION_NETWORK_MAC, mac)} if mac else set(),
            name=entry.title,
            manufacturer=MANUFACTURER,
            model=MODEL,
            sw_version=coordinator.sw_version,
            configuration_url=f"http://{host}:{port}/",
        )
