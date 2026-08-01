"""Climate platform for the FreeFall 800's main grill temperature control."""

from __future__ import annotations

from typing import ClassVar

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import ClimateEntityFeature, HVACMode
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DEFAULT_TARGET_TEMP_C, MAX_TARGET_TEMP_C, MIN_TARGET_TEMP_C
from .coordinator import FreeFall800ConfigEntry, FreeFall800Coordinator
from .entity import FreeFall800Entity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FreeFall800ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the climate entity for a FreeFall 800 config entry."""
    async_add_entities([FreeFall800Climate(entry.runtime_data)])


class FreeFall800Climate(FreeFall800Entity, ClimateEntity):
    """Represents the FreeFall 800's main chamber temperature control."""

    _attr_translation_key = "grill"
    _attr_icon = "mdi:gas-burner"
    _attr_hvac_modes: ClassVar[list[HVACMode]] = [HVACMode.OFF, HVACMode.HEAT]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TURN_ON
    )
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_min_temp = MIN_TARGET_TEMP_C
    _attr_max_temp = MAX_TARGET_TEMP_C

    def __init__(self, coordinator: FreeFall800Coordinator) -> None:
        super().__init__(coordinator, "grill")

    @property
    def hvac_mode(self) -> HVACMode:
        return HVACMode.OFF if self.coordinator.data.set_temp_c is None else HVACMode.HEAT

    @property
    def current_temperature(self) -> float | None:
        return self.coordinator.data.current_temp_c

    @property
    def target_temperature(self) -> float | None:
        return self.coordinator.data.set_temp_c

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.OFF:
            await self.coordinator.client.set_control({"set_temp_c": None})
        elif self.coordinator.data.set_temp_c is None:
            # Enable grill with no prior setpoint: fall back to the 250F/120C.
            await self.coordinator.client.set_control({"set_temp_c": DEFAULT_TARGET_TEMP_C})
        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs) -> None:
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
        await self.coordinator.client.set_control({"set_temp_c": temperature})
        await self.coordinator.async_request_refresh()
