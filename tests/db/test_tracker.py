import unittest
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
