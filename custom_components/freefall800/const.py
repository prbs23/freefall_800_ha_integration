"""Constants for the FreeFall 800 integration."""

DOMAIN = "freefall800"
MANUFACTURER = "FreeFall"
MODEL = "FreeFall 800"

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
