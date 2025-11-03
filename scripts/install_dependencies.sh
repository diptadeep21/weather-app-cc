#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/home/ec2-user/weather-app"

echo "[install] Updating packages"
sudo yum update -y || sudo apt-get update -y || true

echo "[install] Installing Python3 and venv"
if command -v yum >/dev/null 2>&1; then
  sudo yum install -y python3 python3-venv || sudo yum install -y python38 python38-venv || true
elif command -v apt-get >/dev/null 2>&1; then
  sudo apt-get install -y python3 python3-venv python3-pip
fi

cd "$APP_DIR"

echo "[install] Creating virtual environment"
python3 -m venv .venv || true
source .venv/bin/activate

echo "[install] Upgrading pip"
pip install --upgrade pip

echo "[install] Installing requirements"
pip install -r requirements.txt

echo "[install] Done"

