"""Binary sensor platform for the FreeFall: lid state."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import FreeFall800ConfigEntry, FreeFall800Coordinator
from .entity import FreeFall800Entity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FreeFall800ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the lid switch binary sensor for a FreeFall config entry."""
    async_add_entities([FreeFall800LidSwitchSensor(entry.runtime_data)])


class FreeFall800LidSwitchSensor(FreeFall800Entity, BinarySensorEntity):
    """Whether the lid switch is currently open."""

    _attr_translation_key = "lid_switch"
    _attr_icon = "mdi:grill-outline"

    def __init__(self, coordinator: FreeFall800Coordinator) -> None:
        super().__init__(coordinator, "lid_switch")

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.lid_open
