"""
News Validator Agent - News Article Model
Contains the database model for news articles
"""

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base

if TYPE_CHECKING:
    from .validation_result import ValidationResult


class NewsArticle(Base):
    """News article model for storing article information"""
    
    __tablename__ = "news_articles"
    
    # Article metadata
    title: Mapped[str] = Column(String(500), nullable=False, index=True)
    url: Mapped[str] = Column(String(1000), unique=True, nullable=False, index=True)
    source: Mapped[str] = Column(String(200), nullable=False, index=True)
    source_id: Mapped[Optional[str]] = Column(String(200), index=True)
    author: Mapped[Optional[str]] = Column(String(200))
    
    # Content
    content: Mapped[Optional[str]] = Column(Text)
    summary: Mapped[Optional[str]] = Column(Text)
    excerpt: Mapped[Optional[str]] = Column(Text)
    
    # Media
    image_url: Mapped[Optional[str]] = Column(String(1000))
    video_url: Mapped[Optional[str]] = Column(String(1000))
    
    # Dates
    published_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), index=True)
    retrieved_at: Mapped[datetime] = Column(DateTime(timezone=True), server_default="now()")
    
    # Additional metadata
    language: Mapped[Optional[str]] = Column(String(10), default="en")
    category: Mapped[Optional[str]] = Column(String(100), index=True)
    tags: Mapped[Optional[List[str]]] = Column(JSON, default=list)
    metadata_: Mapped[Optional[dict]] = Column("metadata", JSONB, default=dict)
    
    # Relationships
    validations: Mapped[List["ValidationResult"]] = relationship(
        "ValidationResult", 
        back_populates="article",
        cascade="all, delete-orphan"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_articles_source_published", "source", "published_at"),
        Index("idx_articles_published_at", "published_at"),
        Index("idx_articles_retrieved_at", "retrieved_at"),
    )
    
    def __repr__(self) -> str:
        return f"<NewsArticle(id={self.id}, title='{self.title[:50]}...', source='{self.source}')>"
    
    def to_dict(self, include_related: bool = False) -> dict:
        """Convert model to dictionary"""
        result = {
            "id": str(self.id),
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "source_id": self.source_id,
            "author": self.author,
            "content": self.content,
            "summary": self.summary,
            "excerpt": self.excerpt,
            "image_url": self.image_url,
            "video_url": self.video_url,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "retrieved_at": self.retrieved_at.isoformat() if self.retrieved_at else None,
            "language": self.language,
            "category": self.category,
            "tags": self.tags,
            "metadata": self.metadata_,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        
        if include_related and self.validations:
            result["validations"] = [v.to_dict() for v in self.validations]
            
        return result
