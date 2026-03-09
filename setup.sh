#!/bin/bash

# RFID Music Player - Setup Script for Raspberry Pi 3B

echo "========================================"
echo "RFID/CD Music Player Setup"
echo "========================================"

# Check if running on Raspberry Pi
if [ ! -f /etc/os-release ] || ! grep -q "Raspberry Pi" /etc/os-release; then
    echo "Warning: This script is designed for Raspberry Pi OS"
fi

# Update system packages
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    git \
    libmpv-dev \
    mpv \
    libcdio-dev \
    libcdio-paranoia-dev \
    cdparanoia \
    sqlite3 \
    python3-gpio \
    libfreetype6-dev \
    libjpeg-dev \
    build-essential \
    x11-xserver-utils \
    xserver-xorg-core

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install Python requirements
echo "Installing Python packages..."
pip install -r requirements.txt

# Enable SPI for RFID + Display
echo "Configuring Raspberry Pi interfaces..."
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_i2c 0

# Create data directories
echo "Creating data directories..."
mkdir -p data/music
mkdir -p data/cd_database
mkdir -p logs

# Create stub files
touch data/jukebox.db
touch logs/player.log

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Configure hardware settings in config/"
echo "3. Test hardware components (GPIO, RFID, audio)"
echo "4. See docs/SETUP_GUIDE.md for detailed instructions"
echo ""
