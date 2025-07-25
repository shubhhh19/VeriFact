"""
VeriFact - Configuration Module

This module handles configuration settings using environment variables with pydantic-settings.
"""

import os
from datetime import datetime, timezone
from typing import List, Optional

from pydantic import AnyHttpUrl, Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    PROJECT_NAME: str = "VeriFact"
    DEBUG: bool = Field(default=False, env="DEBUG")
    SECRET_KEY: str = Field(
        default="your-secret-key-here",
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
    DATABASE_URL: Optional[PostgresDsn] = None
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], values) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_SERVER"),
            path=f"{values.data.get('POSTGRES_DB') or ''}",
        )
    
    # Redis
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # Google Gemini API
    GEMINI_API_KEY: str = Field(..., env="GEMINI_API_KEY")
    
    # NewsAPI
    NEWS_API_KEY: str = Field(..., env="NEWS_API_KEY")
    
    # Rate Limiting
    RATE_LIMIT: int = Field(default=100, env="RATE_LIMIT")
    RATE_LIMIT_WINDOW: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # 1 hour
    
    # Model Config
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    def get_current_datetime(self) -> datetime:
        """Get current datetime in UTC"""
        return datetime.now(timezone.utc)


# Create settings instance
settings = Settings()
