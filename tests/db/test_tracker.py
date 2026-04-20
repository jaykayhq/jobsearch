import unittest
import os
import tempfile
import sqlite3
import sqlite3
import tempfile
import os
import sys
from unittest.mock import patch

# Ensure src can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.db.tracker import ApplicationTracker

class TestApplicationTracker(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_applications.db")
        self.tracker = ApplicationTracker(db_path=self.db_path)

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
    def test_log_application_success(self):
        job_url = "https://example.com/job/1"
        company = "Example Corp"
        title = "Software Engineer"
        status = "APPLIED"
        score = 8.5
        notes = "Looks like a great fit"

        # Log the application
        self.tracker.log_application(job_url, company, title, status, score, notes)

        # Verify it was written to the database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT job_url, company, title, status, score, notes FROM applications WHERE job_url = ?", (job_url,))
            row = cursor.fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(row[0], job_url)
        self.assertEqual(row[1], company)
        self.assertEqual(row[2], title)
        self.assertEqual(row[3], status)
        self.assertEqual(row[4], score)
        self.assertEqual(row[5], notes)

    def test_log_application_update_on_conflict(self):
        job_url = "https://example.com/job/1"

        # Insert initial record
        self.tracker.log_application(job_url, "Company", "Title", "EVALUATING", 5.0, "Initial notes")

        # Update record
        self.tracker.log_application(job_url, "Company", "Title", "APPLIED", 9.0, "Updated notes")

        # Verify it was updated, not duplicated
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status, score, notes FROM applications WHERE job_url = ?", (job_url,))
            rows = cursor.fetchall()

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], "APPLIED")
        self.assertEqual(rows[0][1], 9.0)
        self.assertEqual(rows[0][2], "Updated notes")

    @patch('src.db.tracker.sqlite3.connect')
    def test_log_application_database_error(self, mock_connect):
        # Setup mock to raise sqlite3.Error
        mock_connect.side_effect = sqlite3.Error("Mock database error")

        # This shouldn't raise an exception because log_application catches sqlite3.Error
        try:
            self.tracker.log_application("url", "company", "title", "status")
        except sqlite3.Error:
            self.fail("log_application raised sqlite3.Error unexpectedly!")

if __name__ == '__main__':
    unittest.main()
