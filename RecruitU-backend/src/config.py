"""
Configuration Settings for RecruitU Backend

This module contains all configuration settings and environment variable
management for the RecruitU application.
"""

from pydantic import BaseSettings
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    
    This class defines all configuration parameters for the application,
    with sensible defaults and support for environment variable overrides.
    
    Attributes:
        PEOPLE_API_BASE (str): Base URL for the people API
        TIMEOUT_SECONDS (int): HTTP request timeout in seconds
        LLM_PROVIDER (str): LLM provider type ('ollama' or 'none')
        OLLAMA_HOST (str): Ollama server URL
        OLLAMA_MODEL (str): Ollama model name
    """
    
    # API Configuration
    PEOPLE_API_BASE: str = "https://staging.recruitu.com/api/2330891ccbb5404d86277521b9c3f87b490c3fa0e3c9448ba7bd9a587a65c2f8"
    TIMEOUT_SECONDS: int = 15
    
    # LLM Configuration (read from environment)
    LLM_PROVIDER: str = "ollama"
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1:8b"

    class Config:
        """Pydantic configuration class."""
        env_file = "../.env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings with caching.
    
    This function returns a cached instance of the Settings class
    to avoid re-reading environment variables on every request.
    
    Returns:
        Settings: Application configuration settings
    """
    settings = Settings()
    
    # Debug: Print loaded environment variables
    print(f"Loaded settings:")
    print(f"  LLM_PROVIDER: {settings.LLM_PROVIDER}")
    print(f"  OLLAMA_HOST: {settings.OLLAMA_HOST}")
    print(f"  OLLAMA_MODEL: {settings.OLLAMA_MODEL}")
    print(f"  PEOPLE_API_BASE: {settings.PEOPLE_API_BASE}")
    
    return settings


# Export for convenience
settings = get_settings()
