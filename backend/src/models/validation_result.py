"""
News Validator Agent - Validation Result Model
Contains the database model for validation results
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, TYPE_CHECKING, Dict, Any
from uuid import UUID

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Float, Boolean, JSON, Index, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base

if TYPE_CHECKING:
    from .news_article import NewsArticle


class ValidationStatus(str, Enum):
    """Status of a validation result"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    

class ValidationType(str, Enum):
    """Type of validation performed"""
    FACT_CHECK = "fact_check"
    SOURCE_VERIFICATION = "source_verification"
    CONTRADICTION_CHECK = "contradiction_check"
    CREDIBILITY_SCORE = "credibility_score"
    

class ValidationResult(Base):
    """Validation result model for storing validation outcomes"""
    
    __tablename__ = "validation_results"
    
    # Relationships
    article_id: Mapped[UUID] = Column(
        PG_UUID(as_uuid=True), 
        ForeignKey("news_articles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    article: Mapped["NewsArticle"] = relationship("NewsArticle", back_populates="validations")
    
    # Validation metadata
    validation_type: Mapped[ValidationType] = Column(
        SQLEnum(ValidationType, name="validation_type_enum"),
        nullable=False,
        index=True
    )
    status: Mapped[ValidationStatus] = Column(
        SQLEnum(ValidationStatus, name="validation_status_enum"),
        default=ValidationStatus.PENDING,
        nullable=False,
        index=True
    )
    
    # Validation results
    score: Mapped[Optional[float]] = Column(Float, index=True)  # 0.0 to 1.0
    confidence: Mapped[Optional[float]] = Column(Float)  # 0.0 to 1.0
    is_valid: Mapped[Optional[bool]] = Column(Boolean, index=True)
    
    # Detailed results
    details: Mapped[Optional[Dict[str, Any]]] = Column(JSONB, default=dict)
    error: Mapped[Optional[str]] = Column(Text)
    
    # Processing metadata
    started_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True))
    retry_count: Mapped[int] = Column(default=0)
    
    # Indexes
    __table_args__ = (
        Index("idx_validation_article_type_status", "article_id", "validation_type", "status"),
        Index("idx_validation_score", "score"),
        Index("idx_validation_created_at", "created_at"),
    )
    
    def __repr__(self) -> str:
        return (
            f"<ValidationResult(id={self.id}, "
            f"article_id={self.article_id}, "
            f"type={self.validation_type}, "
            f"status={self.status}, "
            f"score={self.score})>"
        )
    
    def to_dict(self, include_article: bool = False) -> dict:
        """Convert model to dictionary"""
        result = {
            "id": str(self.id),
            "article_id": str(self.article_id),
            "validation_type": self.validation_type.value,
            "status": self.status.value,
            "score": self.score,
            "confidence": self.confidence,
            "is_valid": self.is_valid,
            "details": self.details,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        
        if include_article and self.article:
            result["article"] = self.article.to_dict()
            
        return result
    
    def mark_started(self) -> None:
        """Mark validation as started"""
        self.status = ValidationStatus.IN_PROGRESS
        self.started_at = datetime.utcnow()
        self.retry_count += 1
    
    def mark_completed(self, result: Dict[str, Any]) -> None:
        """Mark validation as completed with results"""
        self.status = ValidationStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        
        # Update result fields
        self.score = result.get("score")
        self.confidence = result.get("confidence")
        self.is_valid = result.get("is_valid")
        self.details = result.get("details", {})
    
    def mark_failed(self, error: str) -> None:
        """Mark validation as failed with error"""
        self.status = ValidationStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error = str(error)[:1000]  # Truncate long errors
        
        # Update retry count
        self.retry_count += 1
