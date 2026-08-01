"""Button platform for the FreeFall 800: clearing the timer.

number entities always hold a numeric value - there's no UI-driven way to
send the device a null timer_duration_s. This button is the explicit action
for that, instead of overloading a sentinel value like 0 (which the device
would treat as an already-expired timer, not "no timer").
"""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import FreeFall800ConfigEntry, FreeFall800Coordinator
from .entity import FreeFall800Entity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FreeFall800ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the clear-timer button for a FreeFall 800 config entry."""
    async_add_entities([FreeFall800ClearTimerButton(entry.runtime_data)])


class FreeFall800ClearTimerButton(FreeFall800Entity, ButtonEntity):
    """Clears the cook timer."""

    _attr_translation_key = "timer_clear"
    _attr_icon = "mdi:timer-off"

    def __init__(self, coordinator: FreeFall800Coordinator) -> None:
        super().__init__(coordinator, "timer_clear")

    async def async_press(self) -> None:
        await self.coordinator.client.set_control({"timer_duration_s": None})
        await self.coordinator.async_request_refresh()
