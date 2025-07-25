"""
Planner Component

This module contains the planner agent that determines the validation steps
for a given article based on its content and metadata.
"""

import logging
from typing import Dict, List, Optional, Any
from enum import Enum
import json

from pydantic import BaseModel, Field

from .base import BaseAgent, AgentContext, AgentMessage, PlannerError
from ..schemas.validation import ValidationType, ValidationRequest

logger = logging.getLogger(__name__)


class ValidationStep(BaseModel):
    """A single step in the validation plan."""
    step_id: str
    validation_type: ValidationType
    priority: int = 1
    dependencies: List[str] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    required: bool = True
    timeout: int = 30  # seconds


class ValidationPlan(BaseModel):
    """A complete validation plan for an article."""
    article_id: str
    steps: List[ValidationStep] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)


class Planner(BaseAgent[ValidationRequest]):
    """Planner agent that creates validation plans for articles."""
    
    def __init__(self, context: Optional[AgentContext] = None):
        super().__init__(context)
        self.plan: Optional[ValidationPlan] = None
    
    async def run(self, request: ValidationRequest) -> ValidationPlan:
        """
        Create a validation plan for the given request.
        
        Args:
            request: The validation request
            
        Returns:
            A validation plan
            
        Raises:
            PlannerError: If planning fails
        """
        try:
            self.context.update_state("planning")
            self.context.add_message(AgentMessage(
                content=f"Starting planning for article {request.article_id}",
                metadata={"request": request.model_dump()}
            ))
            
            # Create a new plan
            self.plan = ValidationPlan(article_id=str(request.article_id))
            
            # Add steps based on validation type
            if request.validation_type == ValidationType.FULL_ANALYSIS:
                await self._create_full_analysis_plan()
            elif request.validation_type == ValidationType.FACT_CHECK:
                await self._create_fact_check_plan()
            elif request.validation_type == ValidationType.SOURCE_VERIFICATION:
                await self._create_source_verification_plan()
            elif request.validation_type == ValidationType.BIAS_ANALYSIS:
                await self._create_bias_analysis_plan()
            else:
                raise PlannerError(f"Unknown validation type: {request.validation_type}")
            
            # Log the plan
            self.context.add_message(AgentMessage(
                content=f"Created validation plan with {len(self.plan.steps)} steps",
                metadata={"plan": self.plan.model_dump()}
            ))
            
            self.context.update_state("completed")
            return self.plan
            
        except Exception as e:
            self.context.update_state("failed")
            error_msg = f"Planning failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.context.add_message(AgentMessage(
                content=error_msg,
                metadata={"error": str(e), "traceback": str(e.__traceback__)}
            ))
            raise PlannerError(error_msg) from e
    
    async def _create_full_analysis_plan(self) -> None:
        """Create a plan for full analysis."""
        if not self.plan:
            raise PlannerError("Plan not initialized")
            
        self.plan.steps = [
            ValidationStep(
                step_id="source_verification",
                validation_type=ValidationType.SOURCE_VERIFICATION,
                priority=1,
                parameters={"depth": "thorough"}
            ),
            ValidationStep(
                step_id="fact_checking",
                validation_type=ValidationType.FACT_CHECK,
                priority=2,
                dependencies=["source_verification"],
                parameters={"model": "gemini-pro", "max_claims": 10}
            ),
            ValidationStep(
                step_id="bias_analysis",
                validation_type=ValidationType.BIAS_ANALYSIS,
                priority=2,
                dependencies=["source_verification"],
                parameters={"aspects": ["political", "corporate", "geopolitical"]}
            ),
            ValidationStep(
                step_id="consistency_check",
                validation_type=ValidationType.CONSISTENCY_CHECK,
                priority=3,
                dependencies=["fact_checking", "bias_analysis"],
                parameters={"threshold": 0.8}
            )
        ]
    
    async def _create_fact_check_plan(self) -> None:
        """Create a plan for fact-checking only."""
        if not self.plan:
            raise PlannerError("Plan not initialized")
            
        self.plan.steps = [
            ValidationStep(
                step_id="fact_checking",
                validation_type=ValidationType.FACT_CHECK,
                priority=1,
                parameters={"model": "gemini-pro", "max_claims": 15}
            )
        ]
    
    async def _create_source_verification_plan(self) -> None:
        """Create a plan for source verification only."""
        if not self.plan:
            raise PlannerError("Plan not initialized")
            
        self.plan.steps = [
            ValidationStep(
                step_id="source_verification",
                validation_type=ValidationType.SOURCE_VERIFICATION,
                priority=1,
                parameters={"depth": "standard"}
            )
        ]
    
    async def _create_bias_analysis_plan(self) -> None:
        """Create a plan for bias analysis only."""
        if not self.plan:
            raise PlannerError("Plan not initialized")
            
        self.plan.steps = [
            ValidationStep(
                step_id="bias_analysis",
                validation_type=ValidationType.BIAS_ANALYSIS,
                priority=1,
                parameters={"aspects": ["political", "corporate", "geopolitical"]}
            )
        ]
    
    def get_plan(self) -> Optional[ValidationPlan]:
        """Get the current plan."""
        return self.plan
