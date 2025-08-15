"""
Natural Language Processing with LLM Support and Caching

This module provides functionality for parsing natural language queries into structured
search parameters using Large Language Models (LLMs), primarily Ollama. It includes:

- Query parsing and normalization
- LLM integration for both query parsing and conversation suggestions
- Caching mechanisms for improved performance
- Support for async operations

Key Components:
- QueryParsingCache: TTL-based cache for query parsing results
- NLSlots: Pydantic model for structured query parameters
- LLM integration functions for Ollama API
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from pathlib import Path
import os, json, re, time, hashlib
from ollama import Client, AsyncClient

# Load prompt configuration from JSON file
PROMPT_FILE = Path(__file__).parent / "prompts" / "nl_parser.json"

with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    PROMPT_DATA = json.load(f)

# Allowed sector values for validation
ALLOWED_SECTOR = {"CONSULTING", "FINANCE"}

# Cache for query parsing results to improve performance
class QueryParsingCache:
    """
    In-memory cache for query parsing results with TTL (Time To Live) expiration.
    
    This cache stores LLM parsing results to avoid redundant API calls for identical
    queries. It includes automatic expiration and cleanup functionality.
    
    Attributes:
        cache (Dict): Internal storage for cached entries
        ttl (int): Time-to-live in seconds for cache entries
    """
    
    def __init__(self, ttl_seconds: int = 7200):  # 2 hours TTL
        """
        Initialize the cache with specified TTL.
        
        Args:
            ttl_seconds (int): Time-to-live for cache entries in seconds (default: 2 hours)
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl_seconds
    
    def _generate_key(self, query: str) -> str:
        """
        Generate a consistent cache key from the query string.
        
        The query is normalized (lowercased, whitespace trimmed) and hashed
        to create a consistent key for caching.
        
        Args:
            query (str): The original query string
            
        Returns:
            str: MD5 hash of the normalized query
        """
        # Normalize the query: lowercase, strip whitespace, remove extra spaces
        normalized_query = " ".join(query.lower().strip().split())
        # Create a hash for consistent key generation
        return hashlib.md5(normalized_query.encode()).hexdigest()
    
    def get(self, query: str) -> Dict[str, Any] | None:
        """
        Retrieve cached parsing result if it exists and hasn't expired.
        
        Args:
            query (str): The query to look up
            
        Returns:
            Dict[str, Any] | None: Cached result if found and valid, None otherwise
        """
        key = self._generate_key(query)
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.ttl:
                return entry['result']
            else:
                # Remove expired entry
                del self.cache[key]
        return None
    
    def set(self, query: str, result: Dict[str, Any]) -> None:
        """
        Store parsing result in cache with current timestamp.
        
        Args:
            query (str): The original query string
            result (Dict[str, Any]): The parsing result to cache
        """
        key = self._generate_key(query)
        self.cache[key] = {
            'result': result.copy(),  # Store a copy to avoid mutation
            'timestamp': time.time(),
            'original_query': query  # Store original for debugging
        }
    
    def clear(self) -> int:
        """
        Clear all cached entries.
        
        Returns:
            int: Number of entries that were cleared
        """
        count = len(self.cache)
        self.cache.clear()
        return count
    
    def clear_expired(self) -> int:
        """
        Remove expired entries from cache.
        
        Returns:
            int: Number of expired entries removed
        """
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time - entry['timestamp'] >= self.ttl
        ]
        for key in expired_keys:
            del self.cache[key]
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics.
        
        Returns:
            Dict[str, Any]: Statistics including total, expired, and active entries
        """
        current_time = time.time()
        total_entries = len(self.cache)
        expired_entries = sum(
            1 for entry in self.cache.values()
            if current_time - entry['timestamp'] >= self.ttl
        )
        return {
            'total_entries': total_entries,
            'expired_entries': expired_entries,
            'active_entries': total_entries - expired_entries,
            'ttl_seconds': self.ttl
        }

# Initialize the global cache instance
query_parsing_cache = QueryParsingCache(ttl_seconds=7200)  # 2 hour cache

class NLSlots(BaseModel):
    """
    Pydantic model for structured natural language query parameters.
    
    This model defines the schema for parsed query results, including
    validation rules and default values for search parameters.
    
    Attributes:
        name (Optional[str]): Person's name to search for
        current_company (Optional[str]): Current employer
        previous_company (Optional[str]): Previous employer
        sector (Optional[str]): Industry sector (CONSULTING or FINANCE)
        title (Optional[str]): Job title
        role (Optional[str]): Job role
        school (Optional[str]): Educational institution
        undergraduate_year (Optional[int]): Year of undergraduate graduation
        city (Optional[str]): Location/city
        page (int): Page number for pagination (default: 1)
        count (int): Number of results per page (default: 20)
    """
    
    name: Optional[str] = None
    current_company: Optional[str] = None
    previous_company: Optional[str] = None
    sector: Optional[str] = Field(default=None, description="CONSULTING or FINANCE")
    title: Optional[str] = None
    role: Optional[str] = None
    school: Optional[str] = None
    undergraduate_year: Optional[int] = None
    city: Optional[str] = None
    page: int = 1
    count: int = 20

    @validator("sector")
    def _sector_enum(cls, v):
        """
        Validate that sector is one of the allowed values.
        
        Args:
            v: The sector value to validate
            
        Returns:
            str: The validated and normalized sector value
            
        Raises:
            ValueError: If sector is not in ALLOWED_SECTOR
        """
        if v is None: 
            return v
        v2 = v.upper().strip()
        if v2 not in ALLOWED_SECTOR:
            raise ValueError("sector must be CONSULTING or FINANCE")
        return v2

def normalize_slots(d: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize and clean slot values from LLM parsing results.
    
    This function processes the raw dictionary from LLM parsing to:
    - Trim whitespace from string values
    - Remove empty or None values
    - Ensure valid page and count values with appropriate defaults and limits
    
    Args:
        d (Dict[str, Any]): Raw dictionary from LLM parsing
        
    Returns:
        Dict[str, Any]: Cleaned and normalized dictionary
    """
    # Trim strings, drop empties, clamp page/count
    cleaned: Dict[str, Any] = {}
    for k, v in d.items():
        if isinstance(v, str):
            v = v.strip()
        if v in ("", None):
            continue
        cleaned[k] = v
    
    # Ensure valid pagination parameters
    cleaned["page"] = int(cleaned.get("page", 1) or 1)
    cleaned["count"] = int(cleaned.get("count", 20) or 20)
    cleaned["count"] = max(1, min(cleaned["count"], 200))
    return cleaned

