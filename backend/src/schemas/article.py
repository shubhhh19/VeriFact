"""
Article Schemas

This module contains Pydantic models for article-related requests and responses.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class ArticleSource(str, Enum):
    """Enum for article sources"""
    DIRECT_INPUT = "direct_input"
    URL = "url"
    API = "api"


class ArticleBase(BaseModel):
    """Base article model with common fields"""
    title: str = Field(..., max_length=500, description="Article title")
    url: Optional[HttpUrl] = Field(None, description="Article URL if available")
    source: ArticleSource = Field(..., description="How the article was submitted")
    content: Optional[str] = Field(None, description="Article content if available")
    published_at: Optional[datetime] = Field(None, description="Publication date")
    author: Optional[str] = Field(None, max_length=200, description="Article author")
    image_url: Optional[HttpUrl] = Field(None, description="Featured image URL")
    language: str = Field("en", description="Article language code (ISO 639-1)")


class ArticleCreate(ArticleBase):
    """Schema for creating a new article"""
    pass


class ArticleUpdate(BaseModel):
    """Schema for updating an article"""
    title: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[dict] = None


class ArticleInDBBase(ArticleBase):
    """Base model for database representation"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    status: str

    class Config:
        from_attributes = True


class Article(ArticleInDBBase):
    """Schema for article responses"""
    pass


class ArticleInDB(ArticleInDBBase):
    """Schema for article in database"""
    pass


class ArticleList(BaseModel):
    """Schema for listing articles with pagination"""
    items: List[Article]
    total: int
    page: int
    size: int
    pages: int
