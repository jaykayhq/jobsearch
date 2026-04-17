import os
import json
from mistralai import Mistral
from dotenv import load_dotenv

class AIClient:
    def __init__(self, profile=None):
        load_dotenv()
        self.api_key = os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY environment variable not found.")

        # Initialize the Mistral client
        self.client = Mistral(api_key=self.api_key)
        self.model = "mistral-large-latest" # Best for reasoning and complex text generation

        # Load user profile for context
        self.profile = profile if profile is not None else {}

    def _get_json_completion(self, prompt: str) -> dict:
        """Helper to get guaranteed JSON output from Mistral."""
        messages = [
            {"role": "system", "content": "You are a professional career counselor and expert technical recruiter. You always return valid JSON."},
            {"role": "user", "content": prompt}
        ]

        try:
            chat_response = self.client.chat.complete(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"}
            )
            content = chat_response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print(f"AI API Error: {e}")
            return {}

    def _get_text_completion(self, prompt: str) -> str:
         """Helper to get text output from Mistral."""
         messages = [
             {"role": "system", "content": "You are a professional career counselor and expert technical recruiter."},
             {"role": "user", "content": prompt}
         ]
         try:
             chat_response = self.client.chat.complete(
                 model=self.model,
                 messages=messages
             )
             return chat_response.choices[0].message.content
         except Exception as e:
             print(f"AI API Error: {e}")
             return ""


    def evaluate_job(self, job_title: str, job_description: str) -> dict:
        """
        Evaluate if a job is a good fit for the user.
        Returns a dictionary with 'score' (1-10) and 'reason'.
        """
        prompt = f"""
        Given the following user profile and job description, evaluate how well the user fits the job.

        User Profile (JSON): {json.dumps(self.profile.get('master_resume', {}))}
        User Preferences (JSON): {json.dumps(self.profile.get('job_preferences', {}))}

        Job Title: {job_title}
        Job Description: {job_description}

        Respond ONLY with a JSON object containing:
        - "score": An integer from 1 to 10 (10 being perfect match). Be realistic. Give heavy penalties for missing hard requirements (like specific years of experience or distinct tech stacks).
        - "reason": A brief 1-2 sentence explanation of why this score was given.
        """

        result = self._get_json_completion(prompt)
        return {"score": result.get("score", 0), "reason": result.get("reason", "Failed to evaluate")}

    def generate_cover_letter(self, job_title: str, company: str, job_description: str) -> str:
        """
        Generate a targeted cover letter based on the user profile and job description.
        """
        prompt = f"""
        Write a professional, concise, and highly targeted cover letter for the following job.

        Job Title: {job_title}
        Company: {company}
        Job Description Extracts: {job_description[:1000]}...

        My Profile:
        {json.dumps(self.profile.get('master_resume', {}))}

        My Name: {self.profile.get('personal_info', {}).get('first_name')} {self.profile.get('personal_info', {}).get('last_name')}
        My Email: {self.profile.get('personal_info', {}).get('email')}

        Guidelines:
        - Do not exceed 3 paragraphs.
        - Start directly with excitement for the role at the specific company.
        - Highlight 1-2 specific achievements from my profile that DIRECTLY relate to the job description.
        - Maintain a professional, confident, but not arrogant tone.
        - Do NOT invent any experience, metrics, or skills that are not in my profile.
        - Format it as plain text ready to be pasted into a form.
        """
        return self._get_text_completion(prompt)

    def answer_screening_questions(self, questions: list[str], job_description: str) -> dict:
        """
        Answer a list of dynamic screening questions found on an application form.
        Returns a dict mapping the original question to the generated answer.
        """
        prompt = f"""
        I am applying for a job. Here is the job description context:
        {job_description[:500]}...

        Here is my profile:
        {json.dumps(self.profile)}

        Please provide the best answers for the following application form screening questions based on my profile.
        Questions: {json.dumps(questions)}

        Guidelines:
        - Keep answers concise and professional.
        - If a question asks for years of experience with a tool, calculate it based on my resume dates or estimate conservatively. If I don't have it, say "0".
        - If a question asks about Visa sponsorship, use the 'job_preferences.visa_sponsorship_required' boolean.
        - Respond ONLY with a JSON object where the keys are the exact questions provided, and the values are the answers (strings or booleans).
        """
        return self._get_json_completion(prompt)
