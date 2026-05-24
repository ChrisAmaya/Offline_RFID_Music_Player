#!/bin/bash
# Test script to detect and list CD information from USB CD module
# Usage: bash test_cd_detect.sh

set -e

echo "=========================================="
echo "CD Device Detection & Information"
echo "=========================================="
echo ""

# Function to print section headers
print_section() {
    echo ""
    echo ">>> $1"
    echo "----------------------------------------"
}

# 1. List all block devices (to find CD drive)
print_section "Available Block Devices"
lsblk -d | grep -E "NAME|sr|cd" || echo "No CD devices found in lsblk"
echo ""
lsblk | grep -E "sr|cd" || echo "No CD devices found in lsblk detail view"

# 2. Check dmesg for recently connected USB CD devices
print_section "Recent USB Device Messages"
sudo dmesg | tail -30 | grep -i "cd\|dvd\|usb\|sr" || echo "No CD/USB messages in recent dmesg"

# 3. Check /dev for CD devices
print_section "CD Devices in /dev"
ls -la /dev/sr* /dev/cd* 2>/dev/null || echo "No /dev/sr* or /dev/cd* devices found"

# 4. List mount points
print_section "Current Mount Points"
mount | grep -i "cd\|dvd" || echo "No CD/DVD mounts found"

# 5. Try to detect CD device and query it
print_section "Attempting CD Detection with cdparanoia"
if command -v cdparanoia &> /dev/null; then
    echo "cdparanoia is installed"
    echo ""
    echo "Attempting to read CD info (may require sudo):"
    cdparanoia -Q 2>/dev/null || sudo cdparanoia -Q 2>/dev/null || echo "Could not query CD device with cdparanoia"
else
    echo "⚠️ cdparanoia not installed. Installing..."
    sudo apt-get update -qq
    sudo apt-get install -y cdparanoia 2>&1 | grep -E "Setting up|already|unpacking" || true
    echo ""
    echo "Retrying CD info with cdparanoia:"
    sudo cdparanoia -Q 2>/dev/null || echo "Could not query CD device"
fi

# 6. Check if libcdio tools are available
print_section "Checking libcdio Tools"
if command -v cd-info &> /dev/null; then
    echo "cd-info found. Querying CD:"
    sudo cd-info 2>/dev/null || echo "Could not read CD with cd-info"
else
    echo "⚠️ cd-info (libcdio) not installed. Installing..."
    sudo apt-get install -y libcdio-utils 2>&1 | grep -E "Setting up|already|unpacking" || true
    echo ""
    echo "Retrying with cd-info:"
    sudo cd-info 2>/dev/null || echo "Could not read CD with cd-info"
fi

# 7. Summary
print_section "Summary"
echo "Expected device paths: /dev/sr0, /dev/sr1, /dev/cdrom"
echo ""
echo "Next steps:"
echo "1. Verify USB CD module is connected"
echo "2. Insert a CD into the module"
echo "3. Run this script again to see CD information"
echo "4. Use test_cd_play.sh to attempt playback"
