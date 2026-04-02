# Auto Job Applier (AI-Powered)

An automated job search and application tool powered by Mistral AI. It discovers jobs on LinkedIn and direct company pages (Greenhouse, Lever), evaluates them against your profile, intelligently tailors your resume/cover letter, and applies autonomously using Playwright.

## Features

- **Automated Discovery:** Finds jobs matching your criteria on LinkedIn and direct company ATS pages.
- **AI-Powered Evaluation:** Mistral AI scores job descriptions against your profile to filter out low-match roles and save time.
- **Smart Tailoring:** AI customizes your resume points and generates targeted cover letters for every application.
- **Autonomous Application:** Playwright navigates complex forms (Greenhouse, Lever, LinkedIn Easy Apply), filling out details and answering screening questions using AI.
- **Application Tracking:** A built-in SQLite database tracks all applications, preventing duplicates and keeping a history of what was submitted.

## Getting Started

See `docs/SETUP.md` for instructions on how to install dependencies, configure your API keys, and set up your user profile.

See `docs/BRAINSTORM_STRATEGIES.md` for advanced tips on maximizing your application success rate using this tool.
