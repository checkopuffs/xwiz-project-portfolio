"""Offline unit tests: no Telegram/Ollama calls or network connections."""
import importlib.util
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

os.environ.setdefault('TELEGRAM_BOT_TOKEN', 'testing-only-not-a-real-token')
os.environ.setdefault('TELEGRAM_ALLOWED_USER_ID', '123456789')
os.environ.setdefault('XWIZ_MONITOR_TARGETS', '[]')

MOD = Path(__file__).resolve().parents[1] / 'xwiz_bot.py'
spec = importlib.util.spec_from_file_location('xwiz_bot', MOD)
bot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bot)

class ReminderTests(unittest.TestCase):
    def test_clock(self):
        self.assertEqual(bot.parse_clock('6pm'), (18, 0))
        self.assertEqual(bot.parse_clock('12am'), (0, 0))
        self.assertEqual(bot.parse_clock('18:45'), (18, 45))

    def test_relative_reminder(self):
        now = datetime(2026, 11, 18, 12, 0, tzinfo=ZoneInfo('America/Los_Angeles'))
        due, content = bot.parse_reminder('in 2m Check backups', now=now)
        self.assertEqual(content, 'Check backups')
        self.assertEqual(int((due - now).total_seconds()), 120)

    def test_bad_time(self):
        with self.assertRaises(ValueError):
            bot.parse_clock('25:00')

class MonitorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.conn = sqlite3.connect(Path(self.tmp.name) / 'test.db')
        self.conn.execute('CREATE TABLE monitor_targets (target_key TEXT PRIMARY KEY, status TEXT NOT NULL DEFAULT "unknown", failures INTEGER NOT NULL DEFAULT 0, successes INTEGER NOT NULL DEFAULT 0, checked_utc TEXT, changed_utc TEXT)')
        self.conn.execute('CREATE TABLE monitor_alerts (id INTEGER PRIMARY KEY, message TEXT NOT NULL, created_utc TEXT NOT NULL, sent_utc TEXT)')
        self.target = ('local', 'Example Host', 'example.invalid', 22, 'SSH')

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def test_transitions_and_no_duplicate_alerts(self):
        for _ in range(2):
            self.assertIsNone(bot.record_probe(self.conn, self.target, False))
        down = bot.record_probe(self.conn, self.target, False)
        self.assertIn('alert', down.lower())
        self.assertIsNone(bot.record_probe(self.conn, self.target, False))
        self.assertIsNone(bot.record_probe(self.conn, self.target, True))
        up = bot.record_probe(self.conn, self.target, True)
        self.assertIn('recovery', up.lower())
        self.assertEqual(self.conn.execute('SELECT count(*) FROM monitor_alerts').fetchone()[0], 2)

if __name__ == '__main__':
    unittest.main()
