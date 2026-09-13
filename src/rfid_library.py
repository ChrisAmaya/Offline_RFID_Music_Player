#!/usr/bin/env python3
"""Database-backed RFID tag to album/playlist mapping."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from src.album_tracklist import build_tracklist_file


AUDIO_SUFFIXES = {".mp3", ".m4a", ".flac", ".wav", ".ogg"}


def initialize_database(db_path: Path) -> None:
    """Create the RFID library schema if it does not already exist."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as db:
        db.executescript(
            """
            PRAGMA foreign_keys = ON;

            CREATE TABLE IF NOT EXISTS content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                kind TEXT NOT NULL,
                path TEXT,
                description TEXT
            );

            CREATE TABLE IF NOT EXISTS content_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id INTEGER NOT NULL,
                path TEXT NOT NULL,
                title TEXT,
                sort_order INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(content_id) REFERENCES content(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS tag_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_id TEXT NOT NULL UNIQUE,
                content_id INTEGER NOT NULL,
                FOREIGN KEY(content_id) REFERENCES content(id)
            );
            """
        )


def ensure_tracklist(album_dir: Path) -> Path:
    """Return an album tracklist, creating it when it is absent."""
    album_dir = album_dir.expanduser().resolve()
    if not album_dir.is_dir():
        raise FileNotFoundError(f"Album directory not found: {album_dir}")

    tracklist_path = album_dir / "tracklist.txt"
    if not tracklist_path.exists():
        audio_files = [
            path for path in album_dir.iterdir()
            if path.is_file() and path.suffix.lower() in AUDIO_SUFFIXES
        ]
        if not audio_files:
            raise FileNotFoundError(f"No supported audio files found in {album_dir}")
        build_tracklist_file(album_dir, tracklist_path)

    if not tracklist_path.is_file():
        raise FileNotFoundError(f"Tracklist could not be created: {tracklist_path}")
    return tracklist_path.resolve()


def _content_id_for_directory(db: sqlite3.Connection, album_dir: Path) -> Optional[int]:
    row = db.execute(
        "SELECT id FROM content WHERE kind = 'album' AND path = ? ORDER BY id LIMIT 1",
        (str(album_dir),),
    ).fetchone()
    return row[0] if row else None


def register_tag(tag_id: str, album_dir: Path, db_path: Path) -> Path:
    """Map a unique RFID tag to an album directory and return its tracklist."""
    normalized_tag = str(tag_id).strip()
    if not normalized_tag:
        raise ValueError("tag_id is required")

    album_dir = album_dir.expanduser().resolve()
    tracklist_path = ensure_tracklist(album_dir)
    initialize_database(db_path)

    with sqlite3.connect(db_path) as db:
        db.execute("PRAGMA foreign_keys = ON")
        content_id = _content_id_for_directory(db, album_dir)
        if content_id is None:
            cursor = db.execute(
                "INSERT INTO content (name, kind, path, description) VALUES (?, 'album', ?, ?)",
                (album_dir.name, str(album_dir), f"Album directory: {album_dir}"),
            )
            content_id = cursor.lastrowid

        db.execute(
            "INSERT INTO tag_mappings (tag_id, content_id) VALUES (?, ?) "
            "ON CONFLICT(tag_id) DO UPDATE SET content_id = excluded.content_id",
            (normalized_tag, content_id),
        )
        db.commit()

    return tracklist_path


def playlist_for_tag(tag_id: str, db_path: Path) -> Optional[Path]:
    """Resolve an RFID tag to its existing tracklist, or return None."""
    initialize_database(db_path)
    with sqlite3.connect(db_path) as db:
        row = db.execute(
            "SELECT content.path FROM tag_mappings "
            "JOIN content ON content.id = tag_mappings.content_id "
            "WHERE tag_mappings.tag_id = ? AND content.kind = 'album'",
            (str(tag_id).strip(),),
        ).fetchone()

    if not row:
        return None

    tracklist_path = Path(row[0]).expanduser().resolve() / "tracklist.txt"
    if not tracklist_path.is_file():
        return None
    return tracklist_path
