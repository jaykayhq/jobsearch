import unittest
import os
import sys
from unittest.mock import patch, mock_open, MagicMock

# Mock third-party dependencies that might not be installed in the environment
sys.modules['yaml'] = MagicMock()
sys.modules['mistralai'] = MagicMock()
sys.modules['dotenv'] = MagicMock()

# Now we can safely import the class we want to test
from src.ai.mistral_client import AIClient

class TestAIClient(unittest.TestCase):

    @patch('src.ai.mistral_client.os.getenv')
    @patch('src.ai.mistral_client.load_dotenv')
    def test_init_missing_api_key(self, mock_load_dotenv, mock_getenv):
        """Test that AIClient raises a ValueError if MISTRAL_API_KEY is not set."""
        # Setup: Ensure os.getenv returns None when called for the API key
        mock_getenv.return_value = None

        # Execute & Verify
        with self.assertRaises(ValueError) as context:
            AIClient(profile_path="dummy_path.yaml")

        self.assertEqual(
            str(context.exception),
            "MISTRAL_API_KEY environment variable not found."
        )

    @patch('src.ai.mistral_client.os.getenv')
    @patch('src.ai.mistral_client.load_dotenv')
    @patch('builtins.open', new_callable=mock_open)
    @patch('src.ai.mistral_client.yaml.safe_load')
    @patch('src.ai.mistral_client.Mistral')
    def test_init_with_api_key(self, mock_mistral_class, mock_yaml_load, mock_file_open, mock_load_dotenv, mock_getenv):
        """Test happy path initialization when API key is present."""
        # Setup
        mock_getenv.return_value = "fake-api-key"
        mock_yaml_load.return_value = {"name": "Test User"}

        # Execute
        client = AIClient(profile_path="dummy_path.yaml")

        # Verify
        self.assertEqual(client.api_key, "fake-api-key")
        self.assertEqual(client.profile, {"name": "Test User"})
        mock_getenv.assert_called_with("MISTRAL_API_KEY")
        mock_mistral_class.assert_called_once_with(api_key="fake-api-key")

if __name__ == '__main__':
    unittest.main()
