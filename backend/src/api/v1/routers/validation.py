"""
Validation Router

This module contains the API endpoints for news validation operations.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.deps import get_db
from src.schemas.validation import (
    ValidationRequest,
    ValidationResponse,
    ValidationResult,
    ValidationStatus
)
from src.services.validation import ValidationService

router = APIRouter(prefix="/validation", tags=["validation"])


@router.post("/validate", response_model=ValidationResponse)
async def validate_article(
    request: ValidationRequest,
    db: AsyncSession = Depends(get_db),
) -> ValidationResponse:
    """
    Validate a news article
    
    This endpoint validates a news article by:
    1. Extracting key claims
    2. Verifying sources
    3. Checking for contradictions
    4. Generating credibility score
    """
    service = ValidationService(db)
    try:
        result = await service.validate_article(request)
        return ValidationResponse(
            success=True,
            validation_id=str(result.id),
            status=result.status,
            results=result
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation failed: {str(e)}",
        )


@router.get("/{validation_id}", response_model=ValidationResponse)
async def get_validation_result(
    validation_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ValidationResponse:
    """
    Get validation result by ID
    
    Retrieve the results of a validation operation.
    """
    service = ValidationService(db)
    result = await service.get_validation_result(validation_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Validation result with ID {validation_id} not found",
        )
    return ValidationResponse(
        success=True,
        validation_id=str(result.id),
        status=result.status,
        results=result
    )


@router.get("/article/{article_id}/results", response_model=List[ValidationResult])
async def get_article_validations(
    article_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> List[ValidationResult]:
    """
    Get all validation results for an article
    
    Retrieve all validation results associated with a specific article.
    """
    service = ValidationService(db)
    results = await service.get_article_validations(article_id)
    return results


@router.post("/{validation_id}/retry")
async def retry_validation(
    validation_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ValidationResponse:
    """
    Retry a failed validation
    
    Retry a validation that previously failed.
    """
    service = ValidationService(db)
    try:
        result = await service.retry_validation(validation_id)
        return ValidationResponse(
            success=True,
            validation_id=str(result.id),
            status=result.status,
            results=result
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Retry failed: {str(e)}",
        ) 