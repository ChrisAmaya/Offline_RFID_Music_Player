#!/bin/bash
set -e

echo "Offline RFID Music Player setup"

sudo apt-get update
sudo apt-get install -y \
    git \
    mpv \
    sqlite3 \
    python3-dev \
    python3-pip \
    python3-venv \
    python3-rpi.gpio

python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt

sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_i2c 0

mkdir -p data logs

echo "Setup complete. Activate the environment with: source venv/bin/activate"
