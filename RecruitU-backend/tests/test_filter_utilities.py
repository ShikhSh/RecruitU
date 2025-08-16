"""
Tests for user data filtering utilities

This module tests the filtering functions that prepare user data
for LLM prompts by removing sensitive information.
"""

import sys
from pathlib import Path

# Add the parent directory to Python path to allow imports
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from src.utils.filter_user_details_for_prompts import (
    filter_search_user_data_for_suggestions,
    filter_user_profile_for_suggestions
)


def test_filter_search_user_data_basic(sample_search_user_data):
    """
    Test basic filtering of search user data.
    
    This test verifies that:
    - Essential fields are preserved
    - Sensitive fields are removed
    - Function handles missing fields gracefully
    """
    filtered = filter_search_user_data_for_suggestions(sample_search_user_data)
    
    # Check that essential fields are preserved
    assert filtered["full_name"] == "Jane Smith"
    
    # Check that sensitive fields are removed
    assert "private_info" not in filtered
    assert "internal_id" not in filtered


def test_filter_user_profile_basic(sample_user_data):
    """
    Test basic filtering of user profile data.
    
    This test verifies that:
    - Essential fields are preserved
    - Sensitive fields like email and phone are removed
    - Function handles the data correctly
    """
    filtered = filter_user_profile_for_suggestions(sample_user_data)
    
    # Check that essential fields are preserved
    assert filtered["full_name"] == "John Doe"
    
    # Check that sensitive fields are removed
    assert "email" not in filtered
    assert "phone" not in filtered


def test_filter_search_user_data_empty():
    """
    Test filtering with empty or None data.
    
    This test verifies that:
    - Function handles empty dictionaries
    - Function handles None input
    - No errors are raised
    """
    # Test empty dictionary
    filtered = filter_search_user_data_for_suggestions({})
    assert isinstance(filtered, dict)
    assert len(filtered) == 0
    
    # Test None input
    filtered = filter_search_user_data_for_suggestions(None)
    assert filtered == {}


def test_filter_user_profile_empty():
    """
    Test filtering with empty or None data.
    
    This test verifies that:
    - Function handles empty dictionaries
    - Function handles None input
    - No errors are raised
    """
    # Test empty dictionary
    filtered = filter_user_profile_for_suggestions({})
    assert isinstance(filtered, dict)
    assert len(filtered) == 0
    
    # Test None input
    filtered = filter_user_profile_for_suggestions(None)
    assert filtered == {}


def test_filter_search_user_data_partial():
    """
    Test filtering with partial data.
    
    This test verifies that:
    - Function works with missing optional fields
    - Only available fields are included
    """
    partial_data = {
        "id": "partial_user",
        "full_name": "Partial User",
        "current_role": "Developer"
        # Missing other fields
    }
    
    filtered = filter_search_user_data_for_suggestions(partial_data)
    
    assert filtered["full_name"] == "Partial User"
    assert "current_company" not in filtered  # Not provided
    assert "skills" not in filtered  # Not provided


def test_filter_user_profile_partial():
    """
    Test filtering with partial user profile data.
    
    This test verifies that:
    - Function works with missing optional fields
    - Only available fields are included
    """
    partial_data = {
        "id": "partial_profile",
        "full_name": "Partial Profile"
    }
    
    filtered = filter_user_profile_for_suggestions(partial_data)
    
    assert filtered["full_name"] == "Partial Profile"
    assert "email" not in filtered  # Should be removed
    assert "current_company" not in filtered  # Not provided
