# RecruitU Backend - Natural Language Processing Module

A modular Python package for parsing natural language queries into structured search parameters using Large Language Models (LLMs), primarily Ollama.

## Features

- **Natural Language Query Parsing**: Convert unstructured text queries into structured search parameters
- **LLM Integration**: Support for Ollama API with async/sync operations
- **Intelligent Caching**: Cache system to reduce redundant API calls
- **Conversation Suggestions**: Generate networking conversation starters based on user profiles
- **Data Validation**: Pydantic models for robust data validation and type safety

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

## Environment Variables

- `OLLAMA_HOST`: Ollama server URL (default: `http://localhost:11434`)
- `OLLAMA_MODEL`: Model to use (default: `llama3.1:8b`)
- `LLM_PROVIDER`: LLM provider to use (default: `ollama`)

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

## Tests:
To run test:
```bash
python -m pytest -v
```