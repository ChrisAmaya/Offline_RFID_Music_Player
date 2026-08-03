#!/usr/bin/env python3
"""Control mpv playback from physical buttons using its IPC socket."""

from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable, Optional

from config.gpio_config import BUTTON_NEXT, BUTTON_PLAY_PAUSE, BUTTON_PREV, BUTTON_SHUFFLE
from src.button_handler import ButtonEvent, ButtonHandler


def build_mpv_command(playlist_path: str, socket_path: str = "/tmp/mpv-control.sock") -> list[str]:
    """Build the mpv command for playlist playback with an IPC socket."""
    return [
        "mpv",
        "--no-audio-display",
        "--audio-device=alsa/default",
        "--audio-samplerate=48000",
        "--playlist",
        playlist_path,
        f"--input-ipc-server={socket_path}",
    ]


def button_command_for(button_name: str) -> list[str]:
    """Convert a button name into the mpv command that should be sent."""
    mapping = {
        "Play/Pause": ["cycle", "pause"],
        "Next": ["playlist-next"],
        "Previous": ["playlist-prev"],
        "Shuffle": ["playlist-shuffle"],
    }
    return mapping.get(button_name, [])


def send_mpv_command(socket_path: str, command: list[str]) -> None:
    """Send a command to mpv over its IPC socket."""
    if not command:
        return

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.connect(socket_path)
        payload = "\n".join(command) + "\n"
        sock.sendall(payload.encode("utf-8"))


class MPVButtonController:
    """Bridge physical buttons to mpv playback controls."""

    def __init__(self, playlist_path: str, socket_path: str = "/tmp/mpv-control.sock") -> None:
        self.playlist_path = playlist_path
        self.socket_path = socket_path
        self.process: Optional[subprocess.Popen[str]] = None
        self.button_handler = ButtonHandler(debounce_ms=50)
        self._register_buttons()

    def _register_buttons(self) -> None:
        self.button_handler.register_button(1, BUTTON_PLAY_PAUSE, "Play/Pause")
        self.button_handler.register_button(2, BUTTON_NEXT, "Next")
        self.button_handler.register_button(3, BUTTON_PREV, "Previous")
        self.button_handler.register_button(4, BUTTON_SHUFFLE, "Shuffle")

    def start(self) -> None:
        """Start mpv and the button handler."""
        if self.process is None or self.process.poll() is not None:
            self.process = subprocess.Popen(
                build_mpv_command(self.playlist_path, self.socket_path),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        self.button_handler.start()

        def on_button(event: ButtonEvent) -> None:
            command = button_command_for(event.button_name)
            if not command:
                return
            send_mpv_command(self.socket_path, command)

        for button_id in [1, 2, 3, 4]:
            self.button_handler.set_button_callback(button_id, on_button)

    def stop(self) -> None:
        """Stop the controller and clean up GPIO resources."""
        self.button_handler.cleanup()
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run mpv and control it from physical buttons")
    parser.add_argument("playlist", help="Path to the playlist/tracklist text file")
    parser.add_argument("--socket", default="/tmp/mpv-control.sock")
    args = parser.parse_args()

    controller = MPVButtonController(args.playlist, socket_path=args.socket)
    controller.start()
    print("Controller started. Press buttons to control mpv.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping controller")
    finally:
        controller.stop()

    return 0


if __name__ == "__main__":
    sys.exit(main())
