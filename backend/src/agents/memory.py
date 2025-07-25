"""
Memory Component

This module provides a memory system for the VeriFact agent architecture,
handling storage and retrieval of validation data, article information, and agent states.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Type, TypeVar
from uuid import UUID, uuid4

import redis.asyncio as redis
from pydantic import BaseModel, Field

from .base import BaseAgent, AgentContext, AgentMessage, MemoryError
from ..config import settings

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

class MemoryKey:
    """Helper class for generating Redis keys."""
    
    @staticmethod
    def validation_result(validation_id: Union[str, UUID]) -> str:
        """Key for storing validation results."""
        return f"validation:result:{validation_id}"
    
    @staticmethod
    def article_validations(article_id: Union[str, UUID]) -> str:
        """Key for storing list of validation IDs for an article."""
        return f"article:validations:{article_id}"
    
    @staticmethod
    def agent_state(agent_id: str) -> str:
        """Key for storing agent state."""
        return f"agent:state:{agent_id}"
    
    @staticmethod
    def execution_plan(execution_id: str) -> str:
        """Key for storing execution plans."""
        return f"execution:plan:{execution_id}"
    
    @staticmethod
    def execution_result(execution_id: str) -> str:
        """Key for storing execution results."""
        return f"execution:result:{execution_id}"


class Memory(BaseAgent[Any]):
    """
    Memory system for the VeriFact agent architecture.
    
    This component handles storage and retrieval of validation data, article information,
    and agent states using Redis as the backing store.
    """
    
    def __init__(
        self, 
        redis_client: Optional[redis.Redis] = None,
        context: Optional[AgentContext] = None
    ):
        super().__init__(context)
        self.redis = redis_client or redis.Redis.from_url(settings.REDIS_URL)
    
    async def store_validation_result(self, result: Any) -> None:
        """
        Store a validation result in memory.
        
        Args:
            result: The validation result to store
        """
        try:
            if not hasattr(result, 'id'):
                raise MemoryError("Validation result must have an 'id' attribute")
            
            key = MemoryKey.validation_result(result.id)
            await self._store(key, result, expire=timedelta(days=7))
            
            # If this is associated with an article, update the article's validation list
            if hasattr(result, 'article_id'):
                article_key = MemoryKey.article_validations(result.article_id)
                await self.redis.sadd(article_key, str(result.id))
                await self.redis.expire(article_key, timedelta(days=30))
            
        except Exception as e:
            logger.error(f"Failed to store validation result: {str(e)}", exc_info=True)
            raise MemoryError(f"Failed to store validation result: {str(e)}") from e
    
    async def get_validation_result(
        self, 
        validation_id: Union[str, UUID],
        model_type: Type[T]
    ) -> Optional[T]:
        """
        Retrieve a validation result from memory.
        
        Args:
            validation_id: The ID of the validation result to retrieve
            model_type: The Pydantic model class to deserialize into
            
        Returns:
            The deserialized validation result, or None if not found
        """
        try:
            key = MemoryKey.validation_result(validation_id)
            return await self._retrieve(key, model_type)
        except Exception as e:
            logger.error(f"Failed to retrieve validation result: {str(e)}", exc_info=True)
            raise MemoryError(f"Failed to retrieve validation result: {str(e)}") from e
    
    async def get_article_validations(
        self,
        article_id: Union[str, UUID]
    ) -> List[str]:
        """
        Get all validation IDs for an article.
        
        Args:
            article_id: The ID of the article
            
        Returns:
            List of validation IDs
        """
        try:
            key = MemoryKey.article_validations(article_id)
            members = await self.redis.smembers(key)
            return [member.decode('utf-8') for member in members]
        except Exception as e:
            logger.error(f"Failed to get article validations: {str(e)}", exc_info=True)
            raise MemoryError(f"Failed to get article validations: {str(e)}") from e
    
    async def store_execution_plan(
        self, 
        execution_id: str, 
        plan: Any,
        expire: Optional[timedelta] = None
    ) -> None:
        """
        Store an execution plan in memory.
        
        Args:
            execution_id: The ID of the execution
            plan: The execution plan to store
            expire: Optional expiration time
        """
        try:
            key = MemoryKey.execution_plan(execution_id)
            await self._store(key, plan, expire=expire or timedelta(days=1))
        except Exception as e:
            logger.error(f"Failed to store execution plan: {str(e)}", exc_info=True)
            raise MemoryError(f"Failed to store execution plan: {str(e)}") from e
    
    async def get_execution_plan(
        self, 
        execution_id: str,
        model_type: Type[T]
    ) -> Optional[T]:
        """
        Retrieve an execution plan from memory.
        
        Args:
            execution_id: The ID of the execution
            model_type: The Pydantic model class to deserialize into
            
        Returns:
            The deserialized execution plan, or None if not found
        """
        try:
            key = MemoryKey.execution_plan(execution_id)
            return await self._retrieve(key, model_type)
        except Exception as e:
            logger.error(f"Failed to retrieve execution plan: {str(e)}", exc_info=True)
            raise MemoryError(f"Failed to retrieve execution plan: {str(e)}") from e
    
    async def store_execution_result(
        self, 
        execution_id: str, 
        result: Any,
        expire: Optional[timedelta] = None
    ) -> None:
        """
        Store an execution result in memory.
        
        Args:
            execution_id: The ID of the execution
            result: The execution result to store
            expire: Optional expiration time
        """
        try:
            key = MemoryKey.execution_result(execution_id)
            await self._store(key, result, expire=expire or timedelta(days=7))
            
            # If this is associated with a validation, update the validation result
            if hasattr(result, 'results') and 'validation_id' in result.results:
                validation_key = MemoryKey.validation_result(result.results['validation_id'])
                await self.redis.hset(
                    validation_key,
                    'execution_result',
                    json.dumps(result.dict() if hasattr(result, 'dict') else result)
                )
                
        except Exception as e:
            logger.error(f"Failed to store execution result: {str(e)}", exc_info=True)
            raise MemoryError(f"Failed to store execution result: {str(e)}") from e
    
    async def get_execution_result(
        self, 
        execution_id: str,
        model_type: Type[T]
    ) -> Optional[T]:
        """
        Retrieve an execution result from memory.
        
        Args:
            execution_id: The ID of the execution
            model_type: The Pydantic model class to deserialize into
            
        Returns:
            The deserialized execution result, or None if not found
        """
        try:
            key = MemoryKey.execution_result(execution_id)
            return await self._retrieve(key, model_type)
        except Exception as e:
            logger.error(f"Failed to retrieve execution result: {str(e)}", exc_info=True)
            raise MemoryError(f"Failed to retrieve execution result: {str(e)}") from e
    
    async def _store(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[timedelta] = None
    ) -> None:
        """
        Store a value in Redis.
        
        Args:
            key: The Redis key
            value: The value to store (must be JSON-serializable or have a dict() method)
            expire: Optional expiration time
        """
        try:
            # Handle Pydantic models and other objects with dict() method
            if hasattr(value, 'dict'):
                data = value.dict()
            elif hasattr(value, 'model_dump'):  # Pydantic v2
                data = value.model_dump()
            else:
                data = value
                
            serialized = json.dumps(data, default=str)
            
            pipe = self.redis.pipeline()
            pipe.set(key, serialized)
            if expire:
                pipe.expire(key, expire)
            await pipe.execute()
            
        except Exception as e:
            logger.error(f"Failed to store data in Redis: {str(e)}", exc_info=True)
            raise MemoryError(f"Failed to store data in Redis: {str(e)}") from e
    
    async def _retrieve(self, key: str, model_type: Type[T]) -> Optional[T]:
        """
        Retrieve a value from Redis and deserialize it into the specified model.
        
        Args:
            key: The Redis key
            model_type: The Pydantic model class to deserialize into
            
        Returns:
            The deserialized model instance, or None if not found
        """
        try:
            data = await self.redis.get(key)
            if not data:
                return None
                
            deserialized = json.loads(data)
            
            # Handle both Pydantic v1 and v2
            if hasattr(model_type, 'parse_obj'):  # Pydantic v1
                return model_type.parse_obj(deserialized)
            else:  # Pydantic v2
                return model_type.model_validate(deserialized)
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON data: {str(e)}")
            raise MemoryError(f"Invalid data format in cache: {str(e)}") from e
        except Exception as e:
            logger.error(f"Failed to retrieve data from Redis: {str(e)}", exc_info=True)
            raise MemoryError(f"Failed to retrieve data from Redis: {str(e)}") from e
    
    async def close(self) -> None:
        """Close the Redis connection."""
        try:
            await self.redis.close()
        except Exception as e:
            logger.error(f"Error closing Redis connection: {str(e)}", exc_info=True)
            raise MemoryError(f"Error closing Redis connection: {str(e)}") from e
