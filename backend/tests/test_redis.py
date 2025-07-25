"""
Tests for Redis utility module.
"""

import asyncio
import json
import pickle
from datetime import timedelta
from unittest.mock import patch, MagicMock

import pytest
from pydantic import BaseModel

from src.core.redis import RedisManager, redis_manager


class TestModel(BaseModel):
    """Test model for Redis serialization tests."""
    name: str
    value: int
    is_valid: bool = True


class TestRedisManager:
    """Test cases for RedisManager class."""
    
    @pytest.mark.asyncio
    async def test_connection(self, redis_manager: RedisManager):
        """Test Redis connection."""
        client = await redis_manager.get_redis()
        assert await client.ping() is True
    
    @pytest.mark.asyncio
    async def test_set_get_string(self, redis_manager: RedisManager):
        """Test setting and getting string values."""
        key = "test:string"
        value = "test value"
        
        # Set value
        result = await redis_manager.set(key, value)
        assert result is True
        
        # Get value
        result = await redis_manager.get(key)
        assert result == value
    
    @pytest.mark.asyncio
    async def test_set_get_int(self, redis_manager: RedisManager):
        """Test setting and getting integer values."""
        key = "test:int"
        value = 42
        
        # Set value
        result = await redis_manager.set(key, value)
        assert result is True
        
        # Get value
        result = await redis_manager.get(key)
        assert result == str(value)  # Redis stores all values as strings
    
    @pytest.mark.asyncio
    async def test_set_get_pydantic_model(self, redis_manager: RedisManager):
        """Test setting and getting Pydantic models."""
        key = "test:model"
        value = TestModel(name="test", value=123)
        
        # Set value
        result = await redis_manager.set(key, value)
        assert result is True
        
        # Get value
        result = await redis_manager.get(key, model_type=TestModel)
        assert isinstance(result, TestModel)
        assert result.name == value.name
        assert result.value == value.value
        assert result.is_valid is True
    
    @pytest.mark.asyncio
    async def test_set_get_dict(self, redis_manager: RedisManager):
        """Test setting and getting dictionary values."""
        key = "test:dict"
        value = {"key1": "value1", "key2": 2, "key3": [1, 2, 3]}
        
        # Set value
        result = await redis_manager.set(key, value)
        assert result is True
        
        # Get value
        result = await redis_manager.get(key)
        assert result == value
    
    @pytest.mark.asyncio
    async def test_expiration(self, redis_manager: RedisManager):
        """Test key expiration."""
        key = "test:expire"
        value = "test value"
        
        # Set value with 1 second expiration
        result = await redis_manager.set(key, value, expire=1)
        assert result is True
        
        # Value should exist
        result = await redis_manager.get(key)
        assert result == value
        
        # Wait for expiration
        await asyncio.sleep(1.1)
        
        # Value should be expired
        result = await redis_manager.get(key)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete(self, redis_manager: RedisManager):
        """Test key deletion."""
        key = "test:delete"
        value = "test value"
        
        # Set value
        await redis_manager.set(key, value)
        
        # Verify value exists
        result = await redis_manager.get(key)
        assert result == value
        
        # Delete value
        result = await redis_manager.delete(key)
        assert result == 1
        
        # Verify value is deleted
        result = await redis_manager.get(key)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_exists(self, redis_manager: RedisManager):
        """Test key existence check."""
        key = "test:exists"
        
        # Key should not exist
        result = await redis_manager.exists(key)
        assert result is False
        
        # Set value
        await redis_manager.set(key, "test")
        
        # Key should exist
        result = await redis_manager.exists(key)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_clear_namespace(self, redis_manager: RedisManager):
        """Test clearing a namespace."""
        # Create test keys
        keys = [
            "namespace:key1",
            "namespace:key2",
            "other:key3"
        ]
        
        # Set values
        for key in keys:
            await redis_manager.set(key, "test")
        
        # Clear namespace
        result = await redis_manager.clear_namespace("namespace")
        assert result == 2  # Should delete 2 keys
        
        # Verify keys are deleted
        for key in keys[:2]:
            assert await redis_manager.exists(key) is False
        
        # Other namespace should be unaffected
        assert await redis_manager.exists(keys[2]) is True
    
    @pytest.mark.asyncio
    async def test_cached_decorator(self, redis_manager: RedisManager):
        """Test the @cached decorator."""
        # Create a test function
        call_count = 0
        
        @redis_manager.cached("test:cached", ttl=60)
        async def test_func(arg1, arg2):
            nonlocal call_count
            call_count += 1
            return {"result": arg1 + arg2, "call_count": call_count}
        
        # First call - should call the function
        result1 = await test_func(1, 2)
        assert result1 == {"result": 3, "call_count": 1}
        
        # Second call with same args - should use cache
        result2 = await test_func(1, 2)
        assert result2 == {"result": 3, "call_count": 1}  # call_count should not increment
        
        # Call with different args - should call the function again
        result3 = await test_func(3, 4)
        assert result3 == {"result": 7, "call_count": 2}
        
        # Original function should still work as expected
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_error_handling(self, redis_manager: RedisManager):
        """Test error handling for Redis operations."""
        # Test with invalid key type (should not raise)
        result = await redis_manager.get(123)  # type: ignore
        assert result is None
        
        # Test with unserializable value (a class with unpicklable attributes)
        class Unserializable:
            def __init__(self):
                self.lambda_func = lambda x: x  # Lambdas can't be pickled
                
        with pytest.raises((TypeError, AttributeError)):  # Different Python versions may raise different exceptions
            await redis_manager.set("test:invalid", Unserializable())
            
        # Test with unserializable value using a function that can't be pickled
        def some_function():
            pass
            
        with pytest.raises((TypeError, AttributeError)):
            await redis_manager.set("test:invalid_func", some_function)
            
        # Test with unserializable value in a list
        with pytest.raises((TypeError, AttributeError)):
            await redis_manager.set("test:invalid_list", [1, 2, some_function])
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test RedisManager as a context manager."""
        async with RedisManager() as manager:
            # Test basic operation
            await manager.set("test:context", "value")
            result = await manager.get("test:context")
            assert result == "value"
