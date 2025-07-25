"""
News Validator Agent - Base Database Model
Contains the base SQLAlchemy model with common functionality
"""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Mapped, mapped_column

from src.config import settings


@as_declarative()
class Base:
    """Base database model with common fields and methods"""
    
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        primary_key=True, 
        index=True, 
        default=uuid4
    )
    created_at: Mapped[datetime] = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = Column(
        DateTime(timezone=True), 
        nullable=True
    )
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name"""
        return cls.__name__.lower()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            c.name: getattr(self, c.name) 
            for c in self.__table__.columns  # type: ignore
        }
    
    def __repr__(self) -> str:
        """String representation of the model"""
        return f"<{self.__class__.__name__}(id={self.id})>"
