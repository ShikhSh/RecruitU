# RecruitU Backend - Natural Language Processing Module

A modular Python package for parsing natural language queries into structured search parameters using Large Language Models (LLMs), primarily Ollama.

## Features

- **Natural Language Query Parsing**: Convert unstructured text queries into structured search parameters
- **LLM Integration**: Support for Ollama API with async/sync operations
- **Intelligent Caching**: TTL-based cache system to reduce redundant API calls
- **Conversation Suggestions**: Generate networking conversation starters based on user profiles
- **Data Validation**: Pydantic models for robust data validation and type safety
- **Modular Architecture**: Clean separation of concerns across multiple modules

## Architecture

```
src/
├── __init__.py           # Main package exports
├── cache/                # Caching functionality
│   ├── __init__.py
│   ├── query_cache.py    # TTL-based query result cache
│   └── suggestions_cache.py # TTL-based conversation suggestions cache
├── models/               # Data models and validation
│   ├── __init__.py
│   └── nl_slots.py       # Pydantic models for query parameters
├── llm/                  # LLM integration
│   ├── __init__.py
│   ├── ollama_client.py  # Ollama API client (sync/async)
│   ├── suggestions.py    # Conversation suggestion generation
│   └── nl_parser.py      # Natural language query parsing
├── clients/              # External API clients
│   ├── __init__.py
│   └── people_api.py     # People API HTTP client
├── schemas/              # Request/response schemas
│   ├── __init__.py
│   └── api_models.py     # Pydantic models for API validation
└── utils/                # Utility functions
    ├── __init__.py
    └── prompt_builder.py  # LLM prompt construction
```

## Installation

```bash
pip install -r requirements.txt
```

## Environment Variables

- `OLLAMA_HOST`: Ollama server URL (default: `http://localhost:11434`)
- `OLLAMA_MODEL`: Model to use (default: `llama3.1:8b`)
- `LLM_PROVIDER`: LLM provider to use (default: `ollama`)

## Usage

### Basic Query Parsing

```python
from src import generate_query_with_llm

# Parse a natural language query
result = generate_query_with_llm("Find consultants in finance from Harvard")
print(result)
# Output: {'sector': 'FINANCE', 'school': 'Harvard', 'page': 1, 'count': 20}
```

### Conversation Suggestions

```python
import asyncio
from src import call_llm_for_suggestions_async

async def get_suggestions():
    prompt = "User A: Software Engineer at Google, Stanford CS grad. User B: Data Scientist at Meta, also Stanford CS grad."
    suggestions = await call_llm_for_suggestions_async(prompt)
    return suggestions

suggestions = asyncio.run(get_suggestions())
print(suggestions)
```

### Using the Cache

```python
from src import query_parsing_cache, suggestions_cache

# Check cache statistics
query_stats = query_parsing_cache.get_stats()
suggestions_stats = suggestions_cache.get_stats()
print(f"Query cache has {query_stats['active_entries']} active entries")
print(f"Suggestions cache has {suggestions_stats['active_entries']} active entries")

# Clear expired entries
query_cleared = query_parsing_cache.clear_expired()
suggestions_cleared = suggestions_cache.clear_expired()
print(f"Cleared {query_cleared} expired query entries")
print(f"Cleared {suggestions_cleared} expired suggestion entries")

# Get detailed cache information (suggestions cache only)
cache_info = suggestions_cache.get_cache_info()
print(f"Detailed cache info: {cache_info}")
```

### Data Models

```python
from src import NLSlots, normalize_slots

# Create a structured query
slots = NLSlots(
    name="John Doe",
    sector="CONSULTING",
    school="MIT",
    page=1,
    count=50
)

# Normalize raw LLM output
raw_data = {"name": " Alice Smith ", "sector": "finance", "count": ""}
normalized = normalize_slots(raw_data)
print(normalized)  # {'name': 'Alice Smith', 'sector': 'FINANCE', 'page': 1, 'count': 20}
```

## Module Details

### Cache Module (`src/cache/`)
- **QueryParsingCache**: TTL-based in-memory cache for LLM parsing results
- **SuggestionsCache**: TTL-based cache for conversation suggestions between users
- Automatic expiration and cleanup functionality
- Cache statistics and management
- Global instances available for direct use

### Models Module (`src/models/`)
- **NLSlots**: Pydantic model defining the schema for parsed queries
- **normalize_slots()**: Function to clean and validate raw LLM output
- Sector validation (CONSULTING, FINANCE)

### LLM Module (`src/llm/`)
- **ollama_client**: Sync/async Ollama API integration
- **suggestions**: Conversation starter generation
- **nl_parser**: Natural language query parsing with LLM integration
- Error handling and JSON extraction from LLM responses

### Clients Module (`src/clients/`)
- **PeopleAPI**: HTTP client for external people search and profile APIs
- Data formatting and result extraction utilities
- Comprehensive error handling for API interactions
- Global instance available for direct use

### Schemas Module (`src/schemas/`)
- **API Models**: Pydantic schemas for request/response validation
- **NLSearchRequest**: Natural language search request model
- **SearchResponse**: Search results response model
- **PeopleResponse**: User profile response model
- **CacheStats**: Cache statistics model

### Utils Module (`src/utils/`)
- **prompt_builder**: System and user prompt construction
- Configuration loading from JSON files

## Configuration

The system uses a JSON configuration file at `prompts/nl_parser.json` for LLM instructions and examples:

```json
{
  "instructions": "You are an expert at parsing natural language queries...",
  "examples": [
    {
      "input": "Find consultants from Harvard",
      "output": "{\"sector\": \"CONSULTING\", \"school\": \"Harvard\"}"
    }
  ]
}
```

## Error Handling

The package includes comprehensive error handling:
- LLM API failures with detailed error messages
- JSON parsing errors with fallback extraction
- Pydantic validation errors for data integrity
- Cache operation error handling

## Performance Features

- **Caching**: Reduces redundant LLM API calls
- **Async Support**: Non-blocking operations for better scalability
- **Batch Processing**: Efficient handling of multiple queries
- **Memory Management**: Automatic cleanup of expired cache entries

## Contributing

1. Follow the modular architecture
2. Add comprehensive docstrings to all functions
3. Include type hints for better code clarity
4. Write unit tests for new functionality
5. Update this README for any architectural changes