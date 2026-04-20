import time
import sqlite3
import os
import random
from src.db.tracker import ApplicationTracker

def setup_mock_db(db_path, num_records):
    if os.path.exists(db_path):
        os.remove(db_path)

    tracker = ApplicationTracker(db_path=db_path)

    # Bulk insert mock data
    urls = [f"https://example.com/job/{i}" for i in range(num_records)]

    print(f"Inserting {num_records} mock records into the database...")
    with tracker._get_connection() as conn:
        cursor = conn.cursor()
        data = [(url, "MockCompany", "MockTitle", "APPLIED", 8.0, "Mock notes") for url in urls]
        cursor.executemany('''
            INSERT INTO applications (job_url, company, title, status, score, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', data)
        conn.commit()
    return tracker, urls

def benchmark_n_plus_1(tracker, test_urls):
    start_time = time.time()
    found_count = 0
    for url in test_urls:
        if tracker.has_applied(url):
            found_count += 1
    end_time = time.time()
    return end_time - start_time, found_count

def get_applied_urls_optimized(tracker, job_urls):
    """Temporary optimized function for benchmarking"""
    applied_urls = set()
    # SQLite has a limit on variables in an IN clause, typically 999
    # Chunk the URLs
    chunk_size = 900
    for i in range(0, len(job_urls), chunk_size):
        chunk = job_urls[i:i + chunk_size]
        placeholders = ','.join(['?'] * len(chunk))
        with tracker._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT job_url FROM applications WHERE job_url IN ({placeholders})', chunk)
            results = cursor.fetchall()
            applied_urls.update(row[0] for row in results)
    return applied_urls

def benchmark_optimized(tracker, test_urls):
    start_time = time.time()
    found_count = 0

    # The optimization
    applied_urls = get_applied_urls_optimized(tracker, test_urls)

    for url in test_urls:
        if url in applied_urls:
            found_count += 1

    end_time = time.time()
    return end_time - start_time, found_count

def run_benchmark():
    db_path = "config/benchmark.db"
    db_size = 10000
    test_size = 2000

    # Setup
    tracker, db_urls = setup_mock_db(db_path, db_size)

    # Generate test workload: 50% existing in DB, 50% new
    test_urls = random.sample(db_urls, test_size // 2)
    test_urls.extend([f"https://example.com/new_job/{i}" for i in range(test_size // 2)])
    random.shuffle(test_urls)

    print(f"\nBenchmarking with {test_size} job evaluations against a DB of {db_size} records...")

    # Run N+1
    time_n_plus_1, count1 = benchmark_n_plus_1(tracker, test_urls)
    print(f"N+1 Approach:      {time_n_plus_1:.4f} seconds (Found {count1})")

    # Run Optimized
    time_optimized, count2 = benchmark_optimized(tracker, test_urls)
    print(f"Optimized Approach: {time_optimized:.4f} seconds (Found {count2})")

    # Verify correctness
    assert count1 == count2, "Mismatch in results!"

    speedup = time_n_plus_1 / time_optimized if time_optimized > 0 else float('inf')
    print(f"\nSpeedup: {speedup:.2f}x faster")

    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)

if __name__ == "__main__":
    run_benchmark()
