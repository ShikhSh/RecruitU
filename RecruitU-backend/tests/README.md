# RecruitU Backend Tests

This directory contains the test suite for the RecruitU backend application.

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest configuration and fixtures
├── test_api_endpoints.py    # API endpoint tests
├── test_filter_utilities.py # User data filtering tests
└── test_config.py          # Configuration and settings tests
```

## Test Categories

### 1. API Endpoint Tests (`test_api_endpoints.py`)
- **Health Check**: Tests `/health` endpoint functionality
- **Cache Management**: Tests `/cache/clear` endpoint
- **Natural Language Search**: Tests `/search_nl` endpoint structure
- **People API**: Tests `/people` endpoint validation
- **Conversation Suggestions**: Tests `/suggest_conversation` endpoint

### 2. Filter Utility Tests (`test_filter_utilities.py`)
- **Search Data Filtering**: Tests filtering of search result user data
- **Profile Data Filtering**: Tests filtering of user profile data
- **Edge Cases**: Tests handling of empty/partial data
- **Privacy Protection**: Verifies sensitive data is removed

### 3. Configuration Tests (`test_config.py`)
- **Default Settings**: Tests default configuration values
- **Custom Settings**: Tests settings override functionality
- **Environment Variables**: Tests environment variable loading
- **Validation**: Tests settings validation and type conversion

## Running Tests

### Quick Start (Recommended)
```bash
# From the RecruitU-backend directory
./run_tests.sh
```

### Manual Test Execution

1. **Activate Virtual Environment** (if not already activated):
```bash
cd /home/ubuntu/RecruitU
source .venv/bin/activate
```

2. **Install Test Dependencies**:
```bash
pip install pytest pytest-asyncio
```

3. **Run Tests**:
```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_config.py

# Run specific test function
python -m pytest tests/test_config.py::test_settings_defaults

# Run tests with detailed output
python -m pytest -v --tb=long
```

### Test Environment Variables

The tests use these environment variables:
- `LLM_PROVIDER=none` - Disables LLM functionality for faster tests
- `PEOPLE_API_BASE` - Uses test API endpoint

## Test Fixtures

### Available Fixtures (from `conftest.py`)
- `client`: FastAPI TestClient for API testing
- `test_settings`: Test-safe Settings configuration
- `sample_user_data`: Sample user profile data
- `sample_search_user_data`: Sample search result data

## Test Coverage

The tests cover:
- ✅ Basic API endpoint functionality
- ✅ Configuration and settings management
- ✅ User data filtering and privacy protection
- ✅ Error handling and validation
- ✅ Cache management functionality

## Adding New Tests

1. Create test files following the `test_*.py` pattern
2. Use the provided fixtures from `conftest.py`
3. Follow the existing test structure and naming conventions
4. Include docstrings explaining what each test verifies

Example test function:
```python
def test_new_functionality(client, test_settings):
    """
    Test new functionality.
    
    This test verifies that:
    - Expected behavior occurs
    - Error cases are handled
    """
    # Test implementation
    response = client.get("/new-endpoint")
    assert response.status_code == 200
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're in the RecruitU-backend directory and virtual environment is activated
2. **Missing Dependencies**: Run `pip install pytest pytest-asyncio`
3. **Path Issues**: The tests automatically add the project root to Python path
4. **Environment Variables**: Tests set safe defaults, but you can override them

### Getting Help

- Check the test output for detailed error messages
- Use `-v` flag for verbose output
- Use `--tb=long` for detailed tracebacks
- Ensure all dependencies are installed in your virtual environment
