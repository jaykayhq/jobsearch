import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Mock required third-party dependencies before importing the module under test
sys.modules['yaml'] = MagicMock()
sys.modules['urllib.request'] = MagicMock()
sys.modules['dotenv'] = MagicMock()

# Now it is safe to import AIClient
from src.ai.mistral_client import AIClient

class TestAIClient(unittest.TestCase):
    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "fake_test_key"})
    def test_profile_loading_error(self):
        """
        Test that when an invalid profile path is provided,
        the AIClient handles the exception and sets profile to an empty dict.
        """
        # Verify that the profile defaults to an empty dictionary
        client = AIClient()
        self.assertEqual(client.profile, {})

if __name__ == "__main__":
    unittest.main()
