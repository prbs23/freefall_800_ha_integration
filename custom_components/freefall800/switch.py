"""Switch platform for the FreeFall 800's master power."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DEFAULT_PROBE_TARGET_TEMP_C, NUM_PROBES
from .coordinator import FreeFall800ConfigEntry, FreeFall800Coordinator
from .entity import FreeFall800Entity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FreeFall800ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switches for a FreeFall 800 config entry."""
    coordinator = entry.runtime_data
    entities: list[SwitchEntity] = [FreeFall800PowerSwitch(coordinator)]
    entities += [FreeFall800ProbeAlarmSwitch(coordinator, index) for index in range(NUM_PROBES)]
    async_add_entities(entities)


class FreeFall800PowerSwitch(FreeFall800Entity, SwitchEntity):
    """Master power - independent of heat, which climate.py tracks separately."""

    _attr_translation_key = "power"
    _attr_icon = "mdi:power"

    def __init__(self, coordinator: FreeFall800Coordinator) -> None:
        super().__init__(coordinator, "power")

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.power_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.client.set_control({"power_on": True})
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.client.set_control({"power_on": False})
        await self.coordinator.async_request_refresh()


class FreeFall800ProbeAlarmSwitch(FreeFall800Entity, SwitchEntity):
    """Whether a meat probe's alarm target is armed.

    The device has no separate armed/disarmed flag for this - probe_set_temp_c
    being null *is* disarmed. Arming with no prior target sends the same
    default the device's own front panel uses (100F/40C, see ui_state.rs).
    """

    _attr_icon = "mdi:thermometer-alert"

    def __init__(self, coordinator: FreeFall800Coordinator, index: int) -> None:
        super().__init__(coordinator, f"probe_{index}_alarm")
        self._index = index
        self._attr_translation_key = "probe_alarm"
        self._attr_translation_placeholders = {"index": str(index + 1)}

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.probe_set_temp_c[self._index] is not None

    async def async_turn_on(self, **kwargs: Any) -> None:
        if self.coordinator.data.probe_set_temp_c[self._index] is None:
            await self.coordinator.client.set_control(
                {"probe_set_temp_c": {str(self._index): DEFAULT_PROBE_TARGET_TEMP_C}}
            )
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.client.set_control({"probe_set_temp_c": {str(self._index): None}})
        await self.coordinator.async_request_refresh()
