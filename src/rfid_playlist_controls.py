#!/usr/bin/env python3
"""Start an album playlist after RFID detection and control it with buttons."""

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

from config.gpio_config import (
    BUTTON_NEXT_BOARD,
    BUTTON_PLAY_PAUSE,
    BUTTON_PLAY_PAUSE_BOARD,
    BUTTON_PREV_BOARD,
    BUTTON_SHUFFLE_BOARD,
    LED_SHUFFLE_BOARD,
    PCF8591_CHANNEL_VOLUME,
    PCF8591_I2C_ADDRESS,
    PCF8591_I2C_BUS,
)
from src.button_handler import ButtonHandler
from src.led_handler import LEDHandler
from src.mpv_button_controller import send_mpv_command, socket_status
from src.potentiometer_handler import PotentiometerHandler


PLAYLIST_PATH = os.path.expanduser("~/all_songs/mac_miller_swimming/tracklist.txt")
SOCKET_PATH = "/tmp/rfid-mpv.sock"


def wait_for_tag() -> tuple[int, str]:
    """Initialize the RC522 reader and wait for one RFID tag."""
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
    """Wait for mpv to create its IPC socket or exit."""
    for _ in range(50):
        if process.poll() is not None:
            return False
        if socket_status(socket_path) == "unix-socket":
            return True
        time.sleep(0.1)
    return False


def start_player(playlist_path: str, socket_path: str) -> subprocess.Popen[Any]:
    """Start mpv with an album playlist and a Unix IPC socket."""
    playlist = Path(playlist_path).expanduser().resolve()
    if not playlist.is_file():
        raise FileNotFoundError(f"Tracklist not found: {playlist}")

    if os.path.exists(socket_path):
        os.unlink(socket_path)

    command = [
        "mpv",
        "--no-audio-display",
        "--audio-device=alsa/default",
        "--audio-samplerate=48000",
        "--loop-playlist=inf",
        "--no-input-terminal",
        f"--input-ipc-server={socket_path}",
        f"--playlist={playlist}",
    ]
    print(f"Starting playlist: {playlist}")
    process = subprocess.Popen(command, stdin=subprocess.DEVNULL, start_new_session=True)

    if not wait_for_socket(socket_path, process):
        raise RuntimeError(
            f"mpv did not create IPC socket {socket_path}; process exit code: {process.poll()}"
        )

    print(f"mpv playlist started; socket ready: {socket_path}")
    return process


class PlaylistController:
    """Connect the four physical buttons to one mpv playlist session."""

    def __init__(self, socket_path: str) -> None:
        self.socket_path = socket_path
        self.shuffle_enabled = False
        self.buttons = ButtonHandler(debounce_ms=50, gpio_mode=None)
        self.leds = LEDHandler(gpio_mode=None)
        self.potentiometer = PotentiometerHandler(
            i2c_bus=PCF8591_I2C_BUS,
            pcf8591_address=PCF8591_I2C_ADDRESS,
            channel=PCF8591_CHANNEL_VOLUME,
            deadzone=3,
        )
        self.buttons.register_button(1, BUTTON_PLAY_PAUSE_BOARD, "Play/Pause")
        self.buttons.register_button(2, BUTTON_NEXT_BOARD, "Next")
        self.buttons.register_button(3, BUTTON_PREV_BOARD, "Previous")
        self.buttons.register_button(4, BUTTON_SHUFFLE_BOARD, "Shuffle")
        self.leds.register_led("shuffle", LED_SHUFFLE_BOARD, initial_state=False)

    def start(self) -> None:
        """Start polling and connect callbacks for all four buttons."""
        callbacks = {
            1: lambda _event: self.send(["cycle", "pause"], "Play/Pause"),
            2: lambda _event: self.send(["playlist-next"], "Next"),
            3: lambda _event: self.send(["playlist-prev"], "Previous"),
            4: self.toggle_shuffle,
        }
        for button_id, callback in callbacks.items():
            self.buttons.set_button_callback(button_id, callback)

        self.potentiometer.set_callback(self.set_volume)
        self.buttons.start()
        self.potentiometer.start()

    def send(self, command: list[str], label: str) -> None:
        print(f"{label}: {command}")
        send_mpv_command(self.socket_path, command)

    def toggle_shuffle(self, _event: Any) -> None:
        self.shuffle_enabled = not self.shuffle_enabled
        command = ["playlist-shuffle"] if self.shuffle_enabled else ["playlist-unshuffle"]
        self.leds.set_state("shuffle", self.shuffle_enabled)
        self.send(command, f"Shuffle {'enabled' if self.shuffle_enabled else 'disabled'}")

    def set_volume(self, _raw_value: int, percentage: int) -> None:
        """Set mpv's software volume from the PCF8591 potentiometer."""
        self.send(["set_property", "volume", percentage], f"Volume {percentage}%")

    def cleanup(self) -> None:
        self.potentiometer.cleanup()
        self.buttons.cleanup()
        self.leds.cleanup()


def main() -> int:
    player = None
    controls = None

    try:
        tag_id, text = wait_for_tag()
        print(f"Tag detected: {tag_id}")
        if text:
            print(f"Tag text: {text}")

        player = start_player(PLAYLIST_PATH, SOCKET_PATH)
        controls = PlaylistController(SOCKET_PATH)
        controls.start()
        print(f"Play/Pause uses BCM GPIO {BUTTON_PLAY_PAUSE} (BOARD pin {BUTTON_PLAY_PAUSE_BOARD})")
        print("Next, Previous, and Shuffle buttons are active. Press Ctrl+C to stop.")

        while player.poll() is None:
            time.sleep(0.5)

        return player.returncode or 0
    except KeyboardInterrupt:
        print("Stopping")
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    finally:
        if controls is not None:
            controls.cleanup()
        if player is not None and player.poll() is None:
            player.terminate()
            player.wait(timeout=3)
        if os.path.exists(SOCKET_PATH):
            os.unlink(SOCKET_PATH)


if __name__ == "__main__":
    sys.exit(main())
