#!/usr/bin/env python3
"""
Simple RFID-to-audio mapping script for the offline music player.

This script lets you:
1. create a local SQLite database for RFID tag mappings,
2. map a tag to an album of songs from a directory,
3. play that mapped content when the RFID tag is detected.

Example usage:

  python3 test-rfid-play.py --setup --tag-id 1234567890 --music-dir /home/neonkon/Music/All_Songs
  python3 test-rfid-play.py --listen --db /home/neonkon/Offline_RFID_Music_Player/data/rfid_library.db

The script is intentionally simple and local-only. It does not need to be pushed to GitHub.
"""

import argparse
import os
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional

try:
    from src.rfid_reader import RFIDReader
except ImportError:
    RFIDReader = None

DEFAULT_DB_PATH = Path("~/Offline_RFID_Music_Player/data/rfid_library.db").expanduser()
DEFAULT_MUSIC_DIR = Path("~/All_Songs").expanduser()
DEFAULT_MEDIA_ROOT = DEFAULT_MUSIC_DIR
DEFAULT_TAG_ID = "replace-me-with-your-real-tag"


def init_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            kind TEXT NOT NULL,
            path TEXT,
            description TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS content_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id INTEGER NOT NULL,
            path TEXT NOT NULL,
            title TEXT,
            FOREIGN KEY(content_id) REFERENCES content(id) ON DELETE CASCADE
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tag_mappings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_id TEXT NOT NULL UNIQUE,
            content_id INTEGER NOT NULL,
            FOREIGN KEY(content_id) REFERENCES content(id)
        )
        """
    )
    conn.commit()
    return conn


def discover_audio_files(music_dir: Path) -> List[Path]:
    if not music_dir.exists():
        raise FileNotFoundError(f"Music directory not found: {music_dir}")
    files = [p for p in music_dir.iterdir() if p.is_file() and p.suffix.lower() in {".mp3", ".m4a", ".wav", ".flac"}]
    return sorted(files, key=lambda p: p.name.lower())


def create_album_mapping(conn: sqlite3.Connection, tag_id: str, album_name: str, music_dir: Path, media_root: Optional[Path] = None) -> int:
    audio_files = discover_audio_files(music_dir)
    if not audio_files:
        raise FileNotFoundError(f"No supported audio files found in {music_dir}")

    if media_root is None:
        media_root = music_dir
    media_root = media_root.expanduser()

    cursor = conn.execute("SELECT id FROM content WHERE name = ? AND kind = 'album'", (album_name,))
    existing_row = cursor.fetchone()
    if existing_row:
        content_id = existing_row[0]
        conn.execute("DELETE FROM content_entries WHERE content_id = ?", (content_id,))
    else:
        cursor = conn.execute(
            "INSERT INTO content (name, kind, path, description) VALUES (?, 'album', ?, ?)",
            (album_name, str(media_root.name), f"Album mapped from {music_dir}"),
        )
        content_id = cursor.lastrowid

    for song_path in audio_files:
        relative_path = os.path.relpath(song_path, media_root)
        conn.execute(
            "INSERT INTO content_entries (content_id, path, title) VALUES (?, ?, ?)",
            (content_id, relative_path, song_path.stem),
        )

    conn.execute("INSERT OR REPLACE INTO tag_mappings (tag_id, content_id) VALUES (?, ?)", (tag_id, content_id))
    conn.commit()
    return content_id


def get_content_for_tag(conn: sqlite3.Connection, tag_id: str) -> Optional[tuple]:
    row = conn.execute(
        """
        SELECT content.id, content.name, content.kind, content.path
        FROM tag_mappings
        JOIN content ON content.id = tag_mappings.content_id
        WHERE tag_mappings.tag_id = ?
        """,
        (tag_id,),
    ).fetchone()
    return row


def get_content_entries(conn: sqlite3.Connection, content_id: int) -> List[tuple]:
    return conn.execute(
        "SELECT path, title FROM content_entries WHERE content_id = ? ORDER BY id",
        (content_id,),
    ).fetchall()


def find_player() -> Optional[List[str]]:
    for cmd in (["mpv", "--no-video", "--really-quiet"], ["mplayer"], ["ffplay", "-nodisp", "-autoexit"]):
        try:
            subprocess.run([cmd[0], "--version"], check=False, capture_output=True, text=True)
        except FileNotFoundError:
            continue
        return cmd
    return None


def resolve_media_path(entry_path: str, media_root: Optional[Path] = None) -> Path:
    path = Path(entry_path)
    if path.is_absolute():
        return path
    if media_root is None:
        return path
    return (media_root / path).expanduser()


def play_content(conn: sqlite3.Connection, tag_id: str, media_root: Optional[Path] = None) -> None:
    content_row = get_content_for_tag(conn, tag_id)
    if not content_row:
        print(f"No mapping found for tag: {tag_id}")
        return

    content_id = content_row[0]
    content_name = content_row[1]
    content_kind = content_row[2]
    print(f"Playing {content_name} ({content_kind})")

    entries = get_content_entries(conn, content_id)
    if not entries:
        print("No songs found for this mapped content")
        return

    if media_root is not None:
        media_root = media_root.expanduser()

    resolved_paths = []
    for entry in entries:
        resolved_path = resolve_media_path(entry[0], media_root)
        resolved_paths.append(str(resolved_path))

    player_cmd = find_player()
    if not player_cmd:
        raise RuntimeError("No compatible player found. Install mpv, mplayer, or ffplay.")

    command = player_cmd + resolved_paths
    print("Launching:", " ".join(command))
    subprocess.Popen(command)


class SimulatedRFIDReader:
    """Fallback reader used when the Pi hardware is unavailable."""

    def __init__(self, tag_id: str):
        self.tag_id = tag_id

    def read_once(self):
        return self.tag_id


def listen_for_tags(conn: sqlite3.Connection, tag_id_override: Optional[str] = None) -> None:
    if tag_id_override:
        play_content(conn, tag_id_override)
        return

    if RFIDReader is not None:
        try:
            reader = RFIDReader()
            if not reader.connect():
                print("RFID hardware not available; falling back to simulated mode")
                raise RuntimeError("hardware unavailable")
            reader.start()
            print("Waiting for RFID tags. Press Ctrl+C to stop.")
            while True:
                time.sleep(0.2)
        except KeyboardInterrupt:
            print("Stopped")
        finally:
            try:
                reader.disconnect()
            except Exception:
                pass
        return

    print("RFID hardware libraries are not available. Use --tag-id to test playback manually.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Map RFID tags to songs, albums, or playlists")
    parser.add_argument("--setup", action="store_true", help="Create the database and map one tag to an album")
    parser.add_argument("--tag-id", default=DEFAULT_TAG_ID, help="RFID tag ID to map or play")
    parser.add_argument("--music-dir", default=str(DEFAULT_MUSIC_DIR), help="Directory containing the audio files")
    parser.add_argument("--album-name", default="Mac Miller - Swimming", help="Name for the album entry")
    parser.add_argument("--db", default=str(DEFAULT_DB_PATH), help="Path to the SQLite database file")
    parser.add_argument("--media-root", default=str(DEFAULT_MEDIA_ROOT), help="Base folder containing the audio files on this machine")
    parser.add_argument("--listen", action="store_true", help="Wait for RFID tags and play the mapped content")
    parser.add_argument("--play", action="store_true", help="Play the content mapped to the specified tag")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db_path = Path(args.db).expanduser()
    conn = init_db(db_path)

    if args.setup:
        content_id = create_album_mapping(
            conn,
            args.tag_id,
            args.album_name,
            Path(args.music_dir).expanduser(),
            Path(args.media_root).expanduser(),
        )
        print(f"Mapped tag {args.tag_id} to album '{args.album_name}' (content_id={content_id})")
        print(f"Database: {db_path}")
        if args.tag_id == DEFAULT_TAG_ID:
            print("Warning: the default tag ID is still placeholder text. Replace it with your real RFID tag.")
        return

    if args.play:
        play_content(conn, args.tag_id, Path(args.media_root).expanduser())
        return

    if args.listen:
        listen_for_tags(conn, None if args.tag_id == DEFAULT_TAG_ID else args.tag_id)
        return

    print("No action selected. Use --setup, --play, or --listen.")


if __name__ == "__main__":
    main()
