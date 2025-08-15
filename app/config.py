# Configuration settings for the RecruitU application
from pydantic import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PEOPLE_API_BASE: str = "https://staging.recruitu.com/api/2330891ccbb5404d86277521b9c3f87b490c3fa0e3c9448ba7bd9a587a65c2f8"  # staging base
    TIMEOUT_SECONDS: int = 15

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()