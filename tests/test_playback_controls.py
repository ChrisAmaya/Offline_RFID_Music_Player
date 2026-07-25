import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

module_path = Path(__file__).resolve().parents[1] / "test-rfid-play.py"
spec = importlib.util.spec_from_file_location("rfid_play_test_module", module_path)
rfid_play = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rfid_play)


class PlaybackControllerTests(unittest.TestCase):
    def test_shuffle_uses_deterministic_order(self):
        controller = rfid_play.FFmpegPlaybackController(
            ["track-1.mp3", "track-2.mp3", "track-3.mp3"],
            shuffle=True,
            shuffle_seed=7,
        )

        self.assertEqual(controller.playlist, ["track-3.mp3", "track-1.mp3", "track-2.mp3"])

    def test_next_previous_wrap_and_toggle_pause(self):
        created = []

        class FakeProcess:
            def __init__(self, command):
                self.pid = 4242
                self.command = command
                created.append(command)

        controller = rfid_play.FFmpegPlaybackController(
            ["track-1.mp3", "track-2.mp3"],
            process_factory=lambda command: FakeProcess(command),
        )

        controller.play()
        self.assertEqual(controller.current_path, "track-1.mp3")

        controller.next_track()
        self.assertEqual(controller.current_path, "track-2.mp3")

        controller.previous_track()
        self.assertEqual(controller.current_path, "track-1.mp3")

        with patch.object(rfid_play.os, "kill") as mock_kill:
            controller.toggle_pause()
            self.assertTrue(controller.paused)
            controller.toggle_pause()
            self.assertFalse(controller.paused)

        self.assertEqual(mock_kill.call_count, 2)


if __name__ == "__main__":
    unittest.main()
