#!/bin/bash
# Setup HiFiBerry as Default Audio Device
# Run with: sudo bash setup_hifiberry_default.sh

echo "=========================================="
echo "Setting HiFiBerry DAC as Default Audio"
echo "=========================================="
echo ""

# Create /etc/asound.conf
sudo tee /etc/asound.conf > /dev/null <<EOF
# ALSA Configuration - HiFiBerry DAC as default
defaults.pcm.card 1
defaults.ctl.card 1
EOF

echo "✓ Created /etc/asound.conf"
echo ""
echo "Configuration:"
echo "  Default PCM card: 1 (HiFiBerry)"
echo "  Default CTL card: 1 (HiFiBerry)"
echo ""

# Verify
echo "Verifying configuration:"
cat /etc/asound.conf
echo ""

echo "=========================================="
echo "✓ HiFiBerry is now the default audio device!"
echo "=========================================="
echo ""
echo "All audio applications will use HiFiBerry by default."
echo "No reboot required - changes take effect immediately."
