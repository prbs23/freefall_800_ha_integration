"""Constants for the FreeFall integration."""

DOMAIN = "freefall800"
MANUFACTURER = "FreeFall"

# Display names for the hw_model values reported by /api/config.
MODEL_NAMES = {
    "gravity_800": "FreeFall 800",
    "gravity_1150": "FreeFall 1150",
}
# Firmware older than the hw_model field only supported the Gravity 800.
DEFAULT_HW_MODEL = "gravity_800"

DEFAULT_PORT = 80

# The firmware has no push channel (no websocket/SSE/mDNS), so we poll.
UPDATE_INTERVAL_SECONDS = 10
REQUEST_TIMEOUT_SECONDS = 5

NUM_PROBES = 4

MIN_TARGET_TEMP_C = 0
MAX_TARGET_TEMP_C = 300

# Matches the device's own default when engaging heat with no prior setpoint
# (250F/120C).
DEFAULT_TARGET_TEMP_C = 120

# Matches the device's own default when arming a probe alarm with no prior
# target (100F/40C).
DEFAULT_PROBE_TARGET_TEMP_C = 40

MAX_TIMER_SECONDS = 24 * 60 * 60

EVENT_TYPE = f"{DOMAIN}_event"

TRIGGER_GRILL_REACHED_TARGET = "grill_reached_target"
TRIGGER_TIMER_EXPIRED = "timer_expired"
TRIGGER_PROBE_ALARM_FMT = "probe_{index}_alarm"


def model_name(hw_model: str | None) -> str:
    """Display name for a device from /api/config's hw_model.

    A missing hw_model is treated as DEFAULT_HW_MODEL, and a model not in
    MODEL_NAMES is shown as its raw hw_model string.
    """
    hw_model = hw_model or DEFAULT_HW_MODEL
    return MODEL_NAMES.get(hw_model, hw_model)
