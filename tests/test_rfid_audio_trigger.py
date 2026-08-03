import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import rfid_audio_trigger


class RFIDAudioTriggerTests(unittest.TestCase):
    def test_wait_for_rfid_and_play_uses_mpv_with_samplerate(self):
        class FakeReader:
            def __init__(self):
                self.calls = 0

            def read(self):
                self.calls += 1
                if self.calls == 1:
                    return 123, "sample-text"
                raise RuntimeError("stop")

        fake_reader = FakeReader()

        with patch("subprocess.Popen") as mock_popen:
            with patch("time.sleep", return_value=None):
                result = rfid_audio_trigger.wait_for_rfid_and_play(
                    "/tmp/test.mp3",
                    reader_factory=lambda: fake_reader,
                )

        self.assertEqual(result["tag_id"], 123)
        self.assertEqual(result["text"], "sample-text")
        mock_popen.assert_called_once()
        command = mock_popen.call_args[0][0]
        self.assertIn("mpv", command[0])
        self.assertIn("--audio-samplerate=48000", command)
        self.assertIn("/tmp/test.mp3", command)


if __name__ == "__main__":
    unittest.main()
