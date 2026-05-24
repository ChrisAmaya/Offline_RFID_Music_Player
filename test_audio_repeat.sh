#!/bin/bash
# Repeating Audio Test Script
# Plays the ALSA test sound on repeat through HiFiBerry DAC
# Sends audio directly to hw:1,0 (HiFiBerry DAC+)

echo "=========================================="
echo "Audio Test - Repeating (10 times)"
echo "HiFiBerry DAC (hw:1,0)"
echo "=========================================="
echo ""

for i in {1..10}; do
    echo "Playing test $i/10..."
    aplay -D hw:1,0 /usr/share/sounds/alsa/Front_Center.wav
    echo "  ✓ Completed"
    sleep 1
done

echo ""
echo "=========================================="
echo "Audio test complete!"
echo "=========================================="
