import pytest
import os
from unittest.mock import AsyncMock, patch

# Ensure env vars are set before imports
os.environ["GEMINI_API_KEY"] = "test-key"
os.environ["DEBUG"] = "true"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:pass@localhost:5432/db"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"

@pytest.fixture(autouse=True)
def mock_redis_globally():
    """Globally mock redis for all backend tests."""
    with patch("redis.asyncio.from_url") as mock_from_url:
        mock_client = AsyncMock()
        mock_from_url.return_value = mock_client
        
        # Simple in-memory storage for the mock
        storage = {}
        
        async def mock_setex(name, time, value):
            storage[name] = value
            return True
            
        async def mock_get(name):
            return storage.get(name)
            
        mock_client.setex.side_effect = mock_setex
        mock_client.get.side_effect = mock_get
        
        yield mock_client
