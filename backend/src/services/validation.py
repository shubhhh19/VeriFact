"""
Validation Service

This module contains the business logic for article validation operations.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import select, update, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.news_article import NewsArticle
from src.models.validation_result import ValidationResult as ValidationResultModel
from src.schemas.validation import (
    ValidationRequest,
    ValidationResult,
    ValidationResultCreate,
    ValidationResultUpdate,
    ValidationStatus,
    ValidationType,
    ClaimAnalysis,
    EvidenceSource,
)
from src.services.article import ArticleService

logger = logging.getLogger(__name__)


class ValidationService:
    """Service for validation-related operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_validation(
        self, validation_data: ValidationRequest
    ) -> ValidationResult:
        """Create a new validation request"""
        # Check if article exists
        article_service = await ArticleService.get_service(self.db)
        article = await article_service.get_article(validation_data.article_id)
        
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Article with ID {validation_data.article_id} not found",
            )
        
        # Create validation result
        db_validation = ValidationResultModel(
            id=uuid4(),
            article_id=validation_data.article_id,
            validation_type=validation_data.validation_type,
            status=ValidationStatus.PENDING,
            metadata=validation_data.metadata or {},
            priority=validation_data.priority,
        )
        
        self.db.add(db_validation)
        await self.db.commit()
        await self.db.refresh(db_validation)
        
        # Trigger async validation
        # In a real implementation, this would be sent to a task queue
        await self._start_validation(db_validation.id)
        
        return await self._map_to_schema(db_validation)
    
    async def get_validation(self, validation_id: UUID) -> Optional[ValidationResult]:
        """Get a validation result by ID"""
        result = await self.db.execute(
            select(ValidationResultModel)
            .where(ValidationResultModel.id == validation_id)
        )
        db_validation = result.scalar_one_or_none()
        
        if not db_validation:
            return None
            
        return await self._map_to_schema(db_validation)
    
    async def list_validations(
        self,
        article_id: Optional[UUID] = None,
        status: Optional[ValidationStatus] = None,
        validation_type: Optional[ValidationType] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[List[ValidationResult], int]:
        """List validation results with filtering and pagination"""
        query = select(ValidationResultModel)
        
        # Apply filters
        if article_id:
            query = query.where(ValidationResultModel.article_id == article_id)
        if status:
            query = query.where(ValidationResultModel.status == status)
        if validation_type:
            query = query.where(ValidationResultModel.validation_type == validation_type)
        
        # Get total count for pagination
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await self.db.execute(query)
        validations = result.scalars().all()
        
        # Convert to schemas
        validation_schemas = [
            await self._map_to_schema(validation) for validation in validations
        ]
        
        return validation_schemas, total
    
    async def update_validation(
        self, validation_id: UUID, update_data: ValidationResultUpdate
    ) -> Optional[ValidationResult]:
        """Update a validation result"""
        update_values = {
            k: v for k, v in update_data.model_dump(exclude_unset=True).items()
            if v is not None
        }
        
        if not update_values:
            return await self.get_validation(validation_id)
        
        # If status is being updated to completed, set completed_at
        if "status" in update_values and update_values["status"] == ValidationStatus.COMPLETED:
            update_values["completed_at"] = datetime.now(timezone.utc)
        
        update_values["updated_at"] = datetime.now(timezone.utc)
        
        result = await self.db.execute(
            update(ValidationResultModel)
            .where(ValidationResultModel.id == validation_id)
            .values(**update_values)
            .returning(ValidationResultModel)
        )
        
        db_validation = result.scalar_one_or_none()
        
        if not db_validation:
            return None
            
        await self.db.commit()
        await self.db.refresh(db_validation)
        
        return await self._map_to_schema(db_validation)
    
    async def _start_validation(self, validation_id: UUID) -> None:
        """Start the validation process (to be run asynchronously)"""
        # In a real implementation, this would publish a message to a task queue
        # For now, we'll just simulate the validation
        from src.tasks.validation_tasks import process_validation
        
        # This would be done by a task queue in production
        await process_validation(validation_id, self.db)
    
    async def _map_to_schema(
        self, db_validation: ValidationResultModel
    ) -> ValidationResult:
        """Map database model to Pydantic schema"""
        # Parse the raw response if it exists
        claims_analysis = []
        raw_response = db_validation.raw_response or {}
        
        if "claims_analysis" in raw_response:
            for claim_data in raw_response["claims_analysis"]:
                try:
                    claims_analysis.append(ClaimAnalysis(**claim_data))
                except Exception as e:
                    logger.error(f"Error parsing claim analysis: {e}")
        
        return ValidationResult(
            id=db_validation.id,
            article_id=db_validation.article_id,
            status=db_validation.status,
            validation_type=db_validation.validation_type,
            summary=db_validation.summary,
            overall_confidence=db_validation.overall_confidence,
            is_credible=db_validation.is_credible,
            error=db_validation.error,
            claims_analysis=claims_analysis,
            created_at=db_validation.created_at,
            updated_at=db_validation.updated_at,
            completed_at=db_validation.completed_at,
        )
    
    @classmethod
    async def get_service(cls, db: AsyncSession):
        """Factory method to create a service instance"""
        return cls(db)
