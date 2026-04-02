import time
from src.ai.mistral_client import AIClient
from src.db.tracker import ApplicationTracker
from src.applier.browser import BrowserManager
from src.applier.greenhouse import GreenhouseApplier
from src.applier.lever import LeverApplier
from src.applier.linkedin_easy_apply import LinkedInEasyApply
from src.scraper.job_scraper import JobScraper

def main():
    print("Starting Auto Job Applier AI...")

    tracker = ApplicationTracker()
    try:
        ai = AIClient()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("Please check docs/SETUP.md for instructions.")
        return

    # 1. Discover Jobs
    print("\n[1] Discovering new jobs...")
    scraper = JobScraper()
    jobs = scraper.discover_jobs()
    print(f"Found {len(jobs)} potential jobs.")

    # 2. Filter & Evaluate
    print("\n[2] Evaluating Jobs...")
    jobs_to_apply = []
    for job in jobs:
        url = job['url']
        if tracker.has_applied(url):
            print(f"Skipping {url} (Already processed)")
            continue

        print(f"Evaluating: {job['title']} at {job['company']}")
        evaluation = ai.evaluate_job(job['title'], job['description'])
        score = evaluation.get('score', 0)
        reason = evaluation.get('reason', 'No reason provided')

        print(f" -> Score: {score}/10. Reason: {reason}")

        # Only apply if score is high enough
        if score >= 7:
            jobs_to_apply.append(job)
        else:
            tracker.log_application(url, job['company'], job['title'], 'SKIPPED_LOW_SCORE', score, reason)

    # 3. Apply
    if not jobs_to_apply:
        print("\nNo jobs met the criteria to apply.")
        return

    print(f"\n[3] Proceeding to apply to {len(jobs_to_apply)} jobs...")
    browser = BrowserManager(headless=False) # Set to False so you can watch it!
    browser.start()

    # Initialize specific appliers
    appliers = {
        'greenhouse': GreenhouseApplier(browser, ai),
        'lever': LeverApplier(browser, ai),
        'linkedin': LinkedInEasyApply(browser, ai)
    }

    for job in jobs_to_apply:
        url = job['url']
        source = job['source']

        print(f"\nApplying to: {job['title']} at {job['company']}")

        # Optional: Generate a custom cover letter
        print(" -> Generating tailored cover letter...")
        cover_letter = ai.generate_cover_letter(job['title'], job['company'], job['description'])
        # (This cover letter would be passed to the applier or saved to a file)

        applier = appliers.get(source)
        if not applier:
             print(f" -> No applier supported for source: {source}")
             tracker.log_application(url, job['company'], job['title'], 'ERROR', notes=f"Unsupported source: {source}")
             continue

        success = applier.apply(url)

        if success:
             tracker.log_application(url, job['company'], job['title'], 'APPLIED', notes="Successfully filled form")
             print(" -> Application submitted successfully!")
        else:
             tracker.log_application(url, job['company'], job['title'], 'FAILED', notes="Form filling failed")
             print(" -> Application failed.")

        time.sleep(2) # Brief pause between applications

    browser.stop()
    print("\nRun complete. Check database for statistics.")

if __name__ == "__main__":
    main()
