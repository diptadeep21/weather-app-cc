#!/usr/bin/env bash
set -euo pipefail

echo "[start] Starting weather service via systemd"
sudo systemctl daemon-reload || true
sudo systemctl enable weather.service || true
sudo systemctl restart weather.service
sudo systemctl status weather.service --no-pager || true

