#!/usr/bin/env python3
"""Wait for RFID tags, resolve albums from SQLite, and control mpv playlists."""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.database_config import RFID_LIBRARY_DB_PATH
from src.rfid_library import playlist_for_tag, register_tag
from src.rfid_playlist_controls import PlaylistController, start_player, wait_for_socket

SOCKET_PATH = "/tmp/rfid-mpv.sock"


def wait_for_tag() -> tuple[int, str]:
    """Initialize RC522 and wait for one RFID tag."""
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


def run_tag(tag_id: str, db_path: Path) -> int:
    """Start the mapped playlist and its hardware controls."""
    playlist = playlist_for_tag(tag_id, db_path)
    if playlist is None:
        print(f"No playlist mapping found for RFID tag {tag_id}", file=sys.stderr)
        return 2

    player = None
    controls = None
    try:
        player = start_player(str(playlist), SOCKET_PATH)
        if not wait_for_socket(SOCKET_PATH, player):
            raise RuntimeError("mpv IPC socket did not become ready")
        controls = PlaylistController(SOCKET_PATH)
        controls.start()
        print(f"Playing tag {tag_id}: {playlist}")
        print("Play/Pause, Next, Previous, Shuffle, and volume controls are active.")
        while player.poll() is None:
            time.sleep(0.5)
        return player.returncode or 0
    finally:
        if controls is not None:
            controls.cleanup()
        if player is not None and player.poll() is None:
            player.terminate()
            player.wait(timeout=3)
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

    try:
        while True:
            tag_id, text = wait_for_tag()
            print(f"Tag detected: {tag_id}" + (f" ({text})" if text else ""))
            result = run_tag(str(tag_id), db_path)
            if args.once:
                return result
            if result == 2:
                print("Waiting for another RFID tag...")
    except KeyboardInterrupt:
        print("Stopping")
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
