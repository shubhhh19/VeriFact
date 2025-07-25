"""
Validation Schemas

This module contains Pydantic models for validation-related requests and responses.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Union
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class ValidationStatus(str, Enum):
    """Status of a validation operation"""
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
    COMPREHENSIVE = "comprehensive"
    BIAS_ANALYSIS = "bias_analysis"
    FULL_ANALYSIS = "full_analysis"


class EvidenceSource(BaseModel):
    """Model for evidence source"""
    url: Optional[HttpUrl] = None
    title: Optional[str] = None
    publisher: Optional[str] = None
    published_date: Optional[datetime] = None
    reliability_score: Optional[float] = Field(None, ge=0, le=1)


class ClaimAnalysis(BaseModel):
    """Model for claim analysis"""
    claim: str
    is_supported: Optional[bool] = None
    confidence: float = Field(..., ge=0, le=1)
    explanation: str
    supporting_evidence: List[EvidenceSource] = []
    contradicting_evidence: List[EvidenceSource] = []


class ValidationRequest(BaseModel):
    """Schema for validation request"""
    article_url: Optional[HttpUrl] = Field(None, description="URL of the article to validate")
    article_content: Optional[str] = Field(None, description="Direct content of the article")
    title: Optional[str] = Field(None, description="Article title")
    validation_types: List[ValidationType] = Field(
        default=[ValidationType.COMPREHENSIVE],
        description="Types of validation to perform"
    )
    include_sources: bool = Field(default=True, description="Include source verification")
    include_contradictions: bool = Field(default=True, description="Include contradiction detection")


class Claim(BaseModel):
    """Schema for a claim extracted from an article"""
    text: str = Field(..., description="The claim text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    category: Optional[str] = Field(None, description="Category of the claim")
    type: Optional[str] = Field(None, description="Type of claim")


class Source(BaseModel):
    """Schema for a verified source"""
    name: str = Field(..., description="Source name")
    url: Optional[HttpUrl] = Field(None, description="Source URL")
    reliability_score: float = Field(..., ge=0.0, le=1.0, description="Reliability score")
    supports_claim: Optional[bool] = Field(None, description="Whether source supports the claim")
    title: Optional[str] = Field(None, description="Source article title")
    published_at: Optional[str] = Field(None, description="Publication date")
    relevance_score: Optional[float] = Field(None, description="Relevance to the claim")


class Contradiction(BaseModel):
    """Schema for a contradiction found"""
    claim: str = Field(..., description="The claim that has contradictions")
    contradicting_sources: List[str] = Field(..., description="Sources that contradict the claim")
    severity: str = Field(..., description="Severity of the contradiction")
    explanation: Optional[str] = Field(None, description="Explanation of the contradiction")


class ValidationResult(BaseModel):
    """Schema for validation result"""
    id: UUID
    article_id: UUID
    validation_type: ValidationType
    status: ValidationStatus
    score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Overall credibility score")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence in the validation")
    is_valid: Optional[bool] = Field(None, description="Whether the article is considered valid")
    
    # Detailed results
    claims: List[Claim] = Field(default_factory=list, description="Extracted claims")
    sources: List[Source] = Field(default_factory=list, description="Verified sources")
    contradictions: List[Contradiction] = Field(default_factory=list, description="Found contradictions")
    
    # Metadata
    started_at: Optional[datetime] = Field(None, description="When validation started")
    completed_at: Optional[datetime] = Field(None, description="When validation completed")
    error: Optional[str] = Field(None, description="Error message if validation failed")
    
    # Additional details
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional validation details")

    class Config:
        from_attributes = True


class ValidationResponse(BaseModel):
    """Schema for validation response"""
    success: bool = Field(..., description="Whether the operation was successful")
    validation_id: Optional[str] = Field(None, description="ID of the validation operation")
    status: Optional[ValidationStatus] = Field(None, description="Current status of validation")
    results: Optional[ValidationResult] = Field(None, description="Validation results")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message if operation failed")


class ValidationResultList(BaseModel):
    """Schema for listing validation results"""
    items: List[ValidationResult]
    total: int
    page: int
    size: int
    pages: int
