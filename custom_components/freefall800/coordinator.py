"""Data update coordinator for the FreeFall 800 integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID, CONF_TYPE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import FreeFall800Client, FreeFall800ConnectionError
from .const import (
    EVENT_TYPE,
    NUM_PROBES,
    TRIGGER_GRILL_REACHED_TARGET,
    TRIGGER_PROBE_ALARM_FMT,
    TRIGGER_TIMER_EXPIRED,
    UPDATE_INTERVAL_SECONDS,
)

_LOGGER = logging.getLogger(__name__)

type FreeFall800ConfigEntry = ConfigEntry[FreeFall800Coordinator]


@dataclass
class FreeFall800Data:
    """Snapshot of /api/status (measured values and current setpoints)."""

    power_on: bool
    lid_open: bool
    fan_speed_pct: int
    current_temp_c: float | None
    set_temp_c: float | None
    thermocouple_temp_c: float | None
    probe_temp_c: list[float | None]
    probe_set_temp_c: list[float | None]
    timer_remaining_s: int | None
    timer_duration_s: int | None


class FreeFall800Coordinator(DataUpdateCoordinator[FreeFall800Data]):
    """Polls the device's status endpoint on a fixed interval."""

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
        self.device_id: str | None = None

    async def _async_update_data(self) -> FreeFall800Data:
        try:
            status = await self.client.get_status()
        except FreeFall800ConnectionError as err:
            raise UpdateFailed(str(err)) from err

        no_probes: list[float | None] = [None] * NUM_PROBES
        probe_temp_c = status.get("probe_temp_c") or no_probes
        probe_set_temp_c = status.get("probe_set_temp_c") or no_probes

        new_data = FreeFall800Data(
            power_on=status["power_on"],
            lid_open=status["lid_open"],
            fan_speed_pct=status["fan_speed_pct"],
            current_temp_c=status.get("current_temp_c"),
            set_temp_c=status.get("set_temp_c"),
            thermocouple_temp_c=status.get("thermocouple_temp_c"),
            probe_temp_c=probe_temp_c,
            probe_set_temp_c=probe_set_temp_c,
            timer_remaining_s=status.get("timer_remaining_s"),
            timer_duration_s=status.get("timer_duration_s"),
        )
        # self.data is still the *previous* cycle's value here - the base
        # class only overwrites it after this method returns.
        self._fire_transition_events(self.data, new_data)
        return new_data

    def _fire_transition_events(
        self, previous: FreeFall800Data | None, new: FreeFall800Data
    ) -> None:
        """Fire device-trigger events on rising edges, not on initial state.

        previous is None on the very first poll - skip firing entirely then,
        so a grill that's already at temp (or a timer already at 0) when HA
        starts doesn't fire a false "just happened" event.
        """
        if self.device_id is None or previous is None:
            return

        if _at_or_past(new.current_temp_c, new.set_temp_c) and not _at_or_past(
            previous.current_temp_c, previous.set_temp_c
        ):
            self._fire_event(TRIGGER_GRILL_REACHED_TARGET)

        for i in range(NUM_PROBES):
            if _at_or_past(
                new.probe_temp_c[i], new.probe_set_temp_c[i]
            ) and not _at_or_past(previous.probe_temp_c[i], previous.probe_set_temp_c[i]):
                self._fire_event(TRIGGER_PROBE_ALARM_FMT.format(index=i + 1))

        timer_now_expired = new.timer_duration_s is not None and new.timer_remaining_s == 0
        timer_was_expired = (
            previous.timer_duration_s is not None and previous.timer_remaining_s == 0
        )
        if timer_now_expired and not timer_was_expired:
            self._fire_event(TRIGGER_TIMER_EXPIRED)

    def _fire_event(self, trigger_type: str) -> None:
        self.hass.bus.async_fire(
            EVENT_TYPE, {CONF_DEVICE_ID: self.device_id, CONF_TYPE: trigger_type}
        )


def _at_or_past(current: float | None, target: float | None) -> bool:
    """True if current has reached or passed target - False if either is unset."""
    return current is not None and target is not None and current >= target
