import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Mock required third-party dependencies before importing the module under test
sys.modules['yaml'] = MagicMock()
sys.modules['mistralai'] = MagicMock()
sys.modules['dotenv'] = MagicMock()

# Now it is safe to import AIClient
from src.ai.mistral_client import AIClient

class TestAIClient(unittest.TestCase):
    @patch.dict(os.environ, {"MISTRAL_API_KEY": "fake_test_key"})
    def test_profile_loading_error(self):
        """
        Test that when an invalid profile path is provided,
        the AIClient handles the exception and sets profile to an empty dict.
        """
        # Provide a non-existent file path to trigger the Exception
        client = AIClient(profile_path="non_existent_file.yaml")

        # Verify that the profile defaults to an empty dictionary on failure
        self.assertEqual(client.profile, {})

if __name__ == "__main__":
    unittest.main()
