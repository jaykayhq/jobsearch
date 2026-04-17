import unittest
import os
import tempfile
import sqlite3
from src.db.tracker import ApplicationTracker

class TestApplicationTracker(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_applications.db")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_init_creates_directory_and_db(self):
        # Ensure the directory doesn't exist yet
        nested_db_path = os.path.join(self.temp_dir.name, "nested", "dir", "test.db")
        self.assertFalse(os.path.exists(os.path.dirname(nested_db_path)))

        tracker = ApplicationTracker(db_path=nested_db_path)

        self.assertTrue(os.path.exists(os.path.dirname(nested_db_path)))
        self.assertTrue(os.path.exists(nested_db_path))

        # Verify schema
        conn = sqlite3.connect(nested_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='applications'")
        self.assertIsNotNone(cursor.fetchone())
        conn.close()

    def test_init_with_memory_db(self):
        tracker = ApplicationTracker(db_path=":memory:")
        self.assertEqual(tracker.db_path, ":memory:")

        # We can query the in-memory db
        with tracker._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='applications'")
            self.assertIsNotNone(cursor.fetchone())

    def test_has_applied(self):
        tracker = ApplicationTracker(db_path=":memory:")
        job_url = "https://example.com/job/1"

        self.assertFalse(tracker.has_applied(job_url))

        tracker.log_application(job_url, "TestCorp", "Software Engineer", "APPLIED", 9.5, "Good fit")
        self.assertTrue(tracker.has_applied(job_url))

    def test_log_application_inserts_and_updates(self):
        tracker = ApplicationTracker(db_path=":memory:")
        job_url = "https://example.com/job/2"

        # Initial insert
        tracker.log_application(job_url, "TestCorp", "Developer", "SKIPPED_LOW_SCORE", 4.0, "Not a fit")

        with tracker._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status, score, notes FROM applications WHERE job_url = ?", (job_url,))
            row = cursor.fetchone()
            self.assertEqual(row, ("SKIPPED_LOW_SCORE", 4.0, "Not a fit"))

        # Update (Upsert)
        tracker.log_application(job_url, "TestCorp", "Developer", "APPLIED", 8.5, "Applied after review")

        with tracker._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status, score, notes FROM applications WHERE job_url = ?", (job_url,))
            row = cursor.fetchone()
            self.assertEqual(row, ("APPLIED", 8.5, "Applied after review"))

    def test_get_stats(self):
        tracker = ApplicationTracker(db_path=":memory:")

        # Empty stats
        self.assertEqual(tracker.get_stats(), {})

        tracker.log_application("url1", "C1", "T1", "APPLIED")
        tracker.log_application("url2", "C2", "T2", "APPLIED")
        tracker.log_application("url3", "C3", "T3", "SKIPPED_LOW_SCORE")
        tracker.log_application("url4", "C4", "T4", "ERROR")

        stats = tracker.get_stats()
        self.assertEqual(stats, {
            "APPLIED": 2,
            "SKIPPED_LOW_SCORE": 1,
            "ERROR": 1
        })

if __name__ == '__main__':
    unittest.main()
