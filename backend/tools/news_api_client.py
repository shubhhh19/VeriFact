"""
News Validator Agent - NewsAPI Client
Handles integration with NewsAPI for fetching news articles and sources
"""

import os
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


class NewsAPIClient:
    """
    Client for interacting with NewsAPI to fetch news articles
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize NewsAPI client
        
        Args:
            api_key: NewsAPI key (if None, reads from environment)
        """
        self.api_key = api_key or os.getenv('NEWS_API_KEY')
        if not self.api_key:
            raise ValueError("NewsAPI key is required. Set NEWS_API_KEY environment variable.")
        
        self.base_url = "https://newsapi.org/v2"
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def search_articles(self, query: str, sources: List[str] = None, 
                            language: str = "en", page_size: int = 20) -> List[Dict[str, Any]]:
        """
        Search for news articles by query
        
        Args:
            query: Search query
            sources: Optional list of specific sources to search
            language: Language code (default: en)
            page_size: Number of articles to return (max 100)
            
        Returns:
            List of news articles with metadata
        """
        params = {
            "q": query,
            "language": language,
            "pageSize": min(page_size, 100),
            "apiKey": self.api_key
        }
        
        if sources:
            params["sources"] = ",".join(sources)
        
        # TODO: Implement actual NewsAPI call
        # async with self.session.get(f"{self.base_url}/everything", params=params) as response:
        #     if response.status == 200:
        #         data = await response.json()
        #         return data.get("articles", [])
        #     else:
        #         raise Exception(f"NewsAPI error: {response.status}")
        
        # Placeholder response
        return [
            {
                "title": "Sample News Article",
                "description": "Sample description of news article",
                "content": "Sample content of the news article...",
                "url": "https://example.com/article",
                "source": {"name": "Sample Source"},
                "publishedAt": datetime.utcnow().isoformat(),
                "author": "Sample Author"
            }
        ]
    
    async def get_top_headlines(self, category: str = None, country: str = "us",
                              sources: List[str] = None, page_size: int = 20) -> List[Dict[str, Any]]:
        """
        Get top headlines
        
        Args:
            category: News category (business, entertainment, general, health, science, sports, technology)
            country: Country code (default: us)
            sources: Optional list of specific sources
            page_size: Number of articles to return (max 100)
            
        Returns:
            List of top headline articles
        """
        params = {
            "country": country,
            "pageSize": min(page_size, 100),
            "apiKey": self.api_key
        }
        
        if category:
            params["category"] = category
        
        if sources:
            params["sources"] = ",".join(sources)
            # Remove country when using sources (NewsAPI restriction)
            del params["country"]
        
        # TODO: Implement actual NewsAPI call
        # async with self.session.get(f"{self.base_url}/top-headlines", params=params) as response:
        #     if response.status == 200:
        #         data = await response.json()
        #         return data.get("articles", [])
        #     else:
        #         raise Exception(f"NewsAPI error: {response.status}")
        
        # Placeholder response
        return [
            {
                "title": "Sample Top Headline",
                "description": "Sample description of top headline",
                "content": "Sample content of the top headline...",
                "url": "https://example.com/headline",
                "source": {"name": "Sample News Source"},
                "publishedAt": datetime.utcnow().isoformat(),
                "author": "Sample Author"
            }
        ]
    
    async def get_sources(self, category: str = None, language: str = "en", 
                         country: str = "us") -> List[Dict[str, Any]]:
        """
        Get available news sources
        
        Args:
            category: Filter by category
            language: Filter by language (default: en)
            country: Filter by country (default: us)
            
        Returns:
            List of available news sources
        """
        params = {
            "language": language,
            "country": country,
            "apiKey": self.api_key
        }
        
        if category:
            params["category"] = category
        
        # TODO: Implement actual NewsAPI call
        # async with self.session.get(f"{self.base_url}/sources", params=params) as response:
        #     if response.status == 200:
        #         data = await response.json()
        #         return data.get("sources", [])
        #     else:
        #         raise Exception(f"NewsAPI error: {response.status}")
        
        # Placeholder response
        return [
            {
                "id": "sample-source",
                "name": "Sample News Source",
                "description": "A sample news source for testing",
                "url": "https://example.com",
                "category": "general",
                "language": "en",
                "country": "us"
            }
        ]
    
    def extract_article_text(self, article: Dict[str, Any]) -> str:
        """
        Extract clean text from article for analysis
        
        Args:
            article: Article dictionary from NewsAPI
            
        Returns:
            Clean text content
        """
        text_parts = []
        
        if article.get("title"):
            text_parts.append(article["title"])
        
        if article.get("description"):
            text_parts.append(article["description"])
        
        if article.get("content"):
            # Remove common NewsAPI content truncation markers
            content = article["content"]
            if "[+" in content:
                content = content.split("[+")[0]
            text_parts.append(content)
        
        return " ".join(text_parts)
