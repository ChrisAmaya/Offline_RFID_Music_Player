import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

module_path = Path(__file__).resolve().parents[1] / "test-rfid-play.py"
spec = importlib.util.spec_from_file_location("rfid_play_test_module", module_path)
rfid_play = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rfid_play)

create_album_mapping = rfid_play.create_album_mapping
init_db = rfid_play.init_db


class AlbumOrderTests(unittest.TestCase):
    def test_create_album_mapping_uses_provided_track_order(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            music_dir = Path(tmpdir)
            files = [
                "What's the Use-.mp3",
                "Hurt Feelings.mp3",
                "Come Back to Earth.mp3",
            ]
            for name in files:
                (music_dir / name).write_bytes(b"audio")

            db_path = music_dir / "test.db"
            conn = init_db(db_path)
            content_id = create_album_mapping(
                conn,
                "tag-1",
                "Test Album",
                music_dir,
                media_root=music_dir,
                track_order=["Come Back to Earth.mp3", "Hurt Feelings.mp3", "What's the Use-.mp3"],
            )

            rows = conn.execute(
                "SELECT path, title FROM content_entries WHERE content_id = ? ORDER BY sort_order, id",
                (content_id,),
            ).fetchall()

            self.assertEqual([row[0] for row in rows], [
                "Come Back to Earth.mp3",
                "Hurt Feelings.mp3",
                "What's the Use-.mp3",
            ])

    def test_create_album_mapping_matches_artist_prefixed_filenames(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            music_dir = Path(tmpdir)
            files = [
                "Mac Miller-What's the Use-.mp3",
                "Mac Miller-Hurt Feelings.mp3",
                "Mac Miller-Come Back to Earth.mp3",
            ]
            for name in files:
                (music_dir / name).write_bytes(b"audio")

            db_path = music_dir / "test.db"
            conn = init_db(db_path)
            content_id = create_album_mapping(
                conn,
                "tag-2",
                "Test Album",
                music_dir,
                media_root=music_dir,
                track_order=["Come Back to Earth.mp3", "Hurt Feelings.mp3", "What's the Use-.mp3"],
            )

            rows = conn.execute(
                "SELECT path, title FROM content_entries WHERE content_id = ? ORDER BY sort_order, id",
                (content_id,),
            ).fetchall()

            self.assertEqual([row[0] for row in rows], [
                "Mac Miller-Come Back to Earth.mp3",
                "Mac Miller-Hurt Feelings.mp3",
                "Mac Miller-What's the Use-.mp3",
            ])


if __name__ == "__main__":
    unittest.main()
