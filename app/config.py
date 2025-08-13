# # Configuration settings for the RecruitU application

# import os

# class Config:
#     DEBUG = os.getenv('DEBUG', 'False') == 'True'
#     DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///recruitu.db')
#     SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key_here')
#     ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
#     API_KEY = os.getenv('API_KEY', 'your_api_key_here')

from pydantic import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PEOPLE_API_BASE: str = "https://staging.recruitu.com/api/2330891ccbb5404d86277521b9c3f87b490c3fa0e3c9448ba7bd9a587a65c2f8"  # staging base

    TIMEOUT_SECONDS: int = 15

    # LLM_PROVIDER: str = "openai"       # none | openai | anthropic | azure_openai
    # OPENAI_MODEL: str = "gpt-4o-mini"


    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()