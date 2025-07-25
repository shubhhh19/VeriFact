"""
Validation Schemas

This module contains Pydantic models for validation requests and responses.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class ValidationStatus(str, Enum):
    """Enum for validation status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ValidationType(str, Enum):
    """Enum for validation types"""
    FACT_CHECK = "fact_check"
    SOURCE_VERIFICATION = "source_verification"
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
    article_id: UUID
    validation_type: ValidationType = ValidationType.FULL_ANALYSIS
    priority: int = Field(1, ge=1, le=5, description="Priority from 1 (lowest) to 5 (highest)")
    metadata: Optional[Dict[str, str]] = None


class ValidationResultBase(BaseModel):
    """Base schema for validation result"""
    status: ValidationStatus
    validation_type: ValidationType
    summary: Optional[str] = None
    overall_confidence: Optional[float] = Field(None, ge=0, le=1)
    is_credible: Optional[bool] = None
    error: Optional[str] = None


class ValidationResultCreate(ValidationResultBase):
    """Schema for creating a validation result"""
    article_id: UUID
    raw_response: Optional[Dict[str, Union[str, float, bool, list, dict]]] = None


class ValidationResultUpdate(BaseModel):
    """Schema for updating a validation result"""
    status: Optional[ValidationStatus] = None
    summary: Optional[str] = None
    overall_confidence: Optional[float] = Field(None, ge=0, le=1)
    is_credible: Optional[bool] = None
    error: Optional[str] = None
    raw_response: Optional[Dict[str, Union[str, float, bool, list, dict]]] = None


class ValidationResult(ValidationResultBase):
    """Schema for validation result response"""
    id: UUID
    article_id: UUID
    claims_analysis: List[ClaimAnalysis] = []
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ValidationResultList(BaseModel):
    """Schema for listing validation results"""
    items: List[ValidationResult]
    total: int
    page: int
    size: int
    pages: int
