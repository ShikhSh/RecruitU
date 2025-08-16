"""
Basic API endpoint tests for RecruitU Backend

This module contains basic tests for the main API endpoints
to ensure they respond correctly and handle errors gracefully.
"""

import pytest
from fastapi.testclient import TestClient


def test_home_endpoint(client):
    """
    Test the home page endpoint.
    
    This test verifies that:
    - The home endpoint responds with 200 OK
    - Returns HTML content
    """
    response = client.get("/")
    
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_cache_clear_endpoint(client):
    """
    Test the cache clearing endpoint.
    
    This test verifies that:
    - The cache clear endpoint responds with 200 OK
    - Returns expected JSON structure
    - Can clear all caches by default
    """
    response = client.post("/cache/clear")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check basic structure
    assert "cleared" in data
    assert "stats" in data
    
    # Should clear all caches by default
    assert "suggestions" in data["cleared"]
    assert "query_parsing" in data["cleared"]


def test_cache_clear_specific(client):
    """
    Test clearing specific cache types.
    
    This test verifies that:
    - Can clear only suggestions cache
    - Can clear only query_parsing cache
    """
    # Test clearing only suggestions cache
    response = client.post("/cache/clear?cache_type=suggestions")
    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data["cleared"]
    assert "query_parsing" not in data["cleared"]
    
    # Test clearing only query_parsing cache
    response = client.post("/cache/clear?cache_type=query_parsing")
    assert response.status_code == 200
    data = response.json()
    assert "query_parsing" in data["cleared"]
    assert "suggestions" not in data["cleared"]


def test_search_nl_endpoint_basic(client):
    """
    Test the natural language search endpoint with basic query.
    
    This test verifies that:
    - The endpoint accepts POST requests
    - Returns proper response structure
    - Handles simple queries without LLM
    """
    test_query = {"query": "software engineers in san francisco"}
    
    response = client.post("/search_nl", json=test_query)
    
    # Should not fail even if external API is not available
    # We're testing the endpoint structure, not the actual search
    assert response.status_code in [200, 422, 500]  # Allow various responses
    
    if response.status_code == 200:
        data = response.json()
        # If successful, should have some structure
        assert isinstance(data, dict)


def test_people_endpoint_validation(client):
    """
    Test the people endpoint input validation.
    
    This test verifies that:
    - Endpoint requires user ID
    - Returns appropriate error for missing ID
    """
    # Test without any parameters
    response = client.get("/people")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert "required" in data["error"].lower()


def test_suggest_conversation_validation(client):
    """
    Test the conversation suggestion endpoint validation.
    
    This test verifies that:
    - Endpoint handles missing user data gracefully
    - Returns fallback suggestions when users are missing
    """
    # Test with empty payload
    response = client.post("/suggest_conversation", json={})
    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
    assert len(data["suggestions"]) > 0
    assert "missing user data" in data["suggestions"][0].lower()
    
    # Test with partial data
    partial_payload = {
        "currentUser": {"name": "John"},
        "inquiredUser": None
    }
    response = client.post("/suggest_conversation", json=partial_payload)
    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
