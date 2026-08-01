"""Data update coordinator for the FreeFall 800 integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import FreeFall800Client, FreeFall800ConnectionError
from .const import NUM_PROBES, UPDATE_INTERVAL_SECONDS

_LOGGER = logging.getLogger(__name__)

type FreeFall800ConfigEntry = ConfigEntry[FreeFall800Coordinator]


@dataclass
class FreeFall800Data:
    """Merged view of /api/status and /api/control."""

    power_on: bool
    lid_open: bool
    fan_speed_pct: int
    current_temp_c: float | None
    set_temp_c: float | None
    probe_temp_c: list[float | None]
    probe_set_temp_c: list[float | None]
    timer_remaining_s: int | None
    timer_duration_s: int | None


class FreeFall800Coordinator(DataUpdateCoordinator[FreeFall800Data]):
    """Polls the device's status and control endpoints on a fixed interval."""

    config_entry: FreeFall800ConfigEntry

    def __init__(
        self, hass: HomeAssistant, config_entry: FreeFall800ConfigEntry, client: FreeFall800Client
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=config_entry.title,
            update_interval=timedelta(seconds=UPDATE_INTERVAL_SECONDS),
        )
        self.client = client
        # Set once in __init__.py's async_setup_entry, not refreshed on
        # every poll - see the comment there for why.
        self.sw_version: str | None = None

    async def _async_update_data(self) -> FreeFall800Data:
        try:
            status = await self.client.get_status()
            control = await self.client.get_control()
        except FreeFall800ConnectionError as err:
            raise UpdateFailed(str(err)) from err

        no_probes: list[float | None] = [None] * NUM_PROBES
        probe_temp_c = status.get("probe_temp_c") or no_probes
        probe_set_temp_c = control.get("probe_set_temp_c") or no_probes

        return FreeFall800Data(
            power_on=status["power_on"],
            lid_open=status["lid_open"],
            fan_speed_pct=status["fan_speed_pct"],
            current_temp_c=status.get("current_temp_c"),
            set_temp_c=control.get("set_temp_c"),
            probe_temp_c=probe_temp_c,
            probe_set_temp_c=probe_set_temp_c,
            timer_remaining_s=status.get("timer_remaining_s"),
            timer_duration_s=control.get("timer_duration_s"),
        )
