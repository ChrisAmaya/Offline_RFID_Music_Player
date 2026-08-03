#!/usr/bin/env python3
"""
RFID-triggered audio playback helper.

This module can initialize an RC522 reader, wait for a tag, and then play
an MP3 file through mpv using the working HiFiBerry ALSA settings.
"""

import argparse
import os
import subprocess
import sys
import time
from typing import Any, Callable, Optional


def setup_rfid_reader(reader_factory: Optional[Callable[[], Any]] = None) -> Any:
    """Create and initialize an RFID reader instance for the Pi RC522."""
    if reader_factory is not None:
        return reader_factory()

    try:
        from mfrc522 import SimpleMFRC522
        import RPi.GPIO as GPIO
    except ImportError as exc:  # pragma: no cover - runtime dependency
        raise ImportError(f"Required library not installed: {exc}")

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    return SimpleMFRC522()


def build_mpv_command(audio_path: str) -> list[str]:
    """Return the mpv command used for playback."""
    return [
        "mpv",
        "--no-audio-display",
        "--audio-device=alsa/default",
        "--audio-samplerate=48000",
        audio_path,
    ]


def wait_for_rfid_and_play(
    audio_path: str,
    reader_factory: Optional[Callable[[], Any]] = None,
    timeout: Optional[float] = None,
) -> dict[str, Any]:
    """
    Initialize the RFID reader, wait for a tag, and play the given audio file.

    Args:
        audio_path: Path to an MP3 file to play.
        reader_factory: Optional factory for a reader object with a ``read()`` method.
        timeout: Optional maximum wait time in seconds. If None, wait indefinitely.

    Returns:
        A dictionary with the detected tag details and playback command.
    """
    if not audio_path:
        raise ValueError("audio_path is required")

    reader = setup_rfid_reader(reader_factory=reader_factory)
    start_time = time.time()

    try:
        while True:
            if timeout is not None and (time.time() - start_time) > timeout:
                raise TimeoutError("Timed out waiting for RFID tag")

            try:
                tag_id, text = reader.read()
                if tag_id is not None:
                    command = build_mpv_command(audio_path)
                    subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return {
                        "tag_id": tag_id,
                        "text": text,
                        "audio_path": audio_path,
                        "command": command,
                    }
            except KeyboardInterrupt:
                raise
            except Exception:
                pass

            time.sleep(0.1)
    finally:
        try:
            import RPi.GPIO as GPIO
        except ImportError:
            GPIO = None

        if GPIO is not None:
            GPIO.cleanup()


def main() -> int:
    parser = argparse.ArgumentParser(description="Wait for an RFID tag and play an MP3 file")
    parser.add_argument("audio_path", nargs="?", default=os.path.expanduser("~/All_Songs/Mac Miller-Jet Fuel.mp3"))
    parser.add_argument("--timeout", type=float, default=None)
    args = parser.parse_args()

    try:
        result = wait_for_rfid_and_play(args.audio_path, timeout=args.timeout)
    except Exception as exc:
        print(f"Error: {exc}")
        return 1

    print(f"Tag detected: {result['tag_id']}")
    if result.get("text"):
        print(f"Text: {result['text']}")
    print(f"Playing: {result['audio_path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
