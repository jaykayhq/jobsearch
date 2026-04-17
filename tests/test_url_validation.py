import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock dependencies to bypass actual loading/parsing requirements for simple tests
sys.modules['yaml'] = MagicMock()
sys.modules['src.applier.browser'] = MagicMock()
sys.modules['src.ai.mistral_client'] = MagicMock()

from src.applier.greenhouse import GreenhouseApplier
from src.applier.lever import LeverApplier
from src.applier.linkedin_easy_apply import LinkedInEasyApply


class TestURLValidation(unittest.TestCase):
    @patch('builtins.open', new_callable=MagicMock)
    def setUp(self, mock_open):
        self.mock_browser = MagicMock()
        self.mock_ai = MagicMock()

        self.greenhouse = GreenhouseApplier(self.mock_browser, self.mock_ai, profile_path="dummy.yaml")
        self.lever = LeverApplier(self.mock_browser, self.mock_ai, profile_path="dummy.yaml")
        self.linkedin = LinkedInEasyApply(self.mock_browser, self.mock_ai, profile_path="dummy.yaml")

    def test_valid_urls(self):
        valid_urls = [
            "https://boards.greenhouse.io/example/jobs/123",
            "http://example.com/apply"
        ]

        # We expect goto to be called if the URL is valid
        # We need to ensure we don't proceed with full apply logic for test simplicity
        for url in valid_urls:
            # Re-initialize mocks
            self.mock_browser.page.goto = MagicMock()
            self.mock_browser.page.is_visible = MagicMock(return_value=False)

            # Should return False because we mocked is_visible to False (form not found)
            # but it should have called goto.
            self.assertFalse(self.greenhouse.apply(url))
            self.mock_browser.page.goto.assert_called()

            # Same for lever
            self.mock_browser.page.goto = MagicMock()
            self.mock_browser.page.is_visible = MagicMock(return_value=False)
            self.assertFalse(self.lever.apply(url))
            self.mock_browser.page.goto.assert_called()

            # Same for linkedin
            self.mock_browser.page.goto = MagicMock()
            self.mock_browser.page.is_visible = MagicMock(return_value=False)
            self.assertFalse(self.linkedin.apply(url))
            self.mock_browser.page.goto.assert_called()

    def test_invalid_urls(self):
        invalid_urls = [
            "file:///etc/passwd",
            "javascript:alert(1)",
            "ftp://example.com/file",
            "data:text/html,<html>",
            "ws://localhost:9222"
        ]

        for url in invalid_urls:
            self.mock_browser.page.goto = MagicMock()

            self.assertFalse(self.greenhouse.apply(url))
            self.mock_browser.page.goto.assert_not_called()

            self.assertFalse(self.lever.apply(url))
            self.mock_browser.page.goto.assert_not_called()

            self.assertFalse(self.linkedin.apply(url))
            self.mock_browser.page.goto.assert_not_called()


if __name__ == '__main__':
    unittest.main()
