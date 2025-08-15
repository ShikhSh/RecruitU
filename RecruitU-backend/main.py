"""
RecruitU Backend - FastAPI Application

This module provides the main FastAPI application for RecruitU, a professional networking
platform with AI-powered features.

Environment Variables:
- LLM_PROVIDER: LLM provider type ('ollama' or 'none')
- OLLAMA_HOST: Ollama server URL (default: http://localhost:11434)
- OLLAMA_MODEL: Ollama model name (default: llama3.1:8b)
- PEOPLE_API_BASE: External people API endpoint

API Endpoints:
- GET /health: Health check with cache maintenance
- GET /cache/stats: Cache statistics and monitoring
- POST /cache/clear: Manual cache clearing
- POST /search_nl: Natural language search with LLM parsing
- POST /suggest_conversation: AI-powered conversation suggestions
- GET /people: User profile proxy endpoint
- GET /: Main application interface
"""

from fastapi import FastAPI, Depends, Query, Request, Body
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any
import os
import sys
from pathlib import Path

# Add the current directory to Python path to allow imports from src
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import from our refactored modules
from src import (
    generate_query_with_llm, 
    call_llm_for_suggestions_async, 
    query_parsing_cache, 
    suggestions_cache,
    people_api,
    NLSearchRequest,
    PeopleResponse,
    filter_search_user_data_for_suggestions,
    filter_user_profile_for_suggestions
)
from src.config import Settings, get_settings

