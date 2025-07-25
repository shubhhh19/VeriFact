"""
Agent Orchestrator

This module contains the main orchestrator that coordinates between
planner, executor, and memory components to validate articles.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Type, TypeVar, Generic, cast
from uuid import UUID, uuid4

from pydantic import BaseModel

from .base import BaseAgent, AgentContext, AgentError
from .planner import Planner, ValidationPlan, ValidationStep
from .executor import Executor, ExecutionResult
from .memory import Memory, MemoryKey
from ..schemas.validation import ValidationRequest, ValidationResult, ValidationStatus
from ..services.article import ArticleService
from ..services.validation import ValidationService

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class ValidationOrchestrator(BaseAgent[ValidationRequest]):
    """
    Orchestrates the validation process by coordinating between planner, executor, and memory.
    
    This is the main entry point for the validation system. It handles the complete
    lifecycle of a validation request from creation to completion.
    """
    
    def __init__(
        self,
        db: Any,
        memory: Optional[Memory] = None,
        planner: Optional[Planner] = None,
        executor: Optional[Executor] = None,
        context: Optional[AgentContext] = None
    ):
        """
        Initialize the orchestrator with its dependencies.
        
        Args:
            db: Database session or connection
            memory: Optional memory component (will be created if not provided)
            planner: Optional planner component (will be created if not provided)
            executor: Optional executor component (will be created if not provided)
            context: Optional agent context (will be created if not provided)
        """
        super().__init__(context or AgentContext())
        self.db = db
        self.memory = memory or Memory(context=self.context)
        self.planner = planner or Planner(context=self.context)
        self.executor = executor or Executor(db, context=self.context)
        self.article_service: Optional[ArticleService] = None
        self.validation_service: Optional[ValidationService] = None
    
    async def run(self, request: ValidationRequest) -> ValidationResult:
        """
        Execute the validation process for the given request.
        
        This is the main entry point for starting a validation. It handles the complete
        validation lifecycle including planning, execution, and result storage.
        
        Args:
            request: The validation request to process
            
        Returns:
            The validation result
            
        Raises:
            AgentError: If the validation process fails
        """
        try:
            # Initialize services
            self.article_service = await ArticleService.get_service(self.db)
            self.validation_service = await ValidationService.get_service(self.db)
            
            # Create initial validation result
            validation = await self._create_validation_result(request)
            
            # Create and store execution plan
            plan = await self.planner.run(request)
            execution_id = str(uuid4())
            
            await self.memory.store_execution_plan(
                execution_id=execution_id,
                plan=plan,
                expire=timedelta(days=1)
            )
            
            # Execute the plan
            execution_result = await self.executor.run(plan)
            
            # Store the execution result
            await self.memory.store_execution_result(
                execution_id=execution_id,
                result=execution_result,
                expire=timedelta(days=7)
            )
            
            # Update the validation result
            validation = await self._update_validation_result(
                validation_id=validation.id,
                execution_result=execution_result
            )
            
            return validation
            
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}", exc_info=True)
            
            # Update validation status to failed
            if 'validation' in locals():
                try:
                    await self._update_validation_result(
                        validation_id=validation.id,
                        status=ValidationStatus.FAILED,
                        error=str(e)
                    )
                except Exception as update_error:
                    logger.error(
                        f"Failed to update validation status: {str(update_error)}",
                        exc_info=True
                    )
            
            raise AgentError(f"Validation failed: {str(e)}") from e
    
    async def _create_validation_result(
        self, 
        request: ValidationRequest
    ) -> ValidationResult:
        """
        Create a new validation result in the database.
        
        Args:
            request: The validation request
            
        Returns:
            The created validation result
        """
        if not self.validation_service:
            raise AgentError("Validation service not initialized")
            
        # Create the validation result
        validation = await self.validation_service.create_validation(request)
        
        # Store in memory
        await self.memory.store_validation_result(validation)
        
        return validation
    
    async def _update_validation_result(
        self,
        validation_id: UUID,
        execution_result: Optional[ExecutionResult] = None,
        status: Optional[ValidationStatus] = None,
        error: Optional[str] = None
    ) -> ValidationResult:
        """
        Update a validation result in the database and memory.
        
        Args:
            validation_id: The ID of the validation to update
            execution_result: Optional execution result to include
            status: Optional status to set
            error: Optional error message
            
        Returns:
            The updated validation result
        """
        if not self.validation_service:
            raise AgentError("Validation service not initialized")
        
        # Prepare update data
        update_data = {}
        
        if execution_result:
            update_data.update({
                'status': ValidationStatus.COMPLETED 
                    if execution_result.status == 'completed' 
                    else ValidationStatus.FAILED,
                'summary': self._generate_summary(execution_result),
                'overall_confidence': self._calculate_confidence(execution_result),
                'is_credible': self._is_credible(execution_result),
                'raw_response': {
                    'execution_id': execution_result.execution_id,
                    'steps': [
                        {
                            'step_id': step.step_id,
                            'success': step.success,
                            'duration': step.duration,
                            'error': step.error,
                            'metadata': step.metadata
                        }
                        for step in execution_result.steps
                    ],
                    'results': execution_result.results
                }
            })
        
        if status:
            update_data['status'] = status
            
        if error:
            update_data['error'] = error
        
        # Update in database
        validation = await self.validation_service.update_validation(
            validation_id=validation_id,
            update_data=update_data
        )
        
        # Update in memory
        await self.memory.store_validation_result(validation)
        
        return validation
    
    def _generate_summary(self, execution_result: ExecutionResult) -> str:
        """
        Generate a human-readable summary of the validation results.
        
        Args:
            execution_result: The execution result to summarize
            
        Returns:
            A summary string
        """
        if not execution_result.steps:
            return "No validation steps were executed."
            
        # Count successful and failed steps
        successful_steps = sum(1 for step in execution_result.steps if step.success)
        total_steps = len(execution_result.steps)
        
        # Get overall confidence
        confidence = self._calculate_confidence(execution_result)
        
        # Generate summary
        summary = [
            f"Validation completed with {successful_steps} of {total_steps} steps successful.",
            f"Overall confidence: {confidence:.1%}"
        ]
        
        # Add step-specific details
        for step in execution_result.steps:
            if step.success and step.result:
                step_summary = self._summarize_step(step)
                if step_summary:
                    summary.append(f"- {step_summary}")
        
        return "\n".join(summary)
    
    def _summarize_step(self, step: Any) -> str:
        """
        Generate a summary for a single execution step.
        
        Args:
            step: The step to summarize
            
        Returns:
            A summary string for the step
        """
        if not step.success or not step.result:
            return ""
            
        step_type = step.metadata.get('validation_type', 'unknown')
        
        if step_type == 'fact_check':
            return (
                f"Fact-checking: {step.result.get('claims_supported', 0)} claims supported, "
                f"{step.result.get('claims_contradicted', 0)} contradicted"
            )
        elif step_type == 'source_verification':
            return (
                f"Source verification: {step.result.get('reliable_sources', 0)} reliable sources, "
                f"{step.result.get('questionable_sources', 0)} questionable sources"
            )
        elif step_type == 'bias_analysis':
            return (
                f"Bias analysis: Overall bias score {step.result.get('bias_score', 0):.1f} "
                f"({step.result.get('bias_direction', 'unknown')})"
            )
        
        return f"{step_type.replace('_', ' ').title()} completed successfully"
    
    def _calculate_confidence(self, execution_result: ExecutionResult) -> float:
        """
        Calculate an overall confidence score from the execution results.
        
        Args:
            execution_result: The execution result to analyze
            
        Returns:
            A confidence score between 0 and 1
        """
        if not execution_result.steps:
            return 0.0
            
        # Calculate average confidence from all steps
        total_confidence = 0.0
        num_steps = 0
        
        for step in execution_result.steps:
            if step.success and step.result:
                # Different step types might report confidence differently
                if 'confidence' in step.result:
                    total_confidence += float(step.result['confidence'])
                    num_steps += 1
                elif 'source_credibility_score' in step.result:
                    total_confidence += float(step.result['source_credibility_score'])
                    num_steps += 1
                elif 'bias_score' in step.result:
                    # Invert bias score since higher bias is worse
                    total_confidence += 1.0 - abs(0.5 - float(step.result['bias_score']))
                    num_steps += 1
        
        # If no steps reported confidence, use success rate
        if num_steps == 0:
            successful_steps = sum(1 for step in execution_result.steps if step.success)
            return successful_steps / len(execution_result.steps) if execution_result.steps else 0.0
        
        return total_confidence / num_steps
    
    def _is_credible(self, execution_result: ExecutionResult) -> bool:
        """
        Determine if the article is credible based on the validation results.
        
        Args:
            execution_result: The execution result to analyze
            
        Returns:
            True if the article is considered credible, False otherwise
        """
        if not execution_result.steps:
            return False
            
        # Check if any critical steps failed
        for step in execution_result.steps:
            if step.metadata.get('required', True) and not step.success:
                return False
        
        # Calculate overall confidence
        confidence = self._calculate_confidence(execution_result)
        
        # Consider the article credible if confidence is above threshold
        return confidence >= 0.7  # 70% confidence threshold
    
    async def close(self) -> None:
        """Clean up resources."""
        try:
            await self.memory.close()
        except Exception as e:
            logger.error(f"Error closing memory: {str(e)}", exc_info=True)
            
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        
    @classmethod
    async def create(
        cls, 
        db: Any, 
        context: Optional[AgentContext] = None
    ) -> 'ValidationOrchestrator':
        """
        Create a new orchestrator with default components.
        
        Args:
            db: Database session or connection
            context: Optional agent context
            
        Returns:
            A new ValidationOrchestrator instance
        """
        memory = Memory(context=context)
        planner = Planner(context=context)
        executor = Executor(db, context=context)
        
        return cls(
            db=db,
            memory=memory,
            planner=planner,
            executor=executor,
            context=context
        )
