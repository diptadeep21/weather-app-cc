#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/home/ec2-user/weather-app"
SERVICE_FILE="/etc/systemd/system/weather.service"

echo "[systemd] Writing service file"
sudo bash -c "cat > $SERVICE_FILE" <<'UNIT'
[Unit]
Description=Weather Flask App (gunicorn)
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/home/ec2-user/weather-app
Environment=PYTHONUNBUFFERED=1
EnvironmentFile=-/etc/sysconfig/weather
ExecStart=/home/ec2-user/weather-app/.venv/bin/gunicorn -w 2 -b 0.0.0.0:8080 app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
UNIT

echo "[systemd] Creating environment file for app"
sudo mkdir -p /etc/sysconfig
sudo bash -c 'cat > /etc/sysconfig/weather <<EOF
# Place secrets here or use SSM/Secrets Manager. Example:
# OPENWEATHER_API_KEY=YOUR_API_KEY
EOF'

echo "[systemd] Daemon reload"
sudo systemctl daemon-reload

