from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from pathlib import Path
import os, json, re, time, hashlib
from ollama import Client, AsyncClient

# from .nl_parser_llm import NLSlots, normalize_slots

PROMPT_FILE = Path(__file__).parent / "prompts" / "nl_parser.json"

with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    PROMPT_DATA = json.load(f)

ALLOWED_SECTOR = {"CONSULTING", "FINANCE"}

# Cache for query parsing results
class QueryParsingCache:
    def __init__(self, ttl_seconds: int = 7200):  # 2 hours TTL
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl_seconds
    
    def _generate_key(self, query: str) -> str:
        """Generate a cache key from the query string"""
        # Normalize the query: lowercase, strip whitespace, remove extra spaces
        normalized_query = " ".join(query.lower().strip().split())
        # Create a hash for consistent key generation
        return hashlib.md5(normalized_query.encode()).hexdigest()
    
    def get(self, query: str) -> Dict[str, Any] | None:
        """Get cached parsing result if it exists and hasn't expired"""
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
        """Cache parsing result with timestamp"""
        key = self._generate_key(query)
        self.cache[key] = {
            'result': result.copy(),  # Store a copy to avoid mutation
            'timestamp': time.time(),
            'original_query': query  # Store original for debugging
        }
    
    def clear(self) -> int:
        """Clear all cached entries and return the number cleared"""
        count = len(self.cache)
        self.cache.clear()
        return count
    
    def clear_expired(self) -> int:
        """Remove expired entries from cache and return count of removed entries"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time - entry['timestamp'] >= self.ttl
        ]
        for key in expired_keys:
            del self.cache[key]
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
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

# Initialize the cache
query_parsing_cache = QueryParsingCache(ttl_seconds=7200)  # 2 hour cache

class NLSlots(BaseModel):
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
        if v is None: 
            return v
        v2 = v.upper().strip()
        if v2 not in ALLOWED_SECTOR:
            raise ValueError("sector must be CONSULTING or FINANCE")
        return v2

def normalize_slots(d: Dict[str, Any]) -> Dict[str, Any]:
    # Trim strings, drop empties, clamp page/count
    cleaned: Dict[str, Any] = {}
    for k, v in d.items():
        if isinstance(v, str):
            v = v.strip()
        if v in ("", None):
            continue
        cleaned[k] = v
    cleaned["page"] = int(cleaned.get("page", 1) or 1)
    cleaned["count"] = int(cleaned.get("count", 20) or 20)
    cleaned["count"] = max(1, min(cleaned["count"], 200))
    return cleaned

def build_system_prompt() -> str:
    """
    Use the instructions from the prompt file directly as the system message.
    """
    return PROMPT_DATA["instructions"]

def build_user_prompt(query: str) -> str:
    """
    Add the examples and the current query to the user message.
    """
    # examples_text = "\n".join(
    #     f"Input: {ex['input']}\nOutput: {ex['output']}"
    #     for ex in PROMPT_DATA.get("examples", [])
    # )
    # return f"{examples_text}\n\nInput: {query}\nOutput:"
    return f"\nInput: {query}\nOutput:"

def generate_query_with_llm(query: str) -> Dict[str, Any]:
    # Check cache first
    cached_result = query_parsing_cache.get(query)
    if cached_result:
        print(f"Returning cached parsing result for query: {query[:50]}...")
        return cached_result
    
    # Generate new parsing result if not cached
    provider = (os.getenv("LLM_PROVIDER") or "none").lower()
    if provider == "ollama":
        result = _ollama_parse(query)
        # Cache the result
        query_parsing_cache.set(query, result)
        return result
    # keep other branches if you want (openai, etc.)
    raise RuntimeError(f"Unsupported LLM_PROVIDER={provider}")

async def call_ollama_json_async(system_prompt: str, user_prompt: str) -> dict:
    """Async version of call_ollama_json"""
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    client = AsyncClient(host=host)
    try:
        resp = await client.chat(
            model=model,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            options={"temperature": 0},
            format="json",
        )
        raw = resp["message"]["content"]
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            m = re.search(r"\{.*\}", raw, re.S)
            if not m:
                raise RuntimeError(f"Ollama did not return JSON: {raw[:200]}")
            return json.loads(m.group(0))
    except Exception as e:
        print(f"Error calling Ollama API: {e}")
        raise RuntimeError(f"Ollama API call failed: {e}")

def call_ollama_json(system_prompt: str, user_prompt: str) -> dict:
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    client = Client(host=host)
    try:
        resp = client.chat(
            model=model,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            options={"temperature": 0},
            format="json",
        )
        raw = resp["message"]["content"]
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            m = re.search(r"\{.*\}", raw, re.S)
            if not m:
                raise RuntimeError(f"Ollama did not return JSON: {raw[:200]}")
            return json.loads(m.group(0))
    except Exception as e:
        print(f"Error calling Ollama API: {e}")
        raise RuntimeError(f"Ollama API call failed: {e}")

def _ollama_parse(query: str) -> dict:
    sys = build_system_prompt()
    user = build_user_prompt(query)
    obj = call_ollama_json(sys, user)
    obj = normalize_slots(obj)
    slots = NLSlots(**obj)
    return slots.dict(exclude_none=True)

async def call_llm_for_suggestions_async(prompt: str):
    """
    Async version: Calls the LLM with the given prompt and returns a list of suggestions.
    """
    sys = "You are an expert networking assistant. Given two user profiles and their backgrounds, suggest 2-3 ways they could start a conversation based on their commonalities. Respond with a JSON object with just Arrays of Strings and no additional information: {\"suggestions\": [ ... ]}"
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
                return [line.strip() for line in response.split("\n") if line.strip()]
        else:
            return []
    except Exception as e:
        print(f"LLM suggestion error: {e}")
        return ["Sorry, could not generate suggestions at this time."]