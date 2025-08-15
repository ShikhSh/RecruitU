from fastapi import FastAPI, Depends, Query, Request, Body
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any
from backend_app.config import Settings, get_settings
from backend_app.clients import people_api
from backend_app.nl_parser_llm import generate_query_with_llm, call_llm_for_suggestions_async, query_parsing_cache
from backend_app.schemas import NLSearchRequest, SearchResponse, PeopleResponse
import os
import time
import hashlib

app = FastAPI(title="RecruitU LateralGPT")

app.mount("/static", StaticFiles(directory="backend_app/static"), name="static")
templates = Jinja2Templates(directory="backend_app/templates")

# Simple in-memory cache for conversation suggestions
class SuggestionsCache:
    def __init__(self, ttl_seconds: int = 3600):  # 1 hour TTL
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl_seconds
    
    def _generate_key(self, user_a: Dict, user_b: Dict) -> str:
        """Generate a cache key based on user IDs"""
        user_a_id = user_a.get('id', str(user_a))
        user_b_id = user_b.get('id', str(user_b))
        return f"{user_a_id}-{user_b_id}"
    
    def get(self, user_a: Dict, user_b: Dict) -> List[str] | None:
        """Get cached suggestions if they exist and haven't expired"""
        key = self._generate_key(user_a, user_b)
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.ttl:
                return entry['suggestions']
            else:
                # Remove expired entry
                del self.cache[key]
        return None
    
    def set(self, user_a: Dict, user_b: Dict, suggestions: List[str]) -> None:
        """Cache suggestions with timestamp"""
        key = self._generate_key(user_a, user_b)
        self.cache[key] = {
            'suggestions': suggestions,
            'timestamp': time.time()
        }
    
    def clear_expired(self) -> None:
        """Remove expired entries from cache"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time - entry['timestamp'] >= self.ttl
        ]
        for key in expired_keys:
            del self.cache[key]

# Initialize cache
suggestions_cache = SuggestionsCache(ttl_seconds=3600)  # 1 hour cache

@app.get("/health")
def health():
    # Clean up expired cache entries on health checks
    suggestions_cache.clear_expired()
    query_parsing_cache.clear_expired()
    return {"ok": True, "cache_size": len(suggestions_cache.cache)}

@app.post("/cache/clear")
def clear_caches(cache_type: str = Query(default="all", description="Type of cache to clear: 'suggestions', 'query_parsing', or 'all'")):
    """Clear caches and return statistics"""
    result = {"cleared": [], "stats": {}}
    
    if cache_type in ["suggestions", "all"]:
        suggestions_count = len(suggestions_cache.cache)
        suggestions_cache.cache.clear()
        result["cleared"].append("suggestions")
        result["stats"]["suggestions_cleared"] = suggestions_count
    
    if cache_type in ["query_parsing", "all"]:
        query_parsing_count = query_parsing_cache.clear()
        result["cleared"].append("query_parsing")
        result["stats"]["query_parsing_cleared"] = query_parsing_count
    
    return result

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/suggest_conversation")
async def suggest_conversation(payload: Dict[str, Any] = Body(...)):
    print(f"Received suggest_conversation request")
    
    userA = payload.get("currentUser", {})
    userB = payload.get("inquiredUser", {})

    # Check if we have valid user data
    if not userA or not userB:
        return {"suggestions": ["Unable to generate suggestions - missing user data."]}
    
    # Check cache first
    cached_suggestions = suggestions_cache.get(userA, userB)
    if cached_suggestions:
        print(f"Returning cached suggestions for users {userA.get('id', 'unknown')}-{userB.get('id', 'unknown')}")
        return {"suggestions": cached_suggestions}
    
    # Generate new suggestions if not cached
    try:
        # First try LLM if available
        suggestions = []
        try:
            prompt = (
                f"User A: {userA}\n"
                f"User B: {userB}\n"
                "Find common backgrounds and suggest 2-3 ways User A can start a conversation with User B."
            )
            suggestions = await call_llm_for_suggestions_async(prompt)
            suggestions_cache.set(userA, userB, suggestions)
            print(f"LLM generated suggestions: {suggestions}")
        except Exception as llm_error:
            print(f"LLM failed, using rule-based suggestions: {llm_error}")
            suggestions = []
        
        # If LLM fails or returns empty, use rule-based suggestions
        if not suggestions:
            suggestions = ["Consider reaching out to discuss shared professional interests."]
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
    use_llm = (os.getenv("LLM_PROVIDER") and os.getenv("LLM_PROVIDER").lower() != "none")
    parsed = {}
    if use_llm:
        try:
            parsed = generate_query_with_llm(req.query)
        except Exception as e:
            print(f"LLM parsing failed: {e}")

    # Defaults
    parsed.setdefault("page", 1)
    parsed.setdefault("count", 20)

    results = await people_api.search_with_formatted_results(parsed, settings=settings)
    return results

@app.get("/people", response_model=PeopleResponse)
async def proxy_people(
    ids: List[str] = Query(None, description="comma-separated ids"),
    settings: Settings = Depends(get_settings),
):
    if not ids or not ids[0]:
        return {"error": "User ID is required"}

    user_information = await people_api.get_user_information(ids[0], settings)
    if not user_information:
        return {"error": "User not found"}
    
    return user_information