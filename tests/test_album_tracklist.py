import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.album_tracklist import build_tracklist_file


class AlbumTracklistTests(unittest.TestCase):
    def test_build_tracklist_uses_metadata_tracknumbers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            album_dir = Path(tmpdir)
            track1 = album_dir / "01-come-back.mp3"
            track2 = album_dir / "02-hurt-feelings.mp3"
            track1.write_bytes(b"dummy")
            track2.write_bytes(b"dummy")

            # Add real ID3-like tags using mutagen if available
            try:
                from mutagen.id3 import ID3, TIT2, TRCK

                id3 = ID3()
                id3.add(TIT2(encoding=3, text=["Come Back to Earth"]))
                id3.add(TRCK(encoding=3, text=["1"]))
                id3.save(track1)

                id3 = ID3()
                id3.add(TIT2(encoding=3, text=["Hurt Feelings"]))
                id3.add(TRCK(encoding=3, text=["2"]))
                id3.save(track2)
            except Exception:
                pass

            output_path = album_dir / "album-order.txt"
            result = build_tracklist_file(album_dir, output_path)

            self.assertEqual(result[0], str(track1.resolve()))
            self.assertEqual(result[1], str(track2.resolve()))
            self.assertTrue(output_path.exists())
            self.assertEqual(output_path.read_text().splitlines(), result)


if __name__ == "__main__":
    unittest.main()
