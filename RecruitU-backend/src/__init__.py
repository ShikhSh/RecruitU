"""
RecruitU Backend - Natural Language Processing Module

This package provides functionality for parsing natural language queries
into structured search parameters using Large Language Models.

Main Components:
- Cache: TTL-based caching for query parsing results and suggestions
- Models: Pydantic models for data validation
- LLM: Large Language Model integration (Ollama)
- Clients: HTTP clients for external API integration
- Schemas: Pydantic schemas for request/response validation
- Utils: Utility functions and prompt building
"""

# Main API exports
from .llm import generate_query_with_llm, call_llm_for_suggestions_async
from .models import NLSlots, normalize_slots
from .cache import QueryParsingCache, query_parsing_cache, SuggestionsCache, suggestions_cache
from .clients import PeopleAPI, people_api
from .schemas import NLSearchRequest, SearchResponse, PeopleResponse
from .utils import filter_search_user_data_for_suggestions, filter_user_profile_for_suggestions

__all__ = [
    'generate_query_with_llm',
    'call_llm_for_suggestions_async', 
    'NLSlots',
    'normalize_slots',
    'QueryParsingCache',
    'query_parsing_cache',
    'SuggestionsCache',
    'suggestions_cache',
    'PeopleAPI',
    'people_api',
    'NLSearchRequest',
    'SearchResponse', 
    'PeopleResponse',
    'filter_search_user_data_for_suggestions',
    'filter_user_profile_for_suggestions'
]