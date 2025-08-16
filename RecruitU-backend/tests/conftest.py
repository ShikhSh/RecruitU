"""
Configuration for pytest testing

This file contains pytest configuration and test fixtures
for the RecruitU backend test suite.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the parent directory to Python path to allow imports
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from main import app
from src.config import Settings


@pytest.fixture
def client():
    """
    Create a test client for the FastAPI application.
    
    Returns:
        TestClient: FastAPI test client instance
    """
    return TestClient(app)


@pytest.fixture
def test_settings():
    """
    Create test settings with safe defaults.
    
    Returns:
        Settings: Test configuration settings
    """
    return Settings(
        LLM_PROVIDER="none",  # Disable LLM for tests
        PEOPLE_API_BASE="https://staging.recruitu.com/api/test",
        TIMEOUT_SECONDS=5
    )


@pytest.fixture
def sample_user_data():
    """
    Sample user data for testing.
    
    Returns:
        Dict: Sample user profile data
    """
    return {
        "id": "test_user_123",
        "full_name": "John Doe",
        "current_role": "Software Engineer",
        "current_company": "Tech Corp",
        "location": "San Francisco, CA",
        "skills": ["Python", "JavaScript", "React"],
        "experience_years": 5,
        "education": "BS Computer Science",
        "bio": "Passionate software engineer with 5 years of experience.",
        "email": "john.doe@example.com",  # This should be filtered out
        "phone": "+1234567890"  # This should be filtered out
    }


@pytest.fixture
def sample_search_user_data():
    """
    Sample search result user data for testing.
    
    Returns:
        Dict: Sample search result user data
    """
    return {
        "id": "search_user_456",
        "full_name": "Jane Smith",
        "current_role": "Product Manager",
        "current_company": "StartupCo",
        "location": "New York, NY",
        "skills": ["Product Management", "Analytics", "Strategy"],
        "experience_years": 3,
        "private_info": "sensitive data",  # Should be filtered out
        "internal_id": "internal_123"  # Should be filtered out
    }
