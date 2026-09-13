#!/usr/bin/env python3
"""Wait for RFID tags, resolve albums from SQLite, and control mpv playlists."""

from __future__ import annotations

import argparse
import os
import queue
import sys
import threading
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.database_config import RFID_LIBRARY_DB_PATH
from src.rfid_library import playlist_for_tag, register_tag

SOCKET_PATH = "/tmp/rfid-mpv.sock"


def create_rfid_reader() -> Any:
    """Initialize the RC522 reader and preserve its GPIO setup."""
    try:
        from mfrc522 import SimpleMFRC522
        import RPi.GPIO as GPIO
    except ImportError as exc:
        raise RuntimeError("Install mfrc522 before running this script") from exc

    GPIO.setwarnings(False)
    return SimpleMFRC522()


class RFIDTagMonitor:
    """Read tags continuously in the background while playback is active."""

    def __init__(self, reader: Any) -> None:
        self.reader = reader
        self.tags: queue.Queue[tuple[int, str]] = queue.Queue()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def _read_loop(self) -> None:
        last_tag_id = None
        last_tag_time = 0.0
        while not self._stop_event.is_set():
            try:
                tag_id, text = self.reader.read()
                now = time.time()
                if tag_id != last_tag_id or now - last_tag_time > 1.0:
                    self.tags.put((tag_id, (text or "").strip()))
                    last_tag_id = tag_id
                    last_tag_time = now
            except Exception:
                if not self._stop_event.is_set():
                    time.sleep(0.1)

    def get(self, timeout: float = 0.5) -> tuple[int, str] | None:
        try:
            return self.tags.get(timeout=timeout)
        except queue.Empty:
            return None

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2)


def start_tag_session(tag_id: str, db_path: Path):
    """Start the mapped playlist and return its player."""
    from src.rfid_playlist_controls import start_player, wait_for_socket

    playlist = playlist_for_tag(tag_id, db_path)
    if playlist is None:
        print(f"No playlist mapping found for RFID tag {tag_id}", file=sys.stderr)
        return None

    player = start_player(str(playlist), SOCKET_PATH)
    if not wait_for_socket(SOCKET_PATH, player):
        player.terminate()
        player.wait(timeout=3)
        raise RuntimeError("mpv IPC socket did not become ready")

    print(f"Playing tag {tag_id}: {playlist}")
    return player


def stop_player(player: Any) -> None:
    """Stop only mpv so the hardware controllers survive album changes."""
    if player is not None and player.poll() is None:
        player.terminate()
        try:
            player.wait(timeout=3)
        except Exception:
            player.kill()
    if os.path.exists(SOCKET_PATH):
        os.unlink(SOCKET_PATH)


def main() -> int:
    parser = argparse.ArgumentParser(description="Map RFID tags to album playlists and play them")
    parser.add_argument("--db", default=RFID_LIBRARY_DB_PATH, help="SQLite RFID library path")
    parser.add_argument("--register", nargs=2, metavar=("TAG_ID", "ALBUM_DIR"), help="Register a tag-to-album mapping")
    parser.add_argument("--once", action="store_true", help="Read and handle one RFID tag, then exit")
    args = parser.parse_args()
    db_path = Path(args.db).expanduser().resolve()

    if args.register:
        tag_id, album_dir = args.register
        tracklist = register_tag(tag_id, Path(album_dir), db_path)
        print(f"Mapped tag {tag_id} to {tracklist}")
        return 0

    player = None
    controls = None
    monitor = None
    active_tag = None

    try:
        monitor = RFIDTagMonitor(create_rfid_reader())
        monitor.start()
        print("RFID reader ready. Waiting for tags...")

        while True:
            detected = monitor.get()
            if detected is None:
                if player is not None and player.poll() is not None:
                    player = None
                    active_tag = None
                continue

            tag_id, text = detected
            tag_key = str(tag_id)
            if tag_key == active_tag:
                continue

            print(f"Tag detected: {tag_id}" + (f" ({text})" if text else ""))
            new_playlist = playlist_for_tag(tag_key, db_path)
            if new_playlist is None:
                print(f"No playlist mapping found for RFID tag {tag_key}", file=sys.stderr)
                continue

            stop_player(player)
            player = start_tag_session(tag_key, db_path)
            if controls is None and player is not None:
                from src.rfid_playlist_controls import PlaylistController

                controls = PlaylistController(SOCKET_PATH)
                controls.start()
                print("Play/Pause, Next, Previous, Shuffle, and volume controls are active.")
            active_tag = tag_key if player is not None else None

            if args.once:
                return 0 if player is not None else 2

    except KeyboardInterrupt:
        print("Stopping")
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    finally:
        if monitor is not None:
            monitor.stop()
        if controls is not None:
            controls.cleanup()
        stop_player(player)


if __name__ == "__main__":
    sys.exit(main())