def build_system_prompt() -> str:
    """
    Build the system prompt for LLM query parsing.
    
    Uses the instructions from the prompt configuration file as the system message
    for consistent LLM behavior across parsing requests.
    
    Returns:
        str: System prompt text from configuration
    """
    return PROMPT_DATA["instructions"]

def build_user_prompt(query: str) -> str:
    """
    Build the user prompt for LLM query parsing.
    
    Formats the user query for submission to the LLM, following the
    expected input/output pattern.
    
    Args:
        query (str): The natural language query to parse
        
    Returns:
        str: Formatted user prompt
    """
    # Note: Examples are commented out but could be re-enabled for few-shot learning
    # examples_text = "\n".join(
    #     f"Input: {ex['input']}\nOutput: {ex['output']}"
    #     for ex in PROMPT_DATA.get("examples", [])
    # )
    # return f"{examples_text}\n\nInput: {query}\nOutput:"
    return f"\nInput: {query}\nOutput:"

def generate_query_with_llm(query: str) -> Dict[str, Any]:
    """
    Parse natural language query into structured parameters using LLM with caching.
    
    This is the main entry point for query parsing. It first checks the cache
    for existing results, and if not found, uses the configured LLM provider
    to parse the query and caches the result.
    
    Args:
        query (str): Natural language search query
        
    Returns:
        Dict[str, Any]: Structured query parameters
        
    Raises:
        RuntimeError: If LLM provider is unsupported or LLM call fails
    """
    # Check cache first for performance optimization
    cached_result = query_parsing_cache.get(query)
    if cached_result:
        print(f"Returning cached parsing result for query: {query[:50]}...")
        return cached_result
    
    # Generate new parsing result if not cached
    provider = (os.getenv("LLM_PROVIDER") or "none").lower()
    if provider == "ollama":
        result = _ollama_parse(query)
        # Cache the result for future requests
        query_parsing_cache.set(query, result)
        return result
    # Additional providers (OpenAI, etc.) can be added here
    raise RuntimeError(f"Unsupported LLM_PROVIDER={provider}")

