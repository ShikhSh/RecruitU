"""
Natural Language Query Parser with LLM Integration

This module provides functionality for parsing natural language queries
into structured search parameters using Large Language Models.
"""

from typing import Dict, Any
import os
from ..cache import query_parsing_cache
from ..models import NLSlots, normalize_slots
from .ollama_client import call_ollama_json
from ..utils import build_system_prompt, build_user_prompt


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
    provider = (os.getenv("LLM_PROVIDER", "ollama") or "none").lower()
    if provider == "ollama":
        result = _ollama_parse(query)
        # Cache the result for future requests
        query_parsing_cache.set(query, result)
        return result
    # Additional providers (OpenAI, etc.) can be added here
    raise RuntimeError(f"Unsupported LLM_PROVIDER={provider}")


def _ollama_parse(query: str) -> Dict[str, Any]:
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
        Dict[str, Any]: Validated and normalized query parameters
    """
    sys = build_system_prompt()
    user = build_user_prompt(query)
    obj = call_ollama_json(sys, user)
    obj = normalize_slots(obj)
    slots = NLSlots(**obj)
    return slots.dict(exclude_none=True)


# Export list for module imports
__all__ = ['generate_query_with_llm']
