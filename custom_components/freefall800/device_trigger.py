"""Device triggers for FreeFall 800."""

from __future__ import annotations

from typing import cast

import voluptuous as vol
from homeassistant.components.device_automation import DEVICE_TRIGGER_BASE_SCHEMA
from homeassistant.components.homeassistant.triggers import event as event_trigger
from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_DOMAIN,
    CONF_EVENT_DATA,
    CONF_PLATFORM,
    CONF_TYPE,
)
from homeassistant.core import CALLBACK_TYPE, HomeAssistant
from homeassistant.helpers.trigger import TriggerActionType, TriggerInfo
from homeassistant.helpers.typing import ConfigType

from .const import (
    DOMAIN,
    EVENT_TYPE,
    NUM_PROBES,
    TRIGGER_GRILL_REACHED_TARGET,
    TRIGGER_PROBE_ALARM_FMT,
    TRIGGER_TIMER_EXPIRED,
)

TRIGGER_TYPES = {TRIGGER_GRILL_REACHED_TARGET, TRIGGER_TIMER_EXPIRED} | {
    TRIGGER_PROBE_ALARM_FMT.format(index=index + 1) for index in range(NUM_PROBES)
}

TRIGGER_SCHEMA = DEVICE_TRIGGER_BASE_SCHEMA.extend(
    {vol.Required(CONF_TYPE): vol.In(TRIGGER_TYPES)}
)


async def async_get_triggers(hass: HomeAssistant, device_id: str) -> list[dict[str, str]]:
    """Return the triggers available for a FreeFall 800 device."""
    return [
        {
            CONF_PLATFORM: "device",
            CONF_DOMAIN: DOMAIN,
            CONF_DEVICE_ID: device_id,
            CONF_TYPE: trigger_type,
        }
        for trigger_type in TRIGGER_TYPES
    ]


async def async_attach_trigger(
    hass: HomeAssistant,
    config: ConfigType,
    action: TriggerActionType,
    trigger_info: TriggerInfo,
) -> CALLBACK_TYPE:
    """Attach a trigger, delegating to the event platform."""
    event_config = cast(
        ConfigType,
        event_trigger.TRIGGER_SCHEMA(
            {
                CONF_PLATFORM: "event",
                event_trigger.CONF_EVENT_TYPE: EVENT_TYPE,
                CONF_EVENT_DATA: {
                    CONF_DEVICE_ID: config[CONF_DEVICE_ID],
                    CONF_TYPE: config[CONF_TYPE],
                },
            }
        ),
    )
    return await event_trigger.async_attach_trigger(
        hass, event_config, action, trigger_info, platform_type="device"
    )
