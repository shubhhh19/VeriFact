"""
Executor Component

This module contains the executor agent that runs validation steps
according to the plan created by the planner.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from .base import BaseAgent
from .context import AgentContext
from .messages import AgentMessage
from .planner import ValidationPlan, ValidationStep, ValidationStatus

logger = logging.getLogger(__name__)


class StepResult(BaseModel):
    """Result of executing a single validation step."""
    step_id: str
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExecutionResult(BaseModel):
    """Result of executing a validation plan."""
    execution_id: str = Field(default_factory=lambda: str(uuid4()))
    plan_id: str
    article_id: str
    status: ValidationStatus = ValidationStatus.PENDING
    steps: List[StepResult] = Field(default_factory=list)
    results: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    start_time: float = Field(default_factory=lambda: asyncio.get_event_loop().time())
    end_time: Optional[float] = None

    def add_step_result(self, result: StepResult) -> None:
        """Add a step result to the execution."""
        self.steps.append(result)

    def finalize(self) -> None:
        """Mark the execution as completed."""
        self.end_time = asyncio.get_event_loop().time()
        self.status = ValidationStatus.COMPLETED


class Executor(BaseAgent):
    """Executor agent that runs validation steps according to a plan."""
    
    def __init__(
        self, 
        db: Any,
        context: Optional[AgentContext] = None
    ):
        super().__init__(context)
        self.db = db
        self.execution_result: Optional[ExecutionResult] = None
        self.article_service: Optional[Any] = None
        self.validation_service: Optional[Any] = None
    
    async def run(self, plan: ValidationPlan) -> ExecutionResult:
        """
        Execute the given validation plan.
        
        Args:
            plan: The validation plan to execute
            
        Returns:
            Execution result with step outcomes
            
        Raises:
            Exception: If execution fails
        """
        try:
            self.context.update_state("executing")
            self.context.add_message(AgentMessage(
                content=f"Starting execution of validation plan for article {plan.article_id}",
                metadata={"plan_id": str(id(plan))}
            ))
            
            # Initialize execution result
            self.execution_result = ExecutionResult(
                plan_id=plan.plan_id,
                article_id=plan.article_id,
                status=ValidationStatus.IN_PROGRESS
            )
            
            # Execute each step in the plan
            for step in plan.steps:
                step_result = await self._execute_step(step, plan.article)
                self.execution_result.add_step_result(step_result)
                
                # If any step fails, mark the whole execution as failed
                if not step_result.success:
                    self.execution_result.status = ValidationStatus.FAILED
                    self.execution_result.error = step_result.error
                    break
            
            # Finalize the execution
            self.execution_result.finalize()
            return self.execution_result
            
        except Exception as e:
            error_msg = f"Failed to execute validation plan: {str(e)}"
            logger.error(error_msg, exc_info=True)
            if self.execution_result:
                self.execution_result.status = ValidationStatus.FAILED
                self.execution_result.error = error_msg
                self.execution_result.finalize()
            raise Exception(error_msg) from e
    
    async def _execute_step(
        self, 
        step: ValidationStep, 
        article: Any
    ) -> StepResult:
        """Execute a single validation step."""
        start_time = asyncio.get_event_loop().time()
        step_result = StepResult(step_id=step.step_id, success=False)
        
        try:
            # Execute the appropriate step handler
            if step.step_type == "fact_check":
                result = await self._execute_fact_check(step, article)
            elif step.step_type == "source_verification":
                result = await self._execute_source_verification(step, article)
            elif step.step_type == "bias_analysis":
                result = await self._execute_bias_analysis(step, article)
            elif step.step_type == "consistency_check":
                result = await self._execute_consistency_check(step)
            else:
                raise ValueError(f"Unknown step type: {step.step_type}")
            
            # Update step result
            step_result.success = True
            step_result.result = result
            
        except Exception as e:
            error_msg = f"Step {step.step_id} failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            step_result.error = error_msg
            step_result.success = False
        
        # Calculate duration
        step_result.duration = asyncio.get_event_loop().time() - start_time
        
        # Log the step result
        status = "success" if step_result.success else "failure"
        self.context.add_message(AgentMessage(
            content=f"Completed step {step.step_id} with status {status}",
            metadata={
                "step_id": step.step_id,
                "success": step_result.success,
                "duration": step_result.duration
            }
        ))
        
        return step_result
    
    async def _execute_fact_check(
        self, 
        step: ValidationStep, 
        article: Any
    ) -> Dict[str, Any]:
        """Execute fact-checking for the article."""
        # Implementation here
        return {"status": "completed", "details": {}}
    
    async def _execute_source_verification(
        self, 
        step: ValidationStep, 
        article: Any
    ) -> Dict[str, Any]:
        """Verify the sources cited in the article."""
        # Implementation here
        return {"status": "completed", "details": {}}
    
    async def _execute_bias_analysis(
        self, 
        step: ValidationStep, 
        article: Any
    ) -> Dict[str, Any]:
        """Analyze the article for bias."""
        # Implementation here
        return {"status": "completed", "details": {}}
    
    async def _execute_consistency_check(
        self, 
        step: ValidationStep
    ) -> Dict[str, Any]:
        """Check the consistency of the validation results."""
        # Implementation here
        return {"status": "completed", "details": {}}
