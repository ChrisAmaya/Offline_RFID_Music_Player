#!/bin/bash
# Repeating Audio Test Script
# Plays the ALSA test sound on repeat for easy testing

echo "=========================================="
echo "Audio Test - Repeating (10 times)"
echo "=========================================="
echo ""

for i in {1..10}; do
    echo "Playing test $i/10..."
    aplay /usr/share/sounds/alsa/Front_Center.wav
    echo "  ✓ Completed"
    sleep 1
done

echo ""
echo "=========================================="
echo "Audio test complete!"
echo "=========================================="
