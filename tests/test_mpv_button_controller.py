import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.button_handler import ButtonHandler
from src.mpv_button_controller import build_mpv_command, button_command_for


class MPVButtonControllerTests(unittest.TestCase):
    def test_build_mpv_command_uses_playlist_and_ipc(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            playlist = Path(tmpdir) / "playlist.txt"
            playlist.write_text("/tmp/track1.mp3\n", encoding="utf-8")
            cmd = build_mpv_command(str(playlist), socket_path="/tmp/mpv.sock")

            self.assertIn("mpv", cmd)
            self.assertIn("--playlist", cmd)
            self.assertIn(str(playlist), cmd)
            self.assertIn("--input-ipc-server=/tmp/mpv.sock", cmd)
            self.assertIn("--audio-samplerate=48000", cmd)

    def test_button_command_for_returns_expected_mpv_command(self):
        self.assertEqual(button_command_for("Play/Pause"), ["cycle", "pause"])
        self.assertEqual(button_command_for("Next"), ["playlist-next"])
        self.assertEqual(button_command_for("Previous"), ["playlist-prev"])
        self.assertEqual(button_command_for("Shuffle"), ["playlist-shuffle"])

    def test_button_handler_registers_buttons_without_gpio(self):
        handler = ButtonHandler()
        handler.register_button(1, 26, "Play/Pause")
        self.assertIn(1, handler.buttons)


if __name__ == "__main__":
    unittest.main()
