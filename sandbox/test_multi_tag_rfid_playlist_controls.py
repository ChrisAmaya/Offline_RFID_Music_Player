#!/usr/bin/env python3
"""Test RFID tag-to-album registration without requiring RFID or mpv hardware."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.rfid_library import normalize_tag_id, playlist_for_tag, register_tag

DEFAULT_ALBUM = Path.home() / "Music" / "Mac Miller"


def main() -> int:
    parser = argparse.ArgumentParser(description="Test RFID playlist mapping and tracklist generation")
    parser.add_argument("--album-dir", default=str(DEFAULT_ALBUM))
    parser.add_argument("--tag-id", default="99000001")
    parser.add_argument("--db", default=None)
    args = parser.parse_args()

    music_dir = Path(args.album_dir).expanduser().resolve()
    if not music_dir.is_dir():
        print(f"Music directory not found: {music_dir}", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(args.db).expanduser().resolve() if args.db else Path(temp_dir) / "rfid-test.db"
        album_dirs = [
            path for path in sorted(music_dir.iterdir())
            if path.is_dir() and any(file.suffix.lower() in {".mp3", ".m4a", ".flac", ".wav", ".ogg"} for file in path.iterdir() if file.is_file())
        ]
        if not album_dirs:
            album_dirs = [music_dir]

        for index, album_dir in enumerate(album_dirs):
            tag_id = args.tag_id if len(album_dirs) == 1 else str(int(args.tag_id) + index)
            tracklist_path = register_tag(tag_id, album_dir, db_path)
            resolved_path = playlist_for_tag(tag_id, db_path)

            print(f"Tag: {tag_id}")
            print(f"Album directory: {album_dir}")
            print(f"Tracklist: {tracklist_path}")
            print(f"Database: {db_path}")
            print(f"Resolved mapping: {resolved_path}")
            print("Tracks:")
            for line in tracklist_path.read_text(encoding="utf-8").splitlines():
                print(f"  {line}")

            if resolved_path != tracklist_path:
                print("ERROR: database mapping did not resolve to the generated tracklist", file=sys.stderr)
                return 1

        print(f"Registered {len(album_dirs)} album mapping(s)")
        print(f"Database: {db_path}")
        print(f"Serial example 35:49:C0:A4 normalizes to {normalize_tag_id('35:49:C0:A4')}")

    print("RFID playlist mapping test passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
