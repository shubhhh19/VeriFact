"""
Base Agent Components

This module contains the base classes for the VeriFact agent architecture.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic
from pydantic import BaseModel, Field
from enum import Enum


class AgentState(str, Enum):
    """Possible states of an agent."""
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentMessage(BaseModel):
    """Base class for messages between agent components."""
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())


class AgentContext(BaseModel):
    """Context for agent execution."""
    state: AgentState = AgentState.IDLE
    messages: List[AgentMessage] = Field(default_factory=list)
    data: Dict[str, Any] = Field(default_factory=dict)
    
    def add_message(self, message: AgentMessage) -> None:
        """Add a message to the context."""
        self.messages.append(message)
    
    def update_state(self, state: AgentState) -> None:
        """Update the agent state."""
        self.state = state
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """Get data from context."""
        return self.data.get(key, default)
    
    def set_data(self, key: str, value: Any) -> None:
        """Set data in context."""
        self.data[key] = value


T = TypeVar('T')


class BaseAgent(ABC, Generic[T]):
    """Base class for all agents."""
    
    def __init__(self, context: Optional[AgentContext] = None):
        self.context = context or AgentContext()
    
    @abstractmethod
    async def run(self, input_data: T) -> Any:
        """Execute the agent's main logic."""
        pass
    
    async def __call__(self, input_data: T) -> Any:
        """Make the agent callable."""
        return await self.run(input_data)


class AgentError(Exception):
    """Base exception for agent-related errors."""
    pass


class PlannerError(AgentError):
    """Exception raised for errors in the planner."""
    pass


class ExecutorError(AgentError):
    """Exception raised for errors in the executor."""
    pass


class MemoryError(AgentError):
    """Exception raised for errors in the memory system."""
    pass
