import sqlite3
import datetime
from pathlib import Path
import os

class ApplicationTracker:
    def __init__(self, db_path="config/applications.db"):
        self.db_path = db_path
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._initialize_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _initialize_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_url TEXT UNIQUE NOT NULL,
                    company TEXT NOT NULL,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    score REAL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                )
            ''')
            conn.commit()

    def has_applied(self, job_url: str) -> bool:
        """Check if we have already evaluated or applied to this job URL."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM applications WHERE job_url = ?', (job_url,))
            return cursor.fetchone() is not None

    def get_applied_urls(self, job_urls: list[str]) -> set[str]:
        """Check a list of URLs and return a set of those we have already applied to."""
        if not job_urls:
            return set()

        applied_urls = set()
        chunk_size = 900  # Safe limit for SQLite placeholders

        with self._get_connection() as conn:
            cursor = conn.cursor()
            for i in range(0, len(job_urls), chunk_size):
                chunk = job_urls[i:i + chunk_size]
                placeholders = ','.join(['?'] * len(chunk))
                cursor.execute(f'SELECT job_url FROM applications WHERE job_url IN ({placeholders})', chunk)
                applied_urls.update(row[0] for row in cursor.fetchall())

        return applied_urls

    def log_application(self, job_url: str, company: str, title: str, status: str, score: float = None, notes: str = ""):
        """
        Log a job evaluation or application.
        Status can be: 'APPLIED', 'SKIPPED_LOW_SCORE', 'FAILED', 'ERROR'
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO applications (job_url, company, title, status, score, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(job_url) DO UPDATE SET
                        status = excluded.status,
                        score = excluded.score,
                        notes = excluded.notes,
                        applied_at = CURRENT_TIMESTAMP
                ''', (job_url, company, title, status, score, notes))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database error logging {job_url}: {e}")

    def get_stats(self):
        """Get basic statistics about applications."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT status, COUNT(*) FROM applications GROUP BY status')
            return dict(cursor.fetchall())
