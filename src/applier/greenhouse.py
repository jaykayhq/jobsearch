from src.applier.browser import BrowserManager
from src.ai.mistral_client import AIClient

class GreenhouseApplier:
    def __init__(self, browser: BrowserManager, ai: AIClient):
        self.browser = browser
        self.ai = ai
        self.profile = self.ai.profile

    def apply(self, job_url: str) -> bool:
        """
        Attempts to fill out and submit a Greenhouse application form.
        Returns True if successful, False otherwise.
        """
        page = self.browser.page
        try:
            page.goto(job_url, timeout=30000)

            # Wait for main application form
            if not page.is_visible('#application_form', timeout=10000):
                print(f"Failed to find Greenhouse form on {job_url}")
                return False

            personal = self.profile.get('personal_info', {})

            # Fill basic info
            if page.is_visible('#first_name'):
                self.browser.human_typing('#first_name', personal.get('first_name', ''))
            if page.is_visible('#last_name'):
                self.browser.human_typing('#last_name', personal.get('last_name', ''))
            if page.is_visible('#email'):
                self.browser.human_typing('#email', personal.get('email', ''))
            if page.is_visible('#phone'):
                self.browser.human_typing('#phone', personal.get('phone', ''))

            # Social links
            if page.is_visible('input[autocomplete="custom-question-linkedin-profile"]'):
                self.browser.human_typing('input[autocomplete="custom-question-linkedin-profile"]', personal.get('linkedin', ''))
            if page.is_visible('input[autocomplete="custom-question-website"]'):
                self.browser.human_typing('input[autocomplete="custom-question-website"]', personal.get('website', ''))

            # Handle Resume Upload (Placeholder - requires local file path)
            # if page.is_visible('input[type="file"][data-source="resume"]'):
            #    page.set_input_files('input[type="file"][data-source="resume"]', 'path/to/tailored_resume.pdf')

            # Extract and answer custom screening questions
            print(" -> Extracting custom questions...")
            custom_questions_locators = page.locator('div.custom_question').all()
            questions_to_answer = []
            question_mapping = {} # Map question text to locator

            for q_locator in custom_questions_locators:
                 label = q_locator.locator('label').first
                 if label.is_visible():
                     text = label.inner_text().strip().split('\n')[0] # Get just the question text
                     if text:
                          questions_to_answer.append(text)
                          question_mapping[text] = q_locator

            if questions_to_answer:
                 print(f" -> Found {len(questions_to_answer)} questions. Asking AI...")
                 # To accurately answer, we'd ideally pass the job description. We'll pass a placeholder here,
                 # but in a full implementation, you'd fetch the job description text from the page first.
                 job_desc = page.locator('#content').inner_text() if page.is_visible('#content') else "Generic Job"

                 answers = self.ai.answer_screening_questions(questions_to_answer, job_desc)

                 for q_text, answer in answers.items():
                      if q_text in question_mapping:
                           loc = question_mapping[q_text]
                           # Try to find input type and fill
                           input_field = loc.locator('input[type="text"], textarea')
                           if input_field.count() > 0:
                                input_field.first.fill(str(answer))

                           # Handling dropdowns/selects is more complex and depends on the specific structure
                           select_field = loc.locator('select')
                           if select_field.count() > 0:
                                # Very basic attempt to select by text
                                try:
                                    select_field.first.select_option(label=str(answer))
                                except:
                                    pass # Could not find exact match


            # Submitting (Commented out to prevent accidental submissions during testing)
            # self.browser.human_click('#submit_app')

            print(f"Successfully filled Greenhouse form for {job_url}")
            return True

        except Exception as e:
            print(f"Error applying to Greenhouse ({job_url}): {e}")
            return False
