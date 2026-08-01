# FreeFall 800 Home Assistant Integration

[Home Assistant](https://www.home-assistant.io/) integration for the [FreeFall 800](https://gitlab.com/prbs23/freefall_800) open source firmware.

For more general information about FreeFall 800, see the main repository here: [prbs23/freefall_800](https://gitlab.com/prbs23/freefall_800)

[[_TOC_]]

## Entities

| Platform           | Entity                       | Source                                         |
| ------------------ | ---------------------------- | ---------------------------------------------- |
| `climate`          | Grill                        | `current_temp_c` / `set_temp_c`                |
| `switch`           | Power                        | `power_on`                                     |
| `switch`           | Probe 1-4 alarm              | `probe_set_temp_c[]` (armed = not null)        |
| `sensor`           | Probe 1-4 temperature        | `probe_temp_c[]`                               |
| `sensor`           | Fan speed                    | `fan_speed_pct`                                |
| `sensor`           | Timer finishes at            | `timer_remaining_s` (as an absolute timestamp) |
| `binary_sensor`    | Lid Open                     | `lid_open`                                     |
| `number`           | Probe 1-4 target             | `probe_set_temp_c[]`                           |
| `number`           | Timer duration               | `timer_duration_s`                             |
| `button`           | Clear timer                  | `timer_duration_s` (sets it to null)           |

The device has no push channel (no WebSocket/SSE/mDNS today), so the
integration polls `/api/status` and `/api/control` every 10 seconds
(`iot_class: local_polling` in `manifest.json`).

Config entries are keyed on the device's MAC address (`mac_address` from
`/api/config`). If the device's IP changes, re-running the config flow with the
new address updates the existing entry in place instead of creating a
duplicate.

## Getting started

### HACS

Add this repository as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories/)
in HACS, category "Integration", then install "FreeFall 800".

### Manual

Copy `custom_components/freefall800/` into your Home Assistant config's
`custom_components/` directory and restart Home Assistant.

Then, in either case: **Settings → Devices & Services → Add Integration →
FreeFall 800**, and enter the device's IP address or host name.

## Development

To set up a venv for development purposes run the following commands:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements_dev.txt
```

Note that this is only required for Pylance/Ruff checking or IDE plugins. You do not need any special environment setup to use this integration.

### Run Type Checks
Type-check with [pyright](https://microsoft.github.io/pyright/):

```sh
pyright custom_components/freefall800/
```

### Run Linting Checks
Lint with [ruff](https://docs.astral.sh/ruff/):

```sh
ruff check custom_components/freefall800/
```

Add `--fix` to have ruff apply its safe fixes automatically.

## Reporting issues
If you run into bugs or have feature requests for the FreeFall 800 Home Assistant integration, please report them on the [FreeFall 800 Issue Tracker](https://gitlab.com/prbs23/freefall_800/-/work_items)

## License
Licensed under the GNU General Public License v3.0 — see (LICENSE)[LICENSE].

## AI Use
LLMs have been used in the development of this repository and reverse engineering of the original controller. However, most code was human-developed, and all AI-generated code has been fully reviewed, if not modified, by a human.

AI-developed contributions are not disallowed, but there **MUST** be a person behind the AI who takes responsibility for the code.