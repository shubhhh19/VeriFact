"""
Validation Tasks

This module contains background tasks for processing article validations.
In a production environment, these would be processed by a task queue like Celery.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.models.validation_result import ValidationResult as ValidationResultModel
from src.schemas.validation import ValidationResultUpdate, ValidationStatus, ValidationType
from src.services.article import ArticleService
from src.services.validation import ValidationService

logger = logging.getLogger(__name__)


async def process_validation(validation_id: UUID, db: AsyncSession) -> None:
    """
    Process a validation request asynchronously.
    
    This function simulates the validation process by:
    1. Marking the validation as in progress
    2. Performing the validation (simulated with sleep)
    3. Updating the validation result
    """
    validation_service = await ValidationService.get_service(db)
    
    try:
        # Mark validation as in progress
        await validation_service.update_validation(
            validation_id,
            ValidationResultUpdate(status=ValidationStatus.IN_PROGRESS)
        )
        
        # Get the validation details
        validation = await validation_service.get_validation(validation_id)
        if not validation:
            logger.error(f"Validation {validation_id} not found")
            return
            
        # Get the article details
        article_service = await ArticleService.get_service(db)
        article = await article_service.get_article(validation.article_id)
        if not article:
            await validation_service.update_validation(
                validation_id,
                ValidationResultUpdate(
                    status=ValidationStatus.FAILED,
                    error=f"Article {validation.article_id} not found"
                )
            )
            return
        
        # Simulate processing time based on validation type
        processing_time = 5.0  # Default 5 seconds
        if validation.validation_type == ValidationType.FULL_ANALYSIS:
            processing_time = 10.0
        elif validation.validation_type == ValidationType.FACT_CHECK:
            processing_time = 7.0
            
        logger.info(f"Processing validation {validation_id} for article {article.id}...")
        
        # Simulate processing
        await asyncio.sleep(processing_time)
        
        # Generate mock validation result
        result = await _generate_mock_validation_result(validation, article)
        
        # Update the validation result
        await validation_service.update_validation(
            validation_id,
            ValidationResultUpdate(
                status=ValidationStatus.COMPLETED,
                summary=result["summary"],
                overall_confidence=result["overall_confidence"],
                is_credible=result["is_credible"],
                raw_response=result,
            )
        )
        
        logger.info(f"Completed validation {validation_id} for article {article.id}")
        
    except Exception as e:
        logger.error(f"Error processing validation {validation_id}: {str(e)}", exc_info=True)
        try:
            await validation_service.update_validation(
                validation_id,
                ValidationResultUpdate(
                    status=ValidationStatus.FAILED,
                    error=f"Validation failed: {str(e)}"
                )
            )
        except Exception as update_error:
            logger.error(f"Failed to update validation status: {str(update_error)}")


async def _generate_mock_validation_result(
    validation: Any,
    article: Any
) -> Dict[str, Any]:
    """
    Generate a mock validation result for demonstration purposes.
    In a real implementation, this would call the actual validation services.
    """
    import random
    from faker import Faker
    
    fake = Faker()
    
    # Generate mock claims from article content
    claims = []
    if article.content:
        # Simple mock: split content into sentences and treat each as a claim
        sentences = [s.strip() for s in article.content.split('.') if s.strip()]
        claims = sentences[:3]  # Take up to 3 sentences as claims
    
    if not claims:
        claims = [
            "This is a sample claim about the article.",
            "The article makes several assertions that need verification.",
            "The source of the information is not clearly stated."
        ]
    
    # Generate mock analysis for each claim
    claims_analysis = []
    for i, claim in enumerate(claims):
        is_supported = random.random() > 0.3  # 70% chance of being supported
        confidence = round(random.uniform(0.5, 1.0), 2)
        
        # Generate mock evidence
        supporting_evidence = []
        contradicting_evidence = []
        
        if is_supported:
            supporting_evidence = [
                {
                    "url": f"https://trustedsource.org/evidence/{fake.uuid4()}",
                    "title": f"Supporting evidence for claim {i+1}",
                    "publisher": "Trusted Source",
                    "reliability_score": round(random.uniform(0.7, 1.0), 2)
                }
                for _ in range(random.randint(1, 3))
            ]
        else:
            contradicting_evidence = [
                {
                    "url": f"https://factcheck.org/evidence/{fake.uuid4()}",
                    "title": f"Contradicting evidence for claim {i+1}",
                    "publisher": "FactCheck.org",
                    "reliability_score": round(random.uniform(0.7, 1.0), 2)
                }
                for _ in range(random.randint(1, 2))
            ]
        
        claims_analysis.append({
            "claim": claim,
            "is_supported": is_supported,
            "confidence": confidence,
            "explanation": fake.paragraph(),
            "supporting_evidence": supporting_evidence,
            "contradicting_evidence": contradicting_evidence
        })
    
    # Calculate overall confidence and credibility
    if claims_analysis:
        overall_confidence = round(
            sum(c["confidence"] for c in claims_analysis) / len(claims_analysis),
            2
        )
        is_credible = overall_confidence > 0.7 and all(
            c["is_supported"] for c in claims_analysis if "is_supported" in c
        )
    else:
        overall_confidence = 0.0
        is_credible = False
    
    return {
        "validation_id": str(validation.id),
        "article_id": str(validation.article_id),
        "validation_type": validation.validation_type,
        "status": "completed",
        "summary": fake.paragraph(),
        "overall_confidence": overall_confidence,
        "is_credible": is_credible,
        "claims_analysis": claims_analysis,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "model_used": "mock-model-v1.0"
    }
