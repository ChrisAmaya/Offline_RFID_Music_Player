import sys
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.multi_tag_rfid_playlist_controls import RFIDTagMonitor


class FakeReader:
    def __init__(self):
        self.values = [(1, ""), (1, ""), (2, "")]

    def read(self):
        time.sleep(0.01)
        if self.values:
            return self.values.pop(0)
        time.sleep(0.05)
        return 2, ""


class MultiTagRuntimeTests(unittest.TestCase):
    def test_monitor_debounces_same_tag_and_reports_new_tag(self):
        monitor = RFIDTagMonitor(FakeReader())
        monitor.start()
        try:
            self.assertEqual(monitor.get(timeout=1), (1, ""))
            self.assertEqual(monitor.get(timeout=1), (2, ""))
        finally:
            monitor.stop()


if __name__ == "__main__":
    unittest.main()
