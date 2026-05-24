#!/bin/bash
# Repeating Audio Test Script
# Plays stereo test tones through HiFiBerry DAC using speaker-test
# Uses hw:1,0 (HiFiBerry DAC+) with 2 channels (stereo)

echo "=========================================="
echo "Audio Test - Repeating (10 times)"
echo "HiFiBerry DAC (hw:1,0) - Stereo"
echo "=========================================="
echo ""

for i in {1..10}; do
    echo "Playing test $i/10..."
    # Generate 1kHz sine wave, 2 channels (stereo), 3 seconds each
    speaker-test -D hw:1,0 -t sine -f 1000 -c 2 -l 1 2>/dev/null
    echo "  ✓ Completed"
    sleep 0.5
done

echo ""
echo "=========================================="
echo "Audio test complete!"
echo "=========================================="
