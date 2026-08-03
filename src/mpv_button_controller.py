#!/usr/bin/env python3
"""Control mpv playback from physical buttons using its IPC socket."""

from __future__ import annotations

import argparse
import os
import socket
import stat
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional


DEBUG = True

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.gpio_config import BUTTON_NEXT, BUTTON_PLAY_PAUSE, BUTTON_PREV, BUTTON_SHUFFLE
from src.button_handler import ButtonEvent, ButtonHandler


def build_mpv_command(playlist_path: str, socket_path: str = "/tmp/mpv-control.sock") -> list[str]:
    """Build the mpv command for playlist playback with an IPC socket."""
    return [
        "mpv",
        "--no-audio-display",
        "--audio-device=alsa/default",
        "--audio-samplerate=48000",
        "--idle=yes",
        f"--playlist={playlist_path}",
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


def debug_print(message: str) -> None:
    """Print a debug message when debugging is enabled."""
    if DEBUG:
        print(f"[mpv-controller] {message}")


def socket_status(socket_path: str) -> str:
    """Return a short status string for the IPC socket path."""
    if not os.path.exists(socket_path):
        return "missing"

    try:
        mode = os.stat(socket_path).st_mode
    except FileNotFoundError:
        return "missing"

    if os.path.islink(socket_path):
        return "symlink"
    if socket.S_ISSOCK(mode):
        return "unix-socket"
    if stat.S_ISREG(mode):
        return "regular-file"
    return "other"


def send_mpv_command(socket_path: str, command: list[str]) -> None:
    """Send a command to mpv over its IPC socket."""
    if not command:
        return

    payload = "\n".join(command) + "\n"
    debug_print(f"sending command: {payload.rstrip()}")
    debug_print(f"socket status before send: {socket_status(socket_path)}")

    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.connect(socket_path)
            sock.sendall(payload.encode("utf-8"))
            debug_print(f"command sent successfully to {socket_path}")
    except FileNotFoundError:
        debug_print(f"socket not found at {socket_path}")
    except ConnectionRefusedError:
        debug_print(f"socket connection refused at {socket_path}")
    except Exception as exc:
        debug_print(f"socket send failed: {exc}")


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
        debug_print(f"starting mpv with playlist: {self.playlist_path}")
        debug_print(f"using socket: {self.socket_path}")

        if self.process is None or self.process.poll() is not None:
            self.process = subprocess.Popen(
                build_mpv_command(self.playlist_path, self.socket_path),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            debug_print(f"mpv process started with pid {self.process.pid}")

        for _ in range(20):
            if socket_status(self.socket_path) != "missing":
                break
            time.sleep(0.2)

        debug_print(f"socket status after startup wait: {socket_status(self.socket_path)}")
        self.button_handler.start()

        def on_button(event: ButtonEvent) -> None:
            command = button_command_for(event.button_name)
            if not command:
                debug_print(f"no mpv command mapped for button: {event.button_name}")
                return
            debug_print(f"button pressed: {event.button_name}")
            send_mpv_command(self.socket_path, command)

        for button_id in [1, 2, 3, 4]:
            self.button_handler.set_button_callback(button_id, on_button)

    def stop(self) -> None:
        """Stop the controller and clean up GPIO resources."""
        debug_print("stopping controller")
        self.button_handler.cleanup()
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
        debug_print(f"final socket status: {socket_status(self.socket_path)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run mpv and control it from physical buttons")
    parser.add_argument("playlist", help="Path to the playlist/tracklist text file")
    parser.add_argument("--socket", default="/tmp/mpv-control.sock")
    args = parser.parse_args()

    controller = MPVButtonController(args.playlist, socket_path=args.socket)
    controller.start()
    print("Controller started. Press buttons to control mpv.")
    debug_print(f"socket status after start: {socket_status(args.socket)}")
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
