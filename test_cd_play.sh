#!/bin/bash
# Test script to play CD audio from USB CD module
# Usage: bash test_cd_play.sh [device]
# Example: bash test_cd_play.sh /dev/sr0

set -e

DEVICE=${1:-/dev/sr0}
PLAY_DURATION=${2:-30}  # Default: play for 30 seconds

echo "=========================================="
echo "CD Playback Test"
echo "=========================================="
echo ""
echo "Device: $DEVICE"
echo "Play Duration: $PLAY_DURATION seconds"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Check device exists
if [ ! -e "$DEVICE" ]; then
    echo "❌ Device $DEVICE not found!"
    echo ""
    echo "Run test_cd_detect.sh first to find available CD devices"
    exit 1
fi

echo "✓ Device $DEVICE found"
echo ""

# Try mpv (preferred - most modern)
if command_exists mpv; then
    echo ">>> Using mpv for CD playback"
    echo ""
    echo "Playing CD for $PLAY_DURATION seconds..."
    echo "(Press Ctrl+C to stop early)"
    echo ""
    
    timeout "$PLAY_DURATION" mpv "cdda://$DEVICE" --audio-device=default 2>&1 || {
        EXIT_CODE=$?
        if [ $EXIT_CODE -eq 124 ]; then
            echo ""
            echo "✓ Playback completed successfully!"
        else
            echo ""
            echo "⚠️ mpv exited with code: $EXIT_CODE"
            echo "This may indicate the CD could not be read"
        fi
    }
    exit 0
fi

# Try mplayer (fallback)
if command_exists mplayer; then
    echo ">>> Using mplayer for CD playback (mpv not found)"
    echo ""
    echo "Playing CD for $PLAY_DURATION seconds..."
    echo "(Press Ctrl+C to stop early)"
    echo ""
    
    timeout "$PLAY_DURATION" mplayer "cdda://$DEVICE" 2>&1 || {
        EXIT_CODE=$?
        if [ $EXIT_CODE -eq 124 ]; then
            echo ""
            echo "✓ Playback completed successfully!"
        else
            echo ""
            echo "⚠️ mplayer exited with code: $EXIT_CODE"
        fi
    }
    exit 0
fi

# Try cdparanoia as fallback (just extract first few seconds)
if command_exists cdparanoia; then
    echo ">>> Using cdparanoia for CD audio extraction (mpv/mplayer not found)"
    echo ""
    echo "Extracting first track to test CD readability..."
    echo ""
    
    # Extract first 5 seconds of first track (roughly 44100 Hz * 16-bit * 2 channels)
    cdparanoia -d "$DEVICE" "1[0:5]" /tmp/cd_test.wav 2>&1 || {
        echo "⚠️ Could not extract audio from CD"
        exit 1
    }
    
    echo ""
    echo "✓ CD audio extracted successfully!"
    echo "Audio saved to /tmp/cd_test.wav"
    
    # Try to play the extracted audio
    if command_exists mpv; then
        echo ""
        echo "Now playing extracted audio with mpv..."
        timeout 10 mpv /tmp/cd_test.wav --audio-device=default 2>&1 || true
    elif command_exists mplayer; then
        echo ""
        echo "Now playing extracted audio with mplayer..."
        timeout 10 mplayer /tmp/cd_test.wav 2>&1 || true
    elif command_exists aplay; then
        echo ""
        echo "Now playing extracted audio with aplay..."
        timeout 10 aplay /tmp/cd_test.wav 2>&1 || true
    fi
    
    exit 0
fi

# No playback tools found
echo "❌ No CD playback tools found!"
echo ""
echo "Install playback tools:"
echo "  sudo apt-get install mpv"
echo "  # or:"
echo "  sudo apt-get install mplayer"
echo "  # or:"
echo "  sudo apt-get install cdparanoia"
exit 1
