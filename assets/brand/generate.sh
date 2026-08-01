#!/usr/bin/env bash
# Renders icon.svg into the PNG files HA's brands proxy looks for
# (see custom_components/freefall800/brand/, README.md "Getting started").
# Requires rsvg-convert (librsvg).
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
out_dir="$(cd "$script_dir/../../custom_components/freefall800/brand" && pwd)"

rsvg-convert -w 256 -h 256 -o "$out_dir/icon.png" "$script_dir/icon.svg"
rsvg-convert -w 512 -h 512 -o "$out_dir/icon@2x.png" "$script_dir/icon.svg"

echo "Wrote $out_dir/icon.png and icon@2x.png"
