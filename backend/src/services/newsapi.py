"""
NewsAPI Service

This module provides integration with NewsAPI to verify sources and find
related articles for fact-checking purposes.
"""

import logging
import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlparse, quote_plus

from pydantic import BaseModel, Field, HttpUrl, validator
from ..config import settings

logger = logging.getLogger(__name__)

class NewsAPISource(BaseModel):
    """Model for a news source from NewsAPI."""
    id: Optional[str] = Field(
        None,
        description="The identifier of the news source"
    )
    name: str = Field(
        ...,
        description="The name of the news source"
    )
    description: Optional[str] = Field(
        None,
        description="A brief description of the news source"
    )
    url: Optional[HttpUrl] = Field(
        None,
        description="The URL of the news source's homepage"
    )
    category: Optional[str] = Field(
        None,
        description="The category of the news source (e.g., 'technology', 'business')"
    )
    language: Optional[str] = Field(
        None,
        description="The language of the news source (e.g., 'en')"
    )
    country: Optional[str] = Field(
        None,
        description="The country where the news source is based (ISO 3166-1 alpha-2 code)"
    )

class NewsAPIArticle(BaseModel):
    """Model for an article from NewsAPI."""
    source: Dict[str, str] = Field(
        ...,
        description="The source of the article"
    )
    author: Optional[str] = Field(
        None,
        description="The author of the article"
    )
    title: str = Field(
        ...,
        description="The headline of the article"
    )
    description: Optional[str] = Field(
        None,
        description="A brief description of the article"
    )
    url: HttpUrl = Field(
        ...,
        description="The URL of the article"
    )
    url_to_image: Optional[HttpUrl] = Field(
        None,
        description="URL to an image associated with the article"
    )
    published_at: Optional[datetime] = Field(
        None,
        description="The date and time when the article was published (ISO 8601)"
    )
    content: Optional[str] = Field(
        None,
        description="The full content of the article (may be truncated)"
    )
    
    @validator('published_at', pre=True)
    def parse_published_at(cls, v):
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return None
        return v

class NewsAPISearchResponse(BaseModel):
    """Model for the response from NewsAPI's search endpoint."""
    status: str = Field(
        ...,
        description="The status of the API request"
    )
    total_results: int = Field(
        ...,
        description="The total number of results available for your request"
    )
    articles: List[NewsAPIArticle] = Field(
        default_factory=list,
        description="The list of articles matching your request"
    )
    code: Optional[str] = Field(
        None,
        description="Error code if the request failed"
    )
    message: Optional[str] = Field(
        None,
        description="Error message if the request failed"
    )

class NewsAPISourceResponse(BaseModel):
    """Model for the response from NewsAPI's sources endpoint."""
    status: str = Field(
        ...,
        description="The status of the API request"
    )
    sources: List[NewsAPISource] = Field(
        default_factory=list,
        description="The list of news sources matching your request"
    )
    code: Optional[str] = Field(
        None,
        description="Error code if the request failed"
    )
    message: Optional[str] = Field(
        None,
        description="Error message if the request failed"
    )

