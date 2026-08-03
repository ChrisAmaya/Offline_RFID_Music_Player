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
import random
import re
import shutil
import signal
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable, List, Optional

try:
    from src.rfid_reader import RFIDReader
except ImportError:
    RFIDReader = None

DEFAULT_DB_PATH = Path("~/Offline_RFID_Music_Player/data/rfid_library.db").expanduser()
DEFAULT_MUSIC_DIR = Path("~/All_Songs").expanduser()
DEFAULT_MEDIA_ROOT = DEFAULT_MUSIC_DIR
DEFAULT_TAG_ID = "replace-me-with-your-real-tag"
DEFAULT_TRACK_ORDER = [
    "Come Back to Earth.mp3",
    "Hurt Feelings.mp3",
    "What's the Use-.mp3",
    "Perfecto.mp3",
    "Self Care.mp3",
    "Wings.mp3",
    "Ladders.mp3",
    "Small Worlds.mp3",
    "Conversation Pt. 1.mp3",
    "Dunno.mp3",
    "Jet Fuel.mp3",
    "2009.mp3",
    "So It Goes.mp3",
]


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
            sort_order INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(content_id) REFERENCES content(id) ON DELETE CASCADE
        )
        """
    )
    columns = [row[1] for row in conn.execute("PRAGMA table_info(content_entries)").fetchall()]
    if "sort_order" not in columns:
        conn.execute("ALTER TABLE content_entries ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 0")
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


def _normalize_filename(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _find_matching_audio_file(requested_name: str, audio_files: List[Path]) -> Optional[Path]:
    requested_norm = _normalize_filename(requested_name)
    requested_stem = Path(requested_norm).stem
    for path in audio_files:
        candidate_names = [
            _normalize_filename(path.name),
            _normalize_filename(path.stem),
        ]
        if any(candidate == requested_norm for candidate in candidate_names):
            return path
        if any(candidate.startswith(requested_norm) or requested_norm.startswith(candidate) for candidate in candidate_names):
            return path
        if requested_stem and any(candidate == requested_stem for candidate in [Path(name).stem for name in candidate_names]):
            return path
    return None


def create_album_mapping(
    conn: sqlite3.Connection,
    tag_id: str,
    album_name: str,
    music_dir: Path,
    media_root: Optional[Path] = None,
    track_order: Optional[List[str]] = None,
) -> int:
    audio_files = discover_audio_files(music_dir)
    if not audio_files:
        raise FileNotFoundError(f"No supported audio files found in {music_dir}")

    if media_root is None:
        media_root = music_dir
    media_root = media_root.expanduser()

    if track_order is None and album_name == "Mac Miller - Swimming":
        track_order = DEFAULT_TRACK_ORDER

    ordered_files: List[Path] = []
    if track_order:
        requested_names = [item.strip() for item in track_order if item and item.strip()]
        for requested_name in requested_names:
            matching_file = _find_matching_audio_file(requested_name, audio_files)
            if matching_file is not None and matching_file not in ordered_files:
                ordered_files.append(matching_file)
        remaining_files = [path for path in audio_files if path not in ordered_files]
        ordered_files.extend(remaining_files)
    else:
        ordered_files = sorted(audio_files, key=lambda p: p.name.lower())

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

    for sort_order, song_path in enumerate(ordered_files):
        relative_path = os.path.relpath(song_path, media_root)
        conn.execute(
            "INSERT INTO content_entries (content_id, path, title, sort_order) VALUES (?, ?, ?, ?)",
            (content_id, relative_path, song_path.stem, sort_order),
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
        "SELECT path, title FROM content_entries WHERE content_id = ? ORDER BY sort_order, id",
        (content_id,),
    ).fetchall()


class FFmpegPlaybackController:
    """Small controller for ffmpeg-based playback with pause/skip/shuffle support."""

    def __init__(
        self,
        playlist: List[str],
        *,
        media_root: Optional[Path] = None,
        alsa_device: str = "hw:1,0",
        shuffle: bool = False,
        shuffle_seed: Optional[int] = None,
        process_factory: Optional[Callable[[List[str]], object]] = None,
    ) -> None:
        self.playlist = list(playlist)
        self.media_root = media_root
        self.alsa_device = alsa_device
        self.shuffle = shuffle
        self.shuffle_seed = shuffle_seed
        self.process_factory = process_factory or self._default_process_factory
        self.process = None
        self.current_index = 0
        self.paused = False
        self.current_path = self.playlist[0] if self.playlist else None
        if self.shuffle:
            self._shuffle_playlist()

    def _default_process_factory(self, command: List[str]):
        return subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _is_process_running(self) -> bool:
        if self.process is None:
            return False
        poll = getattr(self.process, "poll", None)
        if poll is None:
            return True
        return poll() is None

    def _shuffle_playlist(self) -> None:
        if not self.playlist:
            return
        shuffled = list(self.playlist)
        random.Random(self.shuffle_seed).shuffle(shuffled)
        self.playlist = shuffled
        self.current_index = 0
        self.current_path = self.playlist[0] if self.playlist else None

    def _build_command(self, path: str) -> List[str]:
        return [
            "ffmpeg",
            "-i",
            path,
            "-vn",
            "-c:a",
            "pcm_s16le",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-f",
            "alsa",
            self.alsa_device,
        ]

    def _stop_current_process(self) -> None:
        if self.process is None:
            return
        poll = getattr(self.process, "poll", None)
        if callable(poll):
            if poll() is not None:
                self.process = None
                return
        try:
            terminate = getattr(self.process, "terminate", None)
            if callable(terminate):
                terminate()
            else:
                os.kill(self.process.pid, signal.SIGTERM)
        except Exception:
            pass
        self.process = None

    def play(self, index: Optional[int] = None) -> None:
        if not self.playlist:
            return
        if index is not None:
            self.current_index = index % len(self.playlist)
        if self._is_process_running():
            if self.paused:
                os.kill(self.process.pid, signal.SIGCONT)
                self.paused = False
            return
        if self.process is not None:
            self.process = None
        self.current_path = self.playlist[self.current_index]
        command = self._build_command(self.current_path)
        self.process = self.process_factory(command)
        self.paused = False

    def toggle_pause(self) -> None:
        if self.process is None:
            self.play()
            return
        if self.paused:
            os.kill(self.process.pid, signal.SIGCONT)
            self.paused = False
        else:
            os.kill(self.process.pid, signal.SIGSTOP)
            self.paused = True

    def next_track(self) -> None:
        if not self.playlist:
            return
        self._stop_current_process()
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play(self.current_index)

    def previous_track(self) -> None:
        if not self.playlist:
            return
        self._stop_current_process()
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play(self.current_index)


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

    if shutil.which("ffmpeg"):
        controller = FFmpegPlaybackController(resolved_paths, media_root=media_root)
        controller.play()
        print("Launching ffmpeg playback controller")
        return

    player_cmd = find_player()
    if not player_cmd:
        raise RuntimeError("No compatible player found. Install mpv, mplayer, ffplay, or ffmpeg.")

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
    parser.add_argument("--track-order", default=None, help="Comma-separated track filenames in the desired album order")
    parser.add_argument("--listen", action="store_true", help="Wait for RFID tags and play the mapped content")
    parser.add_argument("--play", action="store_true", help="Play the content mapped to the specified tag")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db_path = Path(args.db).expanduser()
    conn = init_db(db_path)

    if args.setup:
        track_order = None
        if args.track_order:
            track_order = [item.strip() for item in args.track_order.split(",") if item.strip()]
        content_id = create_album_mapping(
            conn,
            args.tag_id,
            args.album_name,
            Path(args.music_dir).expanduser(),
            Path(args.media_root).expanduser(),
            track_order=track_order,
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
