"""
Database Configuration for RFID Music Player
"""

import os
import sqlite3

# Database paths
BASE_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
MUSIC_DB_PATH = os.path.join(BASE_DATA_DIR, "jukebox.db")
CD_DB_PATH = os.path.join(BASE_DATA_DIR, "cd_database", "musicbrainz.db")

# Database initialization
DB_TIMEOUT = 5.0  # SQLite timeout in seconds
DB_ISOLATION_LEVEL = None  # Autocommit mode

# Schema version for migrations
SCHEMA_VERSION = 1

# Tables for music metadata
TABLES = {
    "albums": """
        CREATE TABLE IF NOT EXISTS albums (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            year INTEGER,
            genre TEXT,
            album_art_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(title, artist)
        )
    """,
    
    "playlists": """
        CREATE TABLE IF NOT EXISTS playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    "playlist_tracks": """
        CREATE TABLE IF NOT EXISTS playlist_tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            playlist_id INTEGER NOT NULL,
            track_path TEXT NOT NULL,
            track_order INTEGER,
            FOREIGN KEY(playlist_id) REFERENCES playlists(id) ON DELETE CASCADE
        )
    """,
    
    "rfid_tags": """
        CREATE TABLE IF NOT EXISTS rfid_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_id TEXT NOT NULL UNIQUE,
            tag_type TEXT,
            content_type TEXT,
            content_id INTEGER,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    "cds": """
        CREATE TABLE IF NOT EXISTS cds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            toc_fingerprint TEXT UNIQUE,
            album_title TEXT,
            artist TEXT,
            year INTEGER,
            genre TEXT,
            album_art_path TEXT,
            track_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    "cd_tracks": """
        CREATE TABLE IF NOT EXISTS cd_tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cd_id INTEGER NOT NULL,
            track_number INTEGER,
            track_title TEXT,
            track_duration INTEGER,
            FOREIGN KEY(cd_id) REFERENCES cds(id) ON DELETE CASCADE
        )
    """,
}

print(f"Database Configuration loaded")
print(f"Music DB: {MUSIC_DB_PATH}")
print(f"CD Database: {CD_DB_PATH}")
