from src.applier.browser import BrowserManager
from src.ai.mistral_client import AIClient
import yaml
import time

class LinkedInEasyApply:
    def __init__(self, browser: BrowserManager, ai: AIClient, profile_path="config/user_profile.yaml"):
        self.browser = browser
        self.ai = ai
        with open(profile_path, 'r') as f:
            self.profile = yaml.safe_load(f)

    def apply(self, job_url: str) -> bool:
        """
        Attempts to complete a LinkedIn Easy Apply workflow.
        Returns True if successful, False otherwise.
        """
        page = self.browser.page
        try:
            page.goto(job_url, timeout=30000)

            # Note: LinkedIn requires login context. For true automation, you must
            # either manually log in first and save cookies, or automate the login
            # process securely (handling 2FA, captchas, etc). This is a framework.

            # Wait for Easy Apply button
            easy_apply_selector = 'button.jobs-apply-button'
            if not page.is_visible(easy_apply_selector, timeout=10000):
                print(f"Failed to find Easy Apply button on {job_url}. Might not be Easy Apply or not logged in.")
                return False

            self.browser.human_click(easy_apply_selector)
            time.sleep(2) # Wait for modal to load

            # LinkedIn's Easy Apply modal is a multi-step form
            # We must iterate through "Next" buttons until we see "Submit application"
            max_steps = 15
            for step in range(max_steps):
                # 1. Fill visible fields (phone, text inputs, radio buttons)
                #    Here, extract label texts and use AI to generate answers or
                #    pull from config.

                # 2. Upload resume if prompted

                # 3. Handle specific form types (dropdowns, multi-select)

                # Find the primary action button (Next, Review, Submit)
                next_button = page.locator('button:has-text("Next"), button:has-text("Review")').first
                submit_button = page.locator('button:has-text("Submit application")').first

                if submit_button.is_visible():
                    print("Reached Submit Step!")
                    # Uncomment to submit
                    # self.browser.human_click(submit_button)
                    return True

                if next_button.is_visible():
                    self.browser.human_click(next_button)
                    time.sleep(2) # Wait for next page transition
                else:
                    print(f"Failed to progress Easy Apply form on {job_url} at step {step}")
                    break

            return False

        except Exception as e:
            print(f"Error applying via LinkedIn Easy Apply ({job_url}): {e}")
            return False
