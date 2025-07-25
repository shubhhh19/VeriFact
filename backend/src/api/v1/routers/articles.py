"""
Article Router

This module contains the API endpoints for article operations.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.deps import get_db
from src.schemas.article import Article, ArticleCreate, ArticleList, ArticleUpdate
from src.services.article import ArticleService

router = APIRouter(prefix="/articles", tags=["articles"])


@router.post("/", response_model=Article, status_code=status.HTTP_201_CREATED)
async def create_article(
    article_data: ArticleCreate,
    db: AsyncSession = Depends(get_db),
) -> Article:
    """
    Create a new article
    
    This endpoint creates a new article with the provided data.
    """
    service = await ArticleService.get_service(db)
    try:
        return await service.create_article(article_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create article: {str(e)}",
        )


@router.get("/{article_id}", response_model=Article)
async def get_article(
    article_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Article:
    """
    Get article by ID
    
    Retrieve detailed information about a specific article.
    """
    service = await ArticleService.get_service(db)
    article = await service.get_article(article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID {article_id} not found",
        )
    return article


@router.get("/", response_model=ArticleList)
async def list_articles(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db),
) -> ArticleList:
    """
    List articles with pagination
    
    Retrieve a paginated list of articles, optionally filtered by status.
    """
    service = await ArticleService.get_service(db)
    skip = (page - 1) * size
    articles, total = await service.list_articles(
        skip=skip, 
        limit=size,
        status=status,
    )
    
    return ArticleList(
        items=articles,
        total=total,
        page=page,
        size=len(articles),
        pages=(total + size - 1) // size if size > 0 else 1,
    )


@router.patch("/{article_id}", response_model=Article)
async def update_article(
    article_id: UUID,
    update_data: ArticleUpdate,
    db: AsyncSession = Depends(get_db),
) -> Article:
    """
    Update an article
    
    Partially update an article with the provided fields.
    """
    service = await ArticleService.get_service(db)
    article = await service.update_article(article_id, update_data)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID {article_id} not found",
        )
    return article


@router.delete(
    "/{article_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Article not found"}},
)
async def delete_article(
    article_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete an article
    
    Permanently delete an article by its ID.
    """
    service = await ArticleService.get_service(db)
    success = await service.delete_article(article_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID {article_id} not found",
        )
    return None
