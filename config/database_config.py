"""
Database Configuration for RFID Music Player
"""

import os
import sqlite3

# Database paths
BASE_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
RFID_LIBRARY_DB_PATH = os.path.join(BASE_DATA_DIR, "rfid_library.db")

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
    
}

print(f"Database Configuration loaded")
print(f"RFID Library DB: {RFID_LIBRARY_DB_PATH}")
