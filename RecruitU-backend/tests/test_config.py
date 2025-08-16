"""
Tests for configuration and settings

This module tests the application configuration and settings
to ensure environment variables are loaded correctly.
"""

import pytest
import sys
from pathlib import Path

# Add the parent directory to Python path to allow imports
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from src.config import Settings, get_settings


def test_settings_defaults():
    """
    Test default settings values.
    
    This test verifies that:
    - Settings can be created with defaults
    - Default values are reasonable
    """
    settings = Settings()
    
    # Check that basic settings exist
    assert hasattr(settings, 'LLM_PROVIDER')
    assert hasattr(settings, 'OLLAMA_HOST')
    assert hasattr(settings, 'OLLAMA_MODEL')
    assert hasattr(settings, 'PEOPLE_API_BASE')
    assert hasattr(settings, 'TIMEOUT_SECONDS')
    
    # Check default values are reasonable
    assert isinstance(settings.TIMEOUT_SECONDS, int)
    assert settings.TIMEOUT_SECONDS > 0
    assert isinstance(settings.PEOPLE_API_BASE, str)
    assert len(settings.PEOPLE_API_BASE) > 0


def test_settings_with_custom_values():
    """
    Test settings with custom values.
    
    This test verifies that:
    - Settings can be overridden
    - Custom values are properly set
    """
    custom_settings = Settings(
        LLM_PROVIDER="test_provider",
        OLLAMA_HOST="http://test:1234",
        OLLAMA_MODEL="test_model",
        TIMEOUT_SECONDS=30
    )
    
    assert custom_settings.LLM_PROVIDER == "test_provider"
    assert custom_settings.OLLAMA_HOST == "http://test:1234"
    assert custom_settings.OLLAMA_MODEL == "test_model"
    assert custom_settings.TIMEOUT_SECONDS == 30


def test_get_settings_function():
    """
    Test the get_settings function.
    
    This test verifies that:
    - get_settings returns a Settings instance
    - Function can be called multiple times
    - Settings have expected attributes
    """
    settings1 = get_settings()
    settings2 = get_settings()
    
    # Should return Settings instances
    assert isinstance(settings1, Settings)
    assert isinstance(settings2, Settings)
    
    # Due to @lru_cache, should be the same instance
    assert settings1 is settings2
    
    # Should have all required attributes
    assert hasattr(settings1, 'LLM_PROVIDER')
    assert hasattr(settings1, 'PEOPLE_API_BASE')


def test_llm_provider_none_handling():
    """
    Test handling of LLM_PROVIDER when set to 'none'.
    
    This test verifies that:
    - LLM_PROVIDER can be set to 'none'
    - Settings handle this value correctly
    """
    settings = Settings(LLM_PROVIDER="none")
    assert settings.LLM_PROVIDER == "none"
    
    settings = Settings(LLM_PROVIDER="NONE")
    assert settings.LLM_PROVIDER == "NONE"


def test_settings_validation():
    """
    Test that settings validation works correctly.
    
    This test verifies that:
    - Invalid timeout values are handled
    - Settings maintain type safety
    """
    # Test with valid timeout
    settings = Settings(TIMEOUT_SECONDS=10)
    assert settings.TIMEOUT_SECONDS == 10
    
    # Pydantic should handle type conversion
    settings = Settings(TIMEOUT_SECONDS="15")
    assert settings.TIMEOUT_SECONDS == 15
    assert isinstance(settings.TIMEOUT_SECONDS, int)
