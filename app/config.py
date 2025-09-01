from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import Field


class Settings(BaseSettings):
    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "astrology_db"
    
    # JWT Configuration
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 600
    
    # App Configuration
    app_name: str = "Astrology Platform"
    debug: bool = True
    
    # OpenAI Configuration
    openai_api_key: str = Field(default="sk-proj-1234567890", alias="open_ai_key")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Allow extra fields to be ignored


settings = Settings()
