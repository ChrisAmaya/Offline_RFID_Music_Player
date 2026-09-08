#!/usr/bin/env python3
"""Play one MP3 after an RFID tag is detected and control pause/play with GPIO."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.button_handler import ButtonHandler
from src.mpv_button_controller import send_mpv_command, socket_status


AUDIO_PATH = os.path.expanduser(
    "~/all_songs/mac_miller_swimming/Mac Miller-Jet Fuel.mp3"
)
SOCKET_PATH = "/tmp/rfid-mpv.sock"
PLAY_PAUSE_BOARD_PIN = 37  # BCM GPIO 26 when using BOARD numbering


def wait_for_tag() -> tuple[int, str]:
    """Initialize the RC522 reader and block until a tag is detected."""
    try:
        from mfrc522 import SimpleMFRC522
    except ImportError as exc:
        raise RuntimeError("Install mfrc522 before running this script") from exc

    reader = SimpleMFRC522()
    print("RFID reader ready. Waiting for a tag...")

    while True:
        try:
            tag_id, text = reader.read()
            return tag_id, (text or "").strip()
        except KeyboardInterrupt:
            raise
        except Exception:
            time.sleep(0.1)


def wait_for_socket(socket_path: str, process: subprocess.Popen[Any]) -> bool:
    """Wait until mpv creates its IPC socket or exits."""
    for _ in range(50):
        if process.poll() is not None:
            return False
        if socket_status(socket_path) == "unix-socket":
            return True
        time.sleep(0.1)
    return False


def start_player(audio_path: str, socket_path: str) -> subprocess.Popen[Any]:
    """Start mpv for one file with a Unix IPC socket."""
    if not Path(audio_path).is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    if os.path.exists(socket_path):
        os.unlink(socket_path)

    command = [
        "mpv",
        "--no-audio-display",
        "--audio-device=alsa/default",
        "--audio-samplerate=48000",
        f"--input-ipc-server={socket_path}",
        audio_path,
    ]
    print(f"Starting: {' '.join(command)}")
    process = subprocess.Popen(command)

    if not wait_for_socket(socket_path, process):
        raise RuntimeError(
            f"mpv did not create IPC socket {socket_path}; process exit code: {process.poll()}"
        )

    print(f"mpv is playing. IPC socket ready: {socket_path}")
    return process


def main() -> int:
    player = None
    buttons = None

    try:
        tag_id, text = wait_for_tag()
        print(f"Tag detected: {tag_id}")
        if text:
            print(f"Tag text: {text}")

        player = start_player(AUDIO_PATH, SOCKET_PATH)

        # SimpleMFRC522 selects BOARD numbering. Preserve that mode and use
        # physical pin 37, which is BCM GPIO 26 from gpio_config.py.
        buttons = ButtonHandler(debounce_ms=50, gpio_mode=None)
        buttons.register_button(1, PLAY_PAUSE_BOARD_PIN, "Play/Pause")

        def toggle_pause(_event: Any) -> None:
            print("Play/Pause button pressed")
            send_mpv_command(SOCKET_PATH, ["cycle", "pause"])

        buttons.set_button_callback(1, toggle_pause)
        buttons.start()
        print(f"Press the GPIO {BUTTON_PLAY_PAUSE} button to pause/play.")
        print("Press Ctrl+C to stop.")

        while player.poll() is None:
            time.sleep(0.5)

        print(f"mpv exited with code {player.returncode}")
        return player.returncode or 0
    except KeyboardInterrupt:
        print("Stopping")
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    finally:
        if buttons is not None:
            buttons.cleanup()
        if player is not None and player.poll() is None:
            player.terminate()
            player.wait(timeout=3)
        if os.path.exists(SOCKET_PATH):
            os.unlink(SOCKET_PATH)


if __name__ == "__main__":
    sys.exit(main())