async def call_ollama_json_async(system_prompt: str, user_prompt: str) -> dict:
    """
    Asynchronously call Ollama API to get JSON response.
    
    This function makes an async API call to Ollama with the provided prompts
    and returns the parsed JSON response. It includes error handling and
    JSON extraction from potentially malformed responses.
    
    Args:
        system_prompt (str): System message for the LLM
        user_prompt (str): User query/prompt
        
    Returns:
        dict: Parsed JSON response from Ollama
        
    Raises:
        RuntimeError: If Ollama API call fails or returns invalid JSON
    """
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    client = AsyncClient(host=host)
    
    try:
        resp = await client.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt}, 
                {"role": "user", "content": user_prompt}
            ],
            options={"temperature": 0},  # Deterministic output
            format="json",
        )
        raw = resp["message"]["content"]
        
        # Try to parse JSON directly
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            raise RuntimeError(f"Ollama did not return JSON: {raw[:200]}")
    except Exception as e:
        print(f"Error calling Ollama API: {e}")
        raise RuntimeError(f"Ollama API call failed: {e}")

def call_ollama_json(system_prompt: str, user_prompt: str) -> dict:
    """
    Synchronously call Ollama API to get JSON response.
    
    This is the synchronous version of call_ollama_json_async. It makes a
    blocking API call to Ollama and includes the same error handling.
    
    Args:
        system_prompt (str): System message for the LLM
        user_prompt (str): User query/prompt
        
    Returns:
        dict: Parsed JSON response from Ollama
        
    Raises:
        RuntimeError: If Ollama API call fails or returns invalid JSON
    """
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    client = Client(host=host)
    
    try:
        resp = client.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt}, 
                {"role": "user", "content": user_prompt}
            ],
            options={"temperature": 0},  # Deterministic output
            format="json",
        )
        raw = resp["message"]["content"]
        
        # Try to parse JSON directly
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # Fallback: extract JSON from potentially malformed response
            m = re.search(r"\{.*\}", raw, re.S)
            if not m:
                raise RuntimeError(f"Ollama did not return JSON: {raw[:200]}")
            return json.loads(m.group(0))
    except Exception as e:
        print(f"Error calling Ollama API: {e}")
        raise RuntimeError(f"Ollama API call failed: {e}")

def _ollama_parse(query: str) -> dict:
    """
    Internal function to parse query using Ollama API.
    
    This function orchestrates the complete parsing process:
    1. Build system and user prompts
    2. Call Ollama API
    3. Normalize the response
    4. Validate with NLSlots model
    
    Args:
        query (str): Natural language query to parse
        
    Returns:
        dict: Validated and normalized query parameters
    """
    sys = build_system_prompt()
    user = build_user_prompt(query)
    obj = call_ollama_json(sys, user)
    obj = normalize_slots(obj)
    slots = NLSlots(**obj)
    return slots.dict(exclude_none=True)

async def call_llm_for_suggestions_async(prompt: str):
    """
    Asynchronously generate conversation suggestions using LLM.
    
    This function takes user profile information and generates conversation
    starter suggestions based on commonalities between two users. It handles
    various response formats and provides fallback suggestions.
    
    Args:
        prompt (str): Formatted prompt containing user profile information
        
    Returns:
        List[str]: List of conversation suggestions, or fallback message if LLM fails
    """
    sys = ("You are an expert networking assistant. Given two user profiles and their "
           "backgrounds, suggest 2-3 ways they could start a conversation based on their "
           "commonalities. Respond with a JSON object with just Arrays of Strings and no "
           "additional information: {\"suggestions\": [ ... ]}")
    user = prompt
    
    try:
        response = await call_ollama_json_async(sys, user)
        if isinstance(response, dict) and "suggestions" in response:
            return response["suggestions"]
        elif isinstance(response, str):
            try:
                suggestions = json.loads(response)
                if isinstance(suggestions, list):
                    return suggestions
            except Exception:
                # Fallback: split by lines and filter non-empty
                return [line.strip() for line in response.split("\n") if line.strip()]
        else:
            return []
    except Exception as e:
        print(f"LLM suggestion error: {e}")
        return ["Sorry, could not generate suggestions at this time."]