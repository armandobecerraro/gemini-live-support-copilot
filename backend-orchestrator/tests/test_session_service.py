"""Test session service."""
import os
import pytest
import json
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime

from app.services.session_service import SessionService
from app.domain.models import SessionState, Hypothesis


class TestSessionService:
    """Test SessionService."""
    
    @pytest.mark.asyncio
    async def test_get_or_create_new_session(self):
        """Test creating a new session."""
        service = SessionService()
        
        state = await service.get_or_create("new-session-123", "corr-456")
        
        assert state.session_id == "new-session-123"
        assert state.correlation_id == "corr-456"
        assert state.timeline == []
    
    @pytest.mark.asyncio
    async def test_get_or_create_existing_session(self):
        """Test getting existing session."""
        service = SessionService()
        
        # Create first and save
        state = await service.get_or_create("existing-session", "corr-1")
        await service.save(state)
        
        # Retrieve
        state = await service.get_or_create("existing-session", "corr-2")
        
        assert state.session_id == "existing-session"
        # Should keep original correlation ID
        assert state.correlation_id == "corr-1"
    
    @pytest.mark.asyncio
    async def test_save_and_get(self):
        """Test save and get session."""
        service = SessionService()
        
        state = SessionState(session_id="test-save", correlation_id="corr")
        state.add_timeline_event("test", {"data": "value"})
        
        await service.save(state)
        
        retrieved = await service.get("test-save")
        
        assert retrieved is not None
        assert retrieved.session_id == "test-save"
        assert len(retrieved.timeline) == 1
    
    @pytest.mark.asyncio
    async def test_get_nonexistent(self):
        """Test getting non-existent session returns None."""
        service = SessionService()
        
        result = await service.get("definitely-does-not-exist")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_session_serialization(self):
        """Test session serialization/deserialization."""
        service = SessionService()
        
        state = SessionState(
            session_id="serialize-test",
            correlation_id="corr-123",
        )
        state.add_timeline_event("start", {"step": 1})
        state.active_hypotheses = [
            Hypothesis(description="Test hypothesis", confidence=0.8, evidence=[])
        ]
        
        await service.save(state)
        
        retrieved = await service.get("serialize-test")
        
        assert retrieved is not None
        assert len(retrieved.active_hypotheses) == 1
        assert retrieved.active_hypotheses[0].description == "Test hypothesis"
