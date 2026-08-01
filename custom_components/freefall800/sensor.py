"""Sensor platform for the FreeFall 800: probe temps, fan speed, timer remaining."""

from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import NUM_PROBES
from .coordinator import FreeFall800ConfigEntry, FreeFall800Coordinator
from .entity import FreeFall800Entity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FreeFall800ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors for a FreeFall 800 config entry."""
    coordinator = entry.runtime_data
    entities: list[SensorEntity] = [
        FreeFall800ProbeTempSensor(coordinator, index) for index in range(NUM_PROBES)
    ]
    entities.append(FreeFall800FanSpeedSensor(coordinator))
    entities.append(FreeFall800TimerFinishesAtSensor(coordinator))
    async_add_entities(entities)


class FreeFall800ProbeTempSensor(FreeFall800Entity, SensorEntity):
    """A single meat probe's current temperature."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:thermometer-probe"

    def __init__(self, coordinator: FreeFall800Coordinator, index: int) -> None:
        super().__init__(coordinator, f"probe_{index}_temp")
        self._index = index
        self._attr_translation_key = "probe_temp"
        self._attr_translation_placeholders = {"index": str(index + 1)}

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.probe_temp_c[self._index]


class FreeFall800FanSpeedSensor(FreeFall800Entity, SensorEntity):
    """Current fan speed as a percentage."""

    _attr_translation_key = "fan_speed"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:fan"

    def __init__(self, coordinator: FreeFall800Coordinator) -> None:
        super().__init__(coordinator, "fan_speed")

    @property
    def native_value(self) -> int:
        return self.coordinator.data.fan_speed_pct


class FreeFall800TimerFinishesAtSensor(FreeFall800Entity, SensorEntity):
    """Absolute time the cook timer finishes, if one is running.

    Reported as a timestamp rather than a countdown so the frontend renders
    it as a live relative time ("in 47 min") without needing repolling to
    stay accurate between coordinator updates.
    """

    _attr_translation_key = "timer_finishes_at"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:timer"
    def __init__(self, coordinator: FreeFall800Coordinator) -> None:
        super().__init__(coordinator, "timer_finishes_at")

    @property
    def native_value(self) -> datetime | None:
        remaining_s = self.coordinator.data.timer_remaining_s
        if remaining_s is None:
            return None
        return dt_util.utcnow() + timedelta(seconds=remaining_s)