# Initialize FastAPI application
app = FastAPI(
    title="RecruitU Backend",
    description="AI-powered professional networking platform with modular architecture",
    version="3.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="/home/ubuntu/RecruitU/RecruitU-backend/static"), name="static")
templates = Jinja2Templates(directory="/home/ubuntu/RecruitU/RecruitU-backend/templates")


@app.get("/health")
def health():
    """
    Health check endpoint with cache maintenance.
    
    This endpoint provides basic health status and performs maintenance
    tasks like cleaning up expired cache entries.
    
    Returns:
        Dict: Health status and current cache statistics
    """
    # Clean up expired cache entries on health checks
    suggestions_expired = suggestions_cache.clear_expired()
    query_parsing_expired = query_parsing_cache.clear_expired()
    
    # Get cache statistics
    suggestions_stats = suggestions_cache.get_stats()
    query_parsing_stats = query_parsing_cache.get_stats()
    
    return {
        "status": "healthy",
        "cache_maintenance": {
            "suggestions_expired_cleared": suggestions_expired,
            "query_parsing_expired_cleared": query_parsing_expired
        },
        "cache_stats": {
            "suggestions": suggestions_stats,
            "query_parsing": query_parsing_stats
        }
    }

@app.post("/cache/clear")
def clear_caches(
    cache_type: str = Query(
        default="all", 
        description="Type of cache to clear: 'suggestions', 'query_parsing', or 'all'"
    )
):
    """
    Clear specified caches and return statistics.
    
    This endpoint allows manual cache clearing for maintenance or testing purposes.
    It can clear specific cache types or all caches at once.
    
    Args:
        cache_type (str): Type of cache to clear ('suggestions', 'query_parsing', or 'all')
        
    Returns:
        Dict: Information about cleared caches and statistics
    """
    result = {"cleared": [], "stats": {}}
    
    if cache_type in ["suggestions", "all"]:
        suggestions_count = suggestions_cache.clear()
        result["cleared"].append("suggestions")
        result["stats"]["suggestions_cleared"] = suggestions_count
    
    if cache_type in ["query_parsing", "all"]:
        query_parsing_count = query_parsing_cache.clear()
        result["cleared"].append("query_parsing")
        result["stats"]["query_parsing_cleared"] = query_parsing_count
    
    return result


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Serve the main application homepage.
    
    Returns the main HTML template for the application interface.
    
    Args:
        request (Request): FastAPI request object
        
    Returns:
        HTMLResponse: Rendered HTML template
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/suggest_conversation")
async def suggest_conversation(payload: Dict[str, Any] = Body(...)):
    """
    Generate conversation suggestions between two users.
    
    This endpoint analyzes two user profiles and generates AI-powered
    conversation suggestions based on their commonalities. It uses caching
    to improve performance for repeated requests.
    
    Args:
        payload (Dict): Request body containing 'currentUser' and 'inquiredUser'
        
    Returns:
        Dict: JSON response with 'suggestions' array
    """
    print(f"Received suggest_conversation request")
    
    userA = payload.get("currentUser", {})
    userB = payload.get("inquiredUser", {})

    # Validate that we have valid user data
    if not userA or not userB:
        return {"suggestions": ["Unable to generate suggestions - missing user data."]}
    
    # Filter user data for consistency in caching and LLM prompts
    filtered_userA = filter_user_profile_for_suggestions(userA)
    filtered_userB = filter_search_user_data_for_suggestions(userB)
    
    # Check cache first for performance optimization (using filtered data for cache key)
    cached_suggestions = suggestions_cache.get(filtered_userA, filtered_userB)
    if cached_suggestions:
        print(f"Returning cached suggestions for users {filtered_userA.get('full_name', 'unknown')}-{filtered_userB.get('full_name', 'unknown')}")
        return {"suggestions": cached_suggestions}
    
    # Generate new suggestions if not cached
    try:
        # Attempt LLM-powered suggestion generation
        suggestions = []
        try:
            prompt = (
                f"User A: {filtered_userA}\n"
                f"User B: {filtered_userB}\n"
                "Find common backgrounds and suggest 2-3 ways User A can start a conversation with User B."
            )
            
            suggestions = await call_llm_for_suggestions_async(prompt)
            if suggestions:
                # Cache using filtered data for consistency
                suggestions_cache.set(filtered_userA, filtered_userB, suggestions)
                print(f"LLM generated suggestions: {suggestions}")
        except Exception as llm_error:
            print(f"LLM failed, using rule-based suggestions: {llm_error}")
            suggestions = []
        
        # Fallback to default suggestions if LLM fails
        if not suggestions:
            suggestions = [
                "Consider reaching out to discuss shared professional interests.",
                "You might connect over industry trends and insights.",
                "Consider starting with a comment about their recent career achievements."
            ]
            
        return {"suggestions": suggestions}
        
    except Exception as e:
        print(f"Error in suggest_conversation: {e}")
        fallback_suggestions = [
            "You could reach out to discuss shared professional interests.",
            "Consider connecting over industry trends and insights.",
            "You might start with a comment about their recent career achievements."
        ]
        return {"suggestions": fallback_suggestions}


@app.post("/search_nl")
async def search_nl(req: NLSearchRequest, settings: Settings = Depends(get_settings)):
    """
    Perform natural language search with LLM parsing.
    
    This endpoint accepts natural language queries and uses LLM to parse them
    into structured search parameters. The parsed parameters are then used
    to search the people database.
    
    Args:
        req (NLSearchRequest): Request containing the natural language query
        settings (Settings): Application settings and configuration
        
    Returns:
        SearchResponse: Formatted search results
    """
    print(f"Received natural language search query: '{req.query}'")
    
    # Check if LLM is available and configured
    use_llm = (os.getenv("LLM_PROVIDER") and os.getenv("LLM_PROVIDER").lower() != "none")
    parsed = {}
    
    if use_llm:
        try:
            # Use LLM to parse the natural language query
            parsed = generate_query_with_llm(req.query)
            print(f"LLM parsed query into: {parsed}")
        except Exception as e:
            print(f"LLM parsing failed: {e}")
            # Continue with empty parsed dict - will use defaults

    # Set default pagination parameters
    parsed.setdefault("page", 1)
    parsed.setdefault("count", 20)

    # Execute search with parsed parameters
    results = await people_api.search_with_formatted_results(parsed, settings=settings)
    print(f"Search returned {len(results.get('results', []))} results")
    
    return results


@app.get("/people", response_model=PeopleResponse)
async def proxy_people(
    ids: List[str] = Query(None, description="comma-separated ids"),
    settings: Settings = Depends(get_settings),
):
    """
    Retrieve detailed information for specific users.
    
    This endpoint serves as a proxy to the people API, allowing the frontend
    to retrieve detailed user information by ID.
    
    Args:
        ids (List[str]): List of user IDs to retrieve
        settings (Settings): Application settings and configuration
        
    Returns:
        PeopleResponse: User information or error message
    """
    # Validate that user ID is provided
    if not ids or not ids[0]:
        return {"error": "User ID is required"}

    print(f"Fetching user information for ID: {ids[0]}")
    
    # Retrieve user information from the people API
    user_information = await people_api.get_user_information(ids[0], settings)
    if not user_information:
        return {"error": "User not found"}
    
    return user_information

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
