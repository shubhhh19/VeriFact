"""
Gemini API Service

This module provides integration with Google's Gemini API for fact-checking
and content analysis of articles.
"""

import logging
import os
from typing import Dict, List, Optional, Any, Union
import google.generativeai as genai
from pydantic import BaseModel, Field, HttpUrl
from ..config import settings

logger = logging.getLogger(__name__)

# Configure Gemini API
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
except Exception as e:
    logger.warning(f"Failed to configure Gemini API: {str(e)}")

class GeminiFactCheckResult(BaseModel):
    """Model for fact-checking results from Gemini."""
    claims: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of claims found in the text with their verification status"
    )
    summary: str = Field(
        default="",
        description="Summary of the fact-checking results"
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence in the fact-checking results"
    )

class GeminiBiasAnalysisResult(BaseModel):
    """Model for bias analysis results from Gemini."""
    bias_score: float = Field(
        ge=-1.0,
        le=1.0,
        description="Bias score from -1 (strongly biased against) to 1 (strongly biased in favor)"
    )
    bias_direction: str = Field(
        default="neutral",
        description="Direction of bias (e.g., 'left', 'right', 'neutral')"
    )
    reasoning: str = Field(
        default="",
        description="Explanation of the bias analysis"
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence in the bias analysis"
    )

class GeminiSourceAnalysisResult(BaseModel):
    """Model for source analysis results from Gemini."""
    source_credibility_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Credibility score of the source"
    )
    reliability_indicators: List[str] = Field(
        default_factory=list,
        description="List of indicators of source reliability"
    )
    potential_issues: List[str] = Field(
        default_factory=list,
        description="List of potential issues with the source"
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence in the source analysis"
    )

class GeminiService:
    """Service for interacting with Google's Gemini API."""
    
    def __init__(self, model_name: str = "gemini-1.5-pro"):
        """Initialize the Gemini service.
        
        Args:
            model_name: Name of the Gemini model to use
        """
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
    
    async def fact_check_article(
        self, 
        title: str, 
        content: str,
        context: Optional[str] = None
    ) -> GeminiFactCheckResult:
        """Fact-check the claims in an article.
        
        Args:
            title: Article title
            content: Article content
            context: Additional context for fact-checking
            
        Returns:
            Fact-checking results
        """
        prompt = f"""
        You are an expert fact-checker. Analyze the following article and identify any factual claims.
        For each claim, determine its veracity based on known facts and provide evidence.
        
        Article Title: {title}
        
        Article Content:
        {content}
        
        {f'Additional Context: {context}' if context else ''}
        
        Return your analysis in the following JSON format:
        {{
            "claims": [
                {{
                    "claim": "the exact claim text",
                    "verdict": "true/false/misleading/unverifiable",
                    "confidence": 0.0-1.0,
                    "explanation": "detailed explanation of the verdict",
                    "sources": ["list of sources that support or refute the claim"]
                }}
            ],
            "summary": "overall summary of the fact-checking results",
            "confidence": 0.0-1.0
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = response.text.strip()
            
            # Parse the response
            import json
            data = json.loads(result)
            
            return GeminiFactCheckResult(**data)
            
        except Exception as e:
            logger.error(f"Error in Gemini fact-checking: {str(e)}", exc_info=True)
            raise
    
    async def analyze_bias(
        self, 
        title: str, 
        content: str
    ) -> GeminiBiasAnalysisResult:
        """Analyze the bias in an article.
        
        Args:
            title: Article title
            content: Article content
            
        Returns:
            Bias analysis results
        """
        prompt = f"""
        Analyze the following article for potential bias. Consider the language used, 
        framing of issues, source selection, and any other indicators of bias.
        
        Article Title: {title}
        
        Article Content:
        {content}
        
        Return your analysis in the following JSON format:
        {{
            "bias_score": -1.0 to 1.0 (negative = biased against, positive = biased in favor, 0 = neutral),
            "bias_direction": "left/right/neutral/other",
            "reasoning": "detailed explanation of the bias analysis",
            "confidence": 0.0-1.0
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = response.text.strip()
            
            # Parse the response
            import json
            data = json.loads(result)
            
            return GeminiBiasAnalysisResult(**data)
            
        except Exception as e:
            logger.error(f"Error in Gemini bias analysis: {str(e)}", exc_info=True)
            raise
    
    async def analyze_sources(
        self,
        article_url: Optional[str] = None,
        source_name: Optional[str] = None,
        content: Optional[str] = None
    ) -> GeminiSourceAnalysisResult:
        """Analyze the credibility of an article's sources.
        
        Args:
            article_url: URL of the article (if available)
            source_name: Name of the source/publication
            content: Article content (for source extraction if URL not available)
            
        Returns:
            Source analysis results
        """
        prompt = """
        Analyze the credibility of the following source or article. Consider factors like:
        - Reputation of the publication
        - Editorial standards
        - History of accuracy
        - Transparency about sources and methods
        - Any known biases or conflicts of interest
        
        """
        
        if article_url:
            prompt += f"Article URL: {article_url}\n\n"
        if source_name:
            prompt += f"Source/Publication: {source_name}\n\n"
        if content:
            prompt += f"Article Content (for context):\n{content}\n\n"
            
        prompt += """
        Return your analysis in the following JSON format:
        {
            "source_credibility_score": 0.0-1.0,
            "reliability_indicators": ["list of positive indicators of reliability"],
            "potential_issues": ["list of any potential issues or concerns"],
            "confidence": 0.0-1.0
        }
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = response.text.strip()
            
            # Parse the response
            import json
            data = json.loads(result)
            
            return GeminiSourceAnalysisResult(**data)
            
        except Exception as e:
            logger.error(f"Error in Gemini source analysis: {str(e)}", exc_info=True)
            raise
    
    async def generate_summary(
        self,
        title: str,
        content: str,
        max_length: int = 250
    ) -> str:
        """Generate a concise summary of an article.
        
        Args:
            title: Article title
            content: Article content
            max_length: Maximum length of the summary in characters
            
        Returns:
            Generated summary
        """
        prompt = f"""
        Generate a concise, factual summary of the following article in {max_length} characters or less.
        Focus on the main points and key information.
        
        Article Title: {title}
        
        Article Content:
        {content}
        
        Summary:
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating summary with Gemini: {str(e)}", exc_info=True)
            raise
