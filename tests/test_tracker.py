import unittest
import os
import tempfile
import sqlite3
from src.db.tracker import ApplicationTracker

class TestApplicationTracker(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for the database
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_applications.db")
        self.tracker = ApplicationTracker(db_path=self.db_path)

    def tearDown(self):
        # Clean up the temporary directory and its contents
        self.temp_dir.cleanup()

    def test_log_application_success(self):
        # Log a new application
        job_url = "https://example.com/job/1"
        company = "TestCorp"
        title = "Software Engineer"
        status = "APPLIED"
        score = 8.5
        notes = "Looks like a great fit"

        self.tracker.log_application(job_url, company, title, status, score, notes)

        # Verify it was inserted into the database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT job_url, company, title, status, score, notes FROM applications")
            results = cursor.fetchall()

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], (job_url, company, title, status, score, notes))

    def test_log_application_update_on_conflict(self):
        # Log an initial application
        job_url = "https://example.com/job/2"
        self.tracker.log_application(job_url, "TechInc", "Data Scientist", "APPLIED", 7.0, "Initial notes")

        # Update the application
        new_status = "FAILED"
        new_score = 7.5
        new_notes = "Rejected after first round"

        self.tracker.log_application(job_url, "TechInc", "Data Scientist", new_status, new_score, new_notes)

        # Verify the record was updated, not duplicated
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT job_url, company, title, status, score, notes FROM applications")
            results = cursor.fetchall()

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], (job_url, "TechInc", "Data Scientist", new_status, new_score, new_notes))

if __name__ == '__main__':
    unittest.main()
