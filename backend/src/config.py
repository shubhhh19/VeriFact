"""
VeriFact - Configuration Module

This module handles configuration settings using environment variables with pydantic-settings.
"""

import os
from datetime import datetime, timezone
from typing import Any, List, Optional, Union

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, Field, field_validator, PostgresDsn
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    PROJECT_NAME: str = "VeriFact"
    DEBUG: bool = Field(default=False, env="DEBUG")
    TESTING: bool = Field(default=False, env="TESTING")
    SECRET_KEY: str = Field(
        default=os.getenv("SECRET_KEY", "test-secret-key-32-characters-long-123"),
        env="SECRET_KEY",
        min_length=32,
        max_length=100,
    )
    
    # API
    API_V1_STR: str = "/api/v1"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Database
    POSTGRES_SERVER: str = Field(default="localhost", env="POSTGRES_SERVER")
    POSTGRES_USER: str = Field(default="postgres", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="postgres", env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(default="verifact", env="POSTGRES_DB")
    DATABASE_URL: Union[str, PostgresDsn] = Field(
        default=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db"),
        env="DATABASE_URL"
    )
    
    # External Services
    GEMINI_API_KEY: str = Field(
        default=os.getenv("GEMINI_API_KEY", "test-gemini-api-key"),
        env="GEMINI_API_KEY"
    )
    
    NEWS_API_KEY: str = Field(
        default=os.getenv("NEWS_API_KEY", "test-news-api-key"),
        env="NEWS_API_KEY"
    )
    
    # Redis
    REDIS_URL: str = Field(
        default=os.getenv("REDIS_URL", "redis://localhost:6379/1"),
        env="REDIS_URL"
    )
    
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")
    
    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: Optional[str], info) -> Any:
        if v and isinstance(v, str):
            # If it's a SQLite URL, return as is
            if v.startswith('sqlite'):
                return v
            # Otherwise, validate as Postgres URL
            return PostgresDsn(v)
        
        # Build from components if no URL is provided
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=info.data.get("POSTGRES_USER"),
            password=info.data.get("POSTGRES_PASSWORD"),
            host=info.data.get("POSTGRES_SERVER"),
            path=f"{info.data.get('POSTGRES_DB') or ''}",
        )

    def get_current_datetime(self) -> datetime:
        """Get current datetime in UTC"""
        return datetime.now(timezone.utc)

# Create settings instance
settings = Settings()
