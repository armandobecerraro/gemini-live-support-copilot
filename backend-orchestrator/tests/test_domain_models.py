"""Test domain models."""
import os
import pytest
from datetime import datetime

os.environ["GEMINI_API_KEY"] = "test-key"
os.environ["DEBUG"] = "true"

from app.domain.models import (
    IncidentCategory,
    IncidentSeverity,
    ActionStatus,
    Hypothesis,
    SuggestedAction,
    SessionState,
)


class TestIncidentCategory:
    """Test IncidentCategory enum."""
    
    def test_categories_exist(self):
        """Verify all categories are defined."""
        assert IncidentCategory.NETWORK.value == "network"
        assert IncidentCategory.DATABASE.value == "database"
        assert IncidentCategory.BACKEND.value == "backend"
        assert IncidentCategory.DEPLOYMENT.value == "deployment"
        assert IncidentCategory.FRONTEND.value == "frontend"
        assert IncidentCategory.UNKNOWN.value == "unknown"


class TestIncidentSeverity:
    """Test IncidentSeverity enum."""
    
    def test_severities_exist(self):
        """Verify all severities are defined."""
        assert IncidentSeverity.CRITICAL.value == "critical"
        assert IncidentSeverity.HIGH.value == "high"
        assert IncidentSeverity.MEDIUM.value == "medium"
        assert IncidentSeverity.LOW.value == "low"


class TestActionStatus:
    """Test ActionStatus enum."""
    
    def test_statuses_exist(self):
        """Verify all statuses are defined."""
        assert ActionStatus.PENDING.value == "pending"
        assert ActionStatus.EXECUTED.value == "executed"
        assert ActionStatus.REJECTED.value == "rejected"
        assert ActionStatus.FAILED.value == "failed"


class TestHypothesis:
    """Test Hypothesis dataclass."""
    
    def test_hypothesis_creation(self):
        """Test creating a hypothesis."""
        h = Hypothesis(
            description="Database connection pool exhausted",
            confidence=0.85,
            evidence=["Error: too many connections", "pg_stat_activity shows 100 connections"]
        )
        
        assert h.description == "Database connection pool exhausted"
        assert h.confidence == 0.85
        assert len(h.evidence) == 2
    
    def test_hypothesis_with_empty_evidence(self):
        """Test hypothesis with no evidence."""
        h = Hypothesis(description="Unknown error", confidence=0.1, evidence=[])
        
        assert h.evidence == []


class TestSuggestedAction:
    """Test SuggestedAction dataclass."""
    
    def test_action_creation(self):
        """Test creating a suggested action."""
        action = SuggestedAction(
            id="act-123",
            title="Restart PostgreSQL",
            description="Restart the database to clear connection pool",
            command="kubectl rollout restart deployment/postgres",
            requires_confirmation=True,
            is_destructive=True,
        )
        
        assert action.id == "act-123"
        assert action.title == "Restart PostgreSQL"
        assert action.requires_confirmation is True
        assert action.is_destructive is True
    
    def test_non_destructive_action(self):
        """Test non-destructive action."""
        action = SuggestedAction(
            id="act-456",
            title="Check logs",
            description="View recent logs",
            command="kubectl logs -n default -l app=myapp --tail=100",
            requires_confirmation=False,
            is_destructive=False,
        )
        
        assert action.is_destructive is False


class TestSessionState:
    """Test SessionState dataclass."""
    
    def test_session_state_creation(self):
        """Test creating a session state."""
        state = SessionState(
            session_id="test-session-123",
            correlation_id="corr-456",
        )
        
        assert state.session_id == "test-session-123"
        assert state.correlation_id == "corr-456"
        assert state.timeline == []
        assert state.active_hypotheses == []
        assert state.pending_actions == []
    
    def test_add_timeline_event(self):
        """Test adding timeline events."""
        state = SessionState(
            session_id="test-session",
            correlation_id="corr",
        )
        
        state.add_timeline_event("issue_received", {"description": "Service down"})
        
        assert len(state.timeline) == 1
        assert state.timeline[0]["type"] == "issue_received"
        assert "timestamp" in state.timeline[0]
    
    def test_add_multiple_timeline_events(self):
        """Test adding multiple timeline events."""
        state = SessionState(session_id="test", correlation_id="corr")
        
        state.add_timeline_event("start", {"step": 1})
        state.add_timeline_event("analysis", {"result": "found"})
        state.add_timeline_event("complete", {"status": "done"})
        
        assert len(state.timeline) == 3
        assert state.timeline[0]["type"] == "start"
        assert state.timeline[1]["type"] == "analysis"
        assert state.timeline[2]["type"] == "complete"
    
    def test_session_state_serialization(self):
        """Test that session state can be serialized."""
        from dataclasses import asdict
        
        state = SessionState(
            session_id="test-session",
            correlation_id="corr-123",
        )
        state.add_timeline_event("start", {"data": "test"})
        
        # Should be serializable to dict
        data = asdict(state)
        
        assert data["session_id"] == "test-session"
        assert len(data["timeline"]) == 1
