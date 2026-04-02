# Initial Setup

Follow these instructions to get the Auto Job Applier up and running.

## Prerequisites

- **Python 3.10+**: Ensure Python is installed on your system.
- **Node.js**: Required by Playwright to install browsers.
- **Mistral API Key**: You'll need a Mistral AI API key (from https://console.mistral.ai/) to power the job scoring, resume tailoring, and form filling.

## Installation

1. Clone the repository and navigate to the root directory.
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

## Configuration

### 1. Environment Variables (.env)
Create a `.env` file in the root directory and add your API keys:

```
MISTRAL_API_KEY=your_mistral_api_key_here
```

### 2. User Profile (config/user_profile.yaml)
Create `config/user_profile.yaml` to store your personal details, master resume, contact info, and job preferences. This file powers the AI personalization and form auto-fill.

Example format:

```yaml
personal_info:
  first_name: John
  last_name: Doe
  email: john.doe@example.com
  phone: "123-456-7890"
  location: "New York, NY"
  linkedin: "https://linkedin.com/in/johndoe"
  github: "https://github.com/johndoe"
  website: "https://johndoe.dev"

job_preferences:
  target_roles: ["Software Engineer", "Backend Developer", "Python Developer"]
  locations: ["Remote", "New York, NY"]
  minimum_salary: 100000
  visa_sponsorship_required: false

master_resume:
  summary: "Experienced software engineer specializing in Python..."
  experience:
    - company: "Tech Corp"
      title: "Senior Developer"
      dates: "Jan 2020 - Present"
      bullets:
        - "Developed scalable microservices..."
        - "Optimized database queries..."
  education:
    - school: "University of Technology"
      degree: "B.S. Computer Science"
      grad_year: "2019"
  skills: ["Python", "JavaScript", "SQL", "Docker", "AWS"]

eeo_data:
  gender: "Male"
  race: "White"
  veteran: "No"
  disability: "No"
```

## Running the Applier

Once configured, you can execute the main script:

```bash
python src/main.py
```
