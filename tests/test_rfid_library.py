import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.rfid_library import normalize_tag_id, playlist_for_tag, register_tag


class RFIDLibraryTests(unittest.TestCase):
    def test_normalizes_decimal_and_hex_tag_forms_to_same_key(self):
        self.assertEqual(normalize_tag_id("35:49:C0:A4"), normalize_tag_id("0x3549C0A4"))
        self.assertEqual(normalize_tag_id("35:49:C0:A4"), str(int("3549C0A4", 16)))

    def test_registers_tag_and_generates_alphabetical_tracklist(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            album_dir = root / "Mac Miller"
            album_dir.mkdir()
            (album_dir / "Mac Miller-Zeta.mp3").write_bytes(b"z")
            (album_dir / "Mac Miller-Alpha.mp3").write_bytes(b"a")
            db_path = root / "library.db"

            tracklist = register_tag("12345", album_dir, db_path)

            self.assertEqual(
                tracklist.read_text(encoding="utf-8").splitlines(),
                [str((album_dir / "Mac Miller-Alpha.mp3").resolve()), str((album_dir / "Mac Miller-Zeta.mp3").resolve())],
            )
            self.assertEqual(playlist_for_tag("12345", db_path), tracklist)

            with sqlite3.connect(db_path) as db:
                self.assertEqual(db.execute("SELECT COUNT(*) FROM tag_mappings").fetchone()[0], 1)

    def test_registering_same_tag_updates_its_playlist(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first = root / "First"
            second = root / "Second"
            first.mkdir()
            second.mkdir()
            (first / "one.mp3").write_bytes(b"1")
            (second / "two.mp3").write_bytes(b"2")
            db_path = root / "library.db"

            register_tag("123456", first, db_path)
            second_tracklist = register_tag("123456", second, db_path)

            self.assertEqual(playlist_for_tag("123456", db_path), second_tracklist)
            with sqlite3.connect(db_path) as db:
                self.assertEqual(db.execute("SELECT COUNT(*) FROM tag_mappings").fetchone()[0], 1)

    def test_registering_refreshes_stale_tracklist_paths(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            album_dir = Path(temp_dir) / "Album With Spaces"
            album_dir.mkdir()
            track = album_dir / "01 Track With Spaces.mp3"
            track.write_bytes(b"audio")
            stale = album_dir / "tracklist.txt"
            stale.write_text("/old/location/01 Track With Spaces.mp3\n", encoding="utf-8")

            register_tag("789", album_dir, Path(temp_dir) / "library.db")

            self.assertEqual(stale.read_text(encoding="utf-8").splitlines(), [str(track.resolve())])


if __name__ == "__main__":
    unittest.main()
