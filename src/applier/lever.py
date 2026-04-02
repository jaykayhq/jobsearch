from src.applier.browser import BrowserManager
from src.ai.mistral_client import AIClient
import yaml

class LeverApplier:
    def __init__(self, browser: BrowserManager, ai: AIClient, profile_path="config/user_profile.yaml"):
        self.browser = browser
        self.ai = ai
        with open(profile_path, 'r') as f:
            self.profile = yaml.safe_load(f)

    def apply(self, job_url: str) -> bool:
        """
        Attempts to fill out and submit a Lever application form.
        Returns True if successful, False otherwise.
        """
        page = self.browser.page
        try:
            # Lever application form is often on a separate URL (/apply)
            if not job_url.endswith('/apply'):
                 job_url = f"{job_url}/apply"

            page.goto(job_url, timeout=30000)

            # Wait for main application form
            if not page.is_visible('#application-form', timeout=10000):
                print(f"Failed to find Lever form on {job_url}")
                return False

            personal = self.profile.get('personal_info', {})

            # Fill basic info
            if page.is_visible('input[name="name"]'):
                full_name = f"{personal.get('first_name', '')} {personal.get('last_name', '')}"
                self.browser.human_typing('input[name="name"]', full_name)
            if page.is_visible('input[name="email"]'):
                self.browser.human_typing('input[name="email"]', personal.get('email', ''))
            if page.is_visible('input[name="phone"]'):
                self.browser.human_typing('input[name="phone"]', personal.get('phone', ''))
            if page.is_visible('input[name="org"]'):
                experience = self.profile.get('master_resume', {}).get('experience', [])
                current_company = experience[0].get('company', '') if experience else ''
                self.browser.human_typing('input[name="org"]', current_company)

            # Social links
            if page.is_visible('input[name="urls[LinkedIn]"]'):
                self.browser.human_typing('input[name="urls[LinkedIn]"]', personal.get('linkedin', ''))
            if page.is_visible('input[name="urls[GitHub]"]'):
                self.browser.human_typing('input[name="urls[GitHub]"]', personal.get('github', ''))
            if page.is_visible('input[name="urls[Portfolio]"]'):
                self.browser.human_typing('input[name="urls[Portfolio]"]', personal.get('website', ''))

            # Handle Resume Upload (Placeholder)
            # if page.is_visible('input[name="resume"]'):
            #    page.set_input_files('input[name="resume"]', 'path/to/tailored_resume.pdf')

            # Extract custom questions
            print(" -> Extracting custom questions...")
            custom_questions_locators = page.locator('div.application-question').all()
            questions_to_answer = []
            question_mapping = {}

            for q_locator in custom_questions_locators:
                 label = q_locator.locator('div.application-label').first
                 if label.is_visible():
                     text = label.inner_text().strip()
                     if text:
                          questions_to_answer.append(text)
                          question_mapping[text] = q_locator

            if questions_to_answer:
                 print(f" -> Found {len(questions_to_answer)} questions. Asking AI...")
                 answers = self.ai.answer_screening_questions(questions_to_answer, "Lever Job Application")

                 for q_text, answer in answers.items():
                      if q_text in question_mapping:
                           loc = question_mapping[q_text]
                           input_field = loc.locator('input[type="text"], textarea')
                           if input_field.count() > 0:
                                input_field.first.fill(str(answer))

                           # Handle single checkboxes (e.g. Yes/No/Agreement)
                           checkbox_fields = loc.locator('input[type="checkbox"]')
                           if checkbox_fields.count() > 0:
                               # If answer looks affirmative, check the first box
                               if str(answer).lower() in ['yes', 'true', 'agree', '1']:
                                   checkbox_fields.first.check()

                           # Note: Dropdowns on Lever can be complex custom elements (divs mimicking selects)
                           # Robust handling requires specific inspection of those elements.


            # Submitting (Commented out to prevent accidental submissions during testing)
            # self.browser.human_click('.postings-btn.template-btn-submit')

            print(f"Successfully filled Lever form for {job_url}")
            return True

        except Exception as e:
            print(f"Error applying to Lever ({job_url}): {e}")
            return False
