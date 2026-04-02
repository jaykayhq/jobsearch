from playwright.sync_api import sync_playwright, Page, Browser
import time
import random

class BrowserManager:
    def __init__(self, headless=False):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def start(self):
        self.playwright = sync_playwright().start()
        # Launch Chromium with basic stealth arguments
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-infobars',
                '--window-size=1920,1080',
            ]
        )
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        self.page = self.context.new_page()

        # Override webdriver property to avoid detection
        self.page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def stop(self):
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def human_typing(self, selector: str, text: str):
        """Simulate human typing to avoid basic bot detection."""
        self.page.focus(selector)
        self.page.fill(selector, "") # Clear first
        for char in text:
            self.page.type(selector, char, delay=random.randint(30, 100))
        time.sleep(random.uniform(0.5, 1.5))

    def human_click(self, selector: str):
        """Simulate a human click with slight delay."""
        self.page.hover(selector)
        time.sleep(random.uniform(0.1, 0.5))
        self.page.click(selector, delay=random.randint(50, 150))
        time.sleep(random.uniform(0.5, 1.5))
