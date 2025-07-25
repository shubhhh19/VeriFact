"""
Validation Router

This module contains the API endpoints for validation operations.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.deps import get_db
from src.schemas.validation import (
    ValidationRequest,
    ValidationResult,
    ValidationResultList,
    ValidationStatus,
    ValidationType,
)
from src.services.validation import ValidationService

router = APIRouter(prefix="/validations", tags=["validations"])


@router.post(
    "/", 
    response_model=ValidationResult, 
    status_code=status.HTTP_201_CREATED,
    summary="Request validation of an article",
    description="""
    Submit an article for validation.
    
    This endpoint starts the validation process for an article.
    The validation will be performed asynchronously.
    """
)
async def create_validation(
    validation_data: ValidationRequest,
    db: AsyncSession = Depends(get_db),
) -> ValidationResult:
    """
    Create a new validation request for an article.
    
    Args:
        validation_data: The validation request data
        db: Database session dependency
        
    Returns:
        The created validation result with initial status
    """
    service = await ValidationService.get_service(db)
    try:
        return await service.create_validation(validation_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create validation: {str(e)}",
        )


@router.get(
    "/{validation_id}",
    response_model=ValidationResult,
    summary="Get validation result by ID",
    description="Retrieve detailed information about a specific validation result.",
)
async def get_validation(
    validation_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ValidationResult:
    """
    Get a validation result by its ID.
    
    Args:
        validation_id: The ID of the validation to retrieve
        db: Database session dependency
        
    Returns:
        The validation result
    """
    service = await ValidationService.get_service(db)
    validation = await service.get_validation(validation_id)
    if not validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Validation with ID {validation_id} not found",
        )
    return validation


@router.get(
    "/",
    response_model=ValidationResultList,
    summary="List validation results",
    description="Retrieve a paginated list of validation results with optional filtering.",
)
async def list_validations(
    article_id: Optional[UUID] = Query(None, description="Filter by article ID"),
    status: Optional[ValidationStatus] = Query(None, description="Filter by status"),
    validation_type: Optional[ValidationType] = Query(None, description="Filter by validation type"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
) -> ValidationResultList:
    """
    List validation results with filtering and pagination.
    
    Args:
        article_id: Filter by article ID
        status: Filter by validation status
        validation_type: Filter by validation type
        page: Page number (1-based)
        size: Number of items per page (max 100)
        db: Database session dependency
        
    Returns:
        Paginated list of validation results
    """
    service = await ValidationService.get_service(db)
    skip = (page - 1) * size
    validations, total = await service.list_validations(
        article_id=article_id,
        status=status,
        validation_type=validation_type,
        skip=skip,
        limit=size,
    )
    
    return ValidationResultList(
        items=validations,
        total=total,
        page=page,
        size=len(validations),
        pages=(total + size - 1) // size if size > 0 else 1,
    )


@router.get(
    "/article/{article_id}",
    response_model=List[ValidationResult],
    summary="Get validations for an article",
    description="Retrieve all validation results for a specific article.",
)
async def get_validations_for_article(
    article_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> List[ValidationResult]:
    """
    Get all validation results for a specific article.
    
    Args:
        article_id: The ID of the article
        db: Database session dependency
        
    Returns:
        List of validation results for the article
    """
    service = await ValidationService.get_service(db)
    validations, _ = await service.list_validations(article_id=article_id, limit=100)
    return validations
