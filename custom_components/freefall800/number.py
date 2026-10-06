"""Number platform for the FreeFall: probe alarm targets and cook timer."""

from __future__ import annotations

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.const import UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import MAX_TARGET_TEMP_C, MAX_TIMER_SECONDS, MIN_TARGET_TEMP_C, NUM_PROBES
from .coordinator import FreeFall800ConfigEntry, FreeFall800Coordinator
from .entity import FreeFall800Entity

TIMER_STEP_MINUTES = 1
MAX_TIMER_MINUTES = MAX_TIMER_SECONDS // 60


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FreeFall800ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up numbers for a FreeFall config entry."""
    coordinator = entry.runtime_data
    entities: list[NumberEntity] = [
        FreeFall800ProbeTargetNumber(coordinator, index) for index in range(NUM_PROBES)
    ]
    entities.append(FreeFall800TimerNumber(coordinator))
    async_add_entities(entities)


class FreeFall800ProbeTargetNumber(FreeFall800Entity, NumberEntity):
    """Alarm/target temperature for a single meat probe."""

    _attr_device_class = NumberDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_native_min_value = MIN_TARGET_TEMP_C
    _attr_native_max_value = MAX_TARGET_TEMP_C
    _attr_native_step = 1
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator: FreeFall800Coordinator, index: int) -> None:
        super().__init__(coordinator, f"probe_{index}_target")
        self._index = index
        self._attr_translation_key = "probe_target"
        self._attr_translation_placeholders = {"index": str(index + 1)}

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.probe_set_temp_c[self._index]

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.client.set_control(
            {"probe_set_temp_c": {str(self._index): value}}
        )
        await self.coordinator.async_request_refresh()


class FreeFall800TimerNumber(FreeFall800Entity, NumberEntity):
    """Cook timer duration, set in minutes for convenience."""

    _attr_translation_key = "timer_duration"
    _attr_device_class = NumberDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_native_min_value = 0
    _attr_native_max_value = MAX_TIMER_MINUTES
    _attr_native_step = TIMER_STEP_MINUTES
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator: FreeFall800Coordinator) -> None:
        super().__init__(coordinator, "timer_duration")

    @property
    def native_value(self) -> float | None:
        duration_s = self.coordinator.data.timer_duration_s
        return None if duration_s is None else duration_s // 60

    async def async_set_native_value(self, value: float) -> None:
        # number entities can't send null (HA's number.set_value schema
        # requires a float), and a literal 0s duration would immediately
        # trip the device's timer alarm rather than clear it (see
        # ui_state.rs's elapsed >= timer_dur check) - so 0 means "cancel"
        # here, sent as timer_duration_s: null instead of a real 0.
        duration_s = int(value) * 60 or None
        await self.coordinator.client.set_control({"timer_duration_s": duration_s})
        await self.coordinator.async_request_refresh()
