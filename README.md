# FreeFall 800 Home Assistant Integration

[Home Assistant](https://www.home-assistant.io/) integration for the [FreeFall 800](https://gitlab.com/prbs23/freefall_800) open source firmware.

For more general information about FreeFall 800, see the main repository here: [prbs23/freefall_800](https://gitlab.com/prbs23/freefall_800)

[[_TOC_]]

## Entities

The FreeFall 800 integration provides the following entities to Home Assistant.

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

## Device triggers

In addition to the entities provided above, this integration also provides
some custom device triggers:

- Grill reached target temperature
- Probe 1-4 alarm reached (fires when that probe's current temperature
  reaches its own target - the same comparison the device's own buzzer
  makes, but usable in an automation independent of hearing it)
- Cook timer expired

These triggers are set up to fires once per rising edge so that each update
does not cause an extra trigger. All the default triggers provided for standard
entities are obviously also available to use.

### Notification blueprints

To help set up notifications and other triggered automations from your FreeFall 800
device, this repository also distributes some helpful automation blueprints. To import
these blueprints into your instance you can use the buttons below through
[my.home-assistant.io](https://my.home-assistant.io), or you can copy the provided links
into the blueprint import interface via **Settings → Automations →
Blueprints → Import Blueprint**.

<!-- Badges use raw HTML instead of markdown image-in-link syntax - nesting
     markdown images inside links inside a table cell doesn't reliably
     render on GitLab, even though it may look fine in some local previews. -->

| Blueprint | Import Link | Raw YAML |
| --- | --- | --- |
| Grill reached target temperature | <a href="https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgitlab.com%2Fprbs23%2Ffreefall_800_ha_integration%2F-%2Fraw%2Fmain%2Fblueprints%2Fautomation%2Ffreefall800%2Fgrill_reached_target.yaml"><img src="https://my.home-assistant.io/badges/blueprint_import.svg" alt="Import Grill reached target temperature" height="30"></a> | `https://gitlab.com/prbs23/freefall_800_ha_integration/-/raw/main/blueprints/automation/freefall800/grill_reached_target.yaml` |
| Probe alarm reached | <a href="https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgitlab.com%2Fprbs23%2Ffreefall_800_ha_integration%2F-%2Fraw%2Fmain%2Fblueprints%2Fautomation%2Ffreefall800%2Fprobe_alarm_reached.yaml"><img src="https://my.home-assistant.io/badges/blueprint_import.svg" alt="Import Probe alarm reached" height="30"></a> | `https://gitlab.com/prbs23/freefall_800_ha_integration/-/raw/main/blueprints/automation/freefall800/probe_alarm_reached.yaml`  |
| Timer expired | <a href="https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgitlab.com%2Fprbs23%2Ffreefall_800_ha_integration%2F-%2Fraw%2Fmain%2Fblueprints%2Fautomation%2Ffreefall800%2Ftimer_expired.yaml"><img src="https://my.home-assistant.io/badges/blueprint_import.svg" alt="Import Timer expired" height="30"></a> | `https://gitlab.com/prbs23/freefall_800_ha_integration/-/raw/main/blueprints/automation/freefall800/timer_expired.yaml` |

(Links point at `main` - they'll resolve once this branch is merged, not before.)

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