class NewsAPIService:
    """Service for interacting with the NewsAPI."""
    
    BASE_URL = "https://newsapi.org/v2"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the NewsAPI service.
        
        Args:
            api_key: Your NewsAPI API key (defaults to settings.NEWSAPI_API_KEY)
        """
        self.api_key = api_key or settings.NEWSAPI_API_KEY
        self.session = None
    
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def start(self):
        """Initialize the HTTP session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the NewsAPI.
        
        Args:
            endpoint: The API endpoint to call (e.g., '/everything')
            params: Query parameters for the request
            
        Returns:
            The parsed JSON response
            
        Raises:
            ValueError: If the API returns an error
        """
        if not self.api_key:
            raise ValueError("NewsAPI API key is not configured")
            
        if not self.session or self.session.closed:
            await self.start()
        
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "X-Api-Key": self.api_key,
            "User-Agent": "VeriFact/1.0"
        }
        
        try:
            async with self.session.get(url, params=params, headers=headers) as response:
                data = await response.json()
                
                if response.status != 200:
                    error_msg = data.get('message', 'Unknown error')
                    error_code = data.get('code', 'unknown')
                    raise ValueError(f"NewsAPI error ({error_code}): {error_msg}")
                
                return data
                
        except aiohttp.ClientError as e:
            logger.error(f"NewsAPI request failed: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to fetch data from NewsAPI: {str(e)}")
    
    async def search_articles(
        self,
        query: str,
        sources: Optional[List[str]] = None,
        domains: Optional[List[str]] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        language: str = "en",
        sort_by: str = "relevancy",
        page_size: int = 10,
        page: int = 1
    ) -> NewsAPISearchResponse:
        """Search for news articles.
        
        Args:
            query: Keywords or phrases to search for
            sources: List of source identifiers to filter by
            domains: List of domains to filter by
            from_date: The oldest article to retrieve
            to_date: The newest article to retrieve
            language: The 2-letter ISO-639-1 code of the language to get articles in
            sort_by: The order to sort the articles in (relevancy, popularity, publishedAt)
            page_size: The number of results to return per page (1-100)
            page: The page number to return
            
        Returns:
            A NewsAPISearchResponse object containing the search results
        """
        params = {
            'q': query,
            'language': language,
            'sortBy': sort_by,
            'pageSize': min(max(1, page_size), 100),  # Clamp between 1 and 100
            'page': max(1, page)
        }
        
        if sources:
            params['sources'] = ','.join(sources)
        
        if domains:
            params['domains'] = ','.join(domains)
        
        if from_date:
            params['from'] = from_date.isoformat()
        
        if to_date:
            params['to'] = to_date.isoformat()
        
        data = await self._make_request('/everything', params)
        return NewsAPISearchResponse(**data)
    
    async def get_top_headlines(
        self,
        q: Optional[str] = None,
        sources: Optional[List[str]] = None,
        category: Optional[str] = None,
        country: Optional[str] = None,
        page_size: int = 10,
        page: int = 1
    ) -> NewsAPISearchResponse:
        """Get the top headlines.
        
        Args:
            q: Keywords or phrases to search for
            sources: List of source identifiers to filter by
            category: The category to get headlines for (business, entertainment, general, health, science, sports, technology)
            country: The 2-letter ISO 3166-1 code of the country to get headlines for
            page_size: The number of results to return per page (1-100)
            page: The page number to return
            
        Returns:
            A NewsAPISearchResponse object containing the top headlines
        """
        params = {
            'pageSize': min(max(1, page_size), 100),  # Clamp between 1 and 100
            'page': max(1, page)
        }
        
        if q:
            params['q'] = q
        
        if sources:
            params['sources'] = ','.join(sources)
        
        if category:
            params['category'] = category
        
        if country:
            params['country'] = country.lower()
        
        data = await self._make_request('/top-headlines', params)
        return NewsAPISearchResponse(**data)
    
    async def get_sources(
        self,
        category: Optional[str] = None,
        language: Optional[str] = None,
        country: Optional[str] = None
    ) -> NewsAPISourceResponse:
        """Get the list of available news sources.
        
        Args:
            category: The category to filter sources by (business, entertainment, general, health, science, sports, technology)
            language: The 2-letter ISO-639-1 code of the language to filter sources by
            country: The 2-letter ISO 3166-1 code of the country to filter sources by
            
        Returns:
            A NewsAPISourceResponse object containing the list of sources
        """
        params = {}
        
        if category:
            params['category'] = category
        
        if language:
            params['language'] = language
        
        if country:
            params['country'] = country.lower()
        
        data = await self._make_request('/top-headlines/sources', params)
        return NewsAPISourceResponse(**data)
    
    async def verify_source(self, domain: str) -> Optional[Dict[str, Any]]:
        """Verify if a domain is a known news source.
        
        Args:
            domain: The domain to verify (e.g., 'bbc.com')
            
        Returns:
            A dictionary with source information if found, None otherwise
        """
        try:
            # First, try to find the source by domain
            sources_response = await self.get_sources()
            
            # Normalize domain for comparison
            domain = domain.lower().strip()
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Check each source's URL
            for source in sources_response.sources:
                if source.url:
                    source_domain = urlparse(str(source.url)).netloc.lower()
                    if source_domain.startswith('www.'):
                        source_domain = source_domain[4:]
                    
                    if source_domain == domain:
                        return {
                            'id': source.id,
                            'name': source.name,
                            'description': source.description,
                            'url': str(source.url) if source.url else None,
                            'category': source.category,
                            'language': source.language,
                            'country': source.country,
                            'is_verified': True
                        }
            
            # If not found in sources, try searching for articles from this domain
            search_response = await self.search_articles(
                query="",
                domains=[domain],
                page_size=1
            )
            
            if search_response.articles:
                article = search_response.articles[0]
                return {
                    'id': None,
                    'name': article.source.get('name', domain),
                    'url': f"https://{domain}",
                    'is_verified': False,
                    'article_count': search_response.total_results
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error verifying source {domain}: {str(e)}", exc_info=True)
            return None
    
    async def find_related_articles(
        self,
        title: str,
        content: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Find articles related to the given content.
        
        Args:
            title: The title of the content
            content: The content to find related articles for
            max_results: Maximum number of related articles to return
            
        Returns:
            A list of related articles with their metadata
        """
        try:
            # Extract key terms from title and content
            search_terms = title.split()[:5]  # First 5 words of the title
            search_query = ' '.join(search_terms)
            
            # Search for related articles
            search_response = await self.search_articles(
                query=search_query,
                page_size=min(max_results, 10),  # Max 10 results
                sort_by='relevancy'
            )
            
            # Format the results
            related_articles = []
            for article in search_response.articles[:max_results]:
                related_articles.append({
                    'title': article.title,
                    'url': str(article.url),
                    'source': article.source.get('name', 'Unknown'),
                    'published_at': article.published_at.isoformat() if article.published_at else None,
                    'description': article.description,
                    'url_to_image': str(article.url_to_image) if article.url_to_image else None
                })
            
            return related_articles
            
        except Exception as e:
            logger.error(f"Error finding related articles: {str(e)}", exc_info=True)
            return []
