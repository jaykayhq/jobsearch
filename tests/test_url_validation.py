import sys
import pytest
from unittest.mock import MagicMock, patch

# Mock dependencies
sys.modules['src.applier.browser'] = MagicMock()
sys.modules['src.ai.mistral_client'] = MagicMock()
sys.modules['yaml'] = MagicMock()

from src.applier.greenhouse import GreenhouseApplier
from src.applier.lever import LeverApplier
from src.applier.linkedin_easy_apply import LinkedInEasyApply

@patch('builtins.open')
def test_greenhouse_url_validation(mock_open, capsys):
    applier = GreenhouseApplier(MagicMock(), MagicMock(), "dummy")

    # Valid URLs
    applier.apply("http://example.com")
    assert "Invalid URL scheme" not in capsys.readouterr().out

    # Invalid URLs
    assert applier.apply("file:///etc/passwd") == False
    assert "Invalid URL scheme 'file'" in capsys.readouterr().out
    assert applier.apply("javascript:alert(1)") == False
    assert "Invalid URL scheme 'javascript'" in capsys.readouterr().out

@patch('builtins.open')
def test_lever_url_validation(mock_open, capsys):
    applier = LeverApplier(MagicMock(), MagicMock(), "dummy")

    # Invalid URLs
    assert applier.apply("file:///etc/passwd") == False
    assert "Invalid URL scheme 'file'" in capsys.readouterr().out

@patch('builtins.open')
def test_linkedin_url_validation(mock_open, capsys):
    applier = LinkedInEasyApply(MagicMock(), MagicMock(), "dummy")

    # Invalid URLs
    assert applier.apply("file:///etc/passwd") == False
    assert "Invalid URL scheme 'file'" in capsys.readouterr().out
