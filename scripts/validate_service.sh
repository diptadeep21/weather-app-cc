#!/usr/bin/env bash
set -euo pipefail

echo "[validate] Checking service health on 8080"
sleep 2
curl -fsS http://localhost:8080/ >/dev/null && echo "[validate] OK" || (echo "[validate] FAILED" && exit 1)

