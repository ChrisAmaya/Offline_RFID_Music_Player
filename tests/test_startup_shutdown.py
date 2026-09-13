import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.multi_tag_rfid_playlist_controls import RFIDTagMonitor, stop_player
from src.rfid_playlist_controls import build_mpv_command


class FakeReader:
    def read(self):
        time.sleep(0.01)
        return 123, ""


class FakeProcess:
    def __init__(self):
        self.returncode = None
        self.terminate_called = False
        self.kill_called = False

    def poll(self):
        return self.returncode

    def terminate(self):
        self.terminate_called = True
        self.returncode = 0

    def wait(self, timeout=None):
        return self.returncode

    def kill(self):
        self.kill_called = True
        self.returncode = -9


class StartupShutdownTests(unittest.TestCase):
    def test_mpv_command_detaches_from_terminal_input(self):
        command = build_mpv_command("/tmp/tracklist.txt", "/tmp/test-mpv.sock")
        self.assertIn("--no-input-terminal", command)
        self.assertIn("--input-ipc-server=/tmp/test-mpv.sock", command)

    def test_rfid_monitor_stops(self):
        monitor = RFIDTagMonitor(FakeReader())
        monitor.start()
        self.assertEqual(monitor.get(timeout=1), (123, ""))
        monitor.stop()
        self.assertFalse(monitor._thread.is_alive())

    def test_stop_player_terminates_process_and_removes_socket(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            socket_path = Path(temp_dir) / "rfid-mpv.sock"
            socket_path.write_text("placeholder", encoding="utf-8")
            process = FakeProcess()

            with patch("src.multi_tag_rfid_playlist_controls.SOCKET_PATH", str(socket_path)):
                stop_player(process)

            self.assertTrue(process.terminate_called)
            self.assertFalse(socket_path.exists())


if __name__ == "__main__":
    unittest.main()
