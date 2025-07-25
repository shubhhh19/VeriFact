"""
Article Service

This module contains the business logic for article-related operations.
"""

from datetime import datetime, timezone
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.news_article import NewsArticle
from src.schemas.article import ArticleCreate, ArticleUpdate, ArticleInDB


class ArticleService:
    """Service for article-related operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_article(self, article_data: ArticleCreate) -> ArticleInDB:
        """Create a new article"""
        db_article = NewsArticle(
            id=uuid4(),
            title=article_data.title,
            url=str(article_data.url) if article_data.url else None,
            source=article_data.source,
            content=article_data.content,
            published_at=article_data.published_at,
            author=article_data.author,
            image_url=str(article_data.image_url) if article_data.image_url else None,
            language=article_data.language,
            status="pending",
        )
        
        self.db.add(db_article)
        await self.db.commit()
        await self.db.refresh(db_article)
        
        return await self._map_to_schema(db_article)
    
    async def get_article(self, article_id: UUID) -> Optional[ArticleInDB]:
        """Get an article by ID"""
        result = await self.db.execute(
            select(NewsArticle).where(NewsArticle.id == article_id)
        )
        db_article = result.scalar_one_or_none()
        
        if not db_article:
            return None
            
        return await self._map_to_schema(db_article)
    
    async def list_articles(
        self,
        skip: int = 0,
        limit: int = 10,
        status: Optional[str] = None,
    ) -> Tuple[List[ArticleInDB], int]:
        """List articles with pagination"""
        query = select(NewsArticle)
        
        if status:
            query = query.where(NewsArticle.status == status)
        
        # Get total count for pagination
        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar()
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await self.db.execute(query)
        articles = result.scalars().all()
        
        # Convert to schemas
        article_schemas = [
            await self._map_to_schema(article) for article in articles
        ]
        
        return article_schemas, total
    
    async def update_article(
        self, article_id: UUID, update_data: ArticleUpdate
    ) -> Optional[ArticleInDB]:
        """Update an article"""
        update_values = {
            k: v for k, v in update_data.model_dump(exclude_unset=True).items()
            if v is not None
        }
        
        if not update_values:
            return await self.get_article(article_id)
            
        update_values["updated_at"] = datetime.now(timezone.utc)
        
        result = await self.db.execute(
            update(NewsArticle)
            .where(NewsArticle.id == article_id)
            .values(**update_values)
            .returning(NewsArticle)
        )
        
        db_article = result.scalar_one_or_none()
        
        if not db_article:
            return None
            
        await self.db.commit()
        await self.db.refresh(db_article)
        
        return await self._map_to_schema(db_article)
    
    async def delete_article(self, article_id: UUID) -> bool:
        """Delete an article"""
        result = await self.db.execute(
            delete(NewsArticle)
            .where(NewsArticle.id == article_id)
            .returning(NewsArticle.id)
        )
        
        if not result.scalar_one_or_none():
            return False
            
        await self.db.commit()
        return True
    
    async def _map_to_schema(self, db_article: NewsArticle) -> ArticleInDB:
        """Map database model to Pydantic schema"""
        return ArticleInDB(
            id=db_article.id,
            title=db_article.title,
            url=db_article.url,
            source=db_article.source,
            content=db_article.content,
            published_at=db_article.published_at,
            author=db_article.author,
            image_url=db_article.image_url,
            language=db_article.language,
            status=db_article.status,
            created_at=db_article.created_at,
            updated_at=db_article.updated_at,
        )
    
    @classmethod
    async def get_service(cls, db: AsyncSession):
        """Factory method to create a service instance"""
        return cls(db)
