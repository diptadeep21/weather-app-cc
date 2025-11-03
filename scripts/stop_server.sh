#!/usr/bin/env bash
set -euo pipefail

echo "[stop] Stopping weather service if running"
sudo systemctl stop weather.service || true

