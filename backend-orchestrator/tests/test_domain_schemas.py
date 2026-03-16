"""Test domain schemas (Pydantic models)."""
import os
import pytest
from pydantic import ValidationError

os.environ["GEMINI_API_KEY"] = "test-key"
os.environ["DEBUG"] = "true"

from app.domain.schemas import (
    IssueRequest,
    ActionConfirmRequest,
    AgentResponse,
    SessionSummaryResponse,
    LogAnalysisRequest,
    LogAnalysisResponse,
)


class TestIssueRequest:
    """Test IssueRequest schema."""
    
    def test_valid_issue_request(self):
        """Test creating a valid issue request."""
        req = IssueRequest(description="Service is returning 500 errors")
        
        assert req.description == "Service is returning 500 errors"
    
    def test_issue_request_with_all_fields(self):
        """Test issue request with all optional fields."""
        req = IssueRequest(
            description="Database connection failures",
            logs="ERROR: connection refused",
            image_base64="iVBORw0KGgoAAAANSUhEUgAAAA==",
            session_id="session-123",
        )
        
        assert req.logs == "ERROR: connection refused"
        assert req.image_base64 == "iVBORw0KGgoAAAANSUhEUgAAAA=="
        assert req.session_id == "session-123"
    
    def test_issue_request_description_too_short(self):
        """Test that description must be at least 5 characters."""
        with pytest.raises(ValidationError):
            IssueRequest(description="abc")
    
    def test_issue_request_description_max_length(self):
        """Test max length validation."""
        long_desc = "x" * 4001
        with pytest.raises(ValidationError):
            IssueRequest(description=long_desc)


class TestActionConfirmRequest:
    """Test ActionConfirmRequest schema."""
    
    def test_valid_confirmation(self):
        """Test valid action confirmation."""
        req = ActionConfirmRequest(
            session_id="session-123",
            action_id="action-456",
            approved=True,
        )
        
        assert req.session_id == "session-123"
        assert req.action_id == "action-456"
        assert req.approved is True
    
    def test_rejected_confirmation(self):
        """Test rejected action."""
        req = ActionConfirmRequest(
            session_id="session-123",
            action_id="action-456",
            approved=False,
        )
        
        assert req.approved is False


class TestAgentResponse:
    """Test AgentResponse schema."""
    
    def test_full_response(self):
        """Test creating a complete agent response."""
        response = AgentResponse(
            session_id="session-123",
            correlation_id="corr-456",
            what_i_understood="API returning 500 errors",
            what_i_see="Error screen with stack trace",
            root_cause_summary="Database connection pool exhausted",
            recommendations=["Increase pool size", "Restart database"],
            next_action="Execute: kubectl rollout restart deployment/db",
            hypotheses=[
                {"description": "Pool exhausted", "confidence": 0.9, "evidence": ["log error"]}
            ],
            confidence=0.9,
            needs_more_info=False,
            suggested_actions=[
                {
                    "id": "act-1",
                    "title": "Restart DB",
                    "description": "Restart database",
                    "command": "restart db",
                    "requires_confirmation": True,
                    "is_destructive": True,
                }
            ],
        )
        
        assert response.session_id == "session-123"
        assert response.root_cause_summary == "Database connection pool exhausted"
        assert len(response.hypotheses) == 1
        assert response.hypotheses[0]["confidence"] == 0.9
    
    def test_response_without_optional_fields(self):
        """Test response without optional fields."""
        response = AgentResponse(
            session_id="session-123",
            correlation_id="corr-456",
            what_i_understood="Test incident",
            recommendations=[],
            hypotheses=[],
            confidence=0.0,
            needs_more_info=True,
            suggested_actions=[],
        )
        
        assert response.what_i_see is None
        assert response.root_cause_summary is None


class TestSessionSummaryResponse:
    """Test SessionSummaryResponse schema."""
    
    def test_session_summary(self):
        """Test session summary creation."""
        summary = SessionSummaryResponse(
            session_id="session-123",
            problem_summary="Test problem",
            incident_category="backend",
            severity="high",
            resolved=False,
            timeline=[
                {"type": "start", "timestamp": "2026-01-01T00:00:00"}
            ],
            markdown_report="# Report",
        )
        
        assert summary.session_id == "session-123"
        assert summary.severity == "high"


class TestLogAnalysisRequest:
    """Test LogAnalysisRequest schema."""
    
    def test_valid_log_request(self):
        """Test valid log analysis request."""
        req = LogAnalysisRequest(
            raw_logs="2026-01-01 ERROR Connection refused\n2026-01-01 WARN Retry attempt 1",
        )
        
        assert "ERROR" in req.raw_logs
    
    def test_log_request_too_long(self):
        """Test log request max length."""
        long_logs = "x" * 100001
        with pytest.raises(ValidationError):
            LogAnalysisRequest(raw_logs=long_logs)


class TestLogAnalysisResponse:
    """Test LogAnalysisResponse schema."""
    
    def test_log_response(self):
        """Test log analysis response."""
        response = LogAnalysisResponse(
            errors=["Connection refused", "Timeout"],
            warnings=[],
            anomalies=[],
            probable_cause="Database overload",
        )
        
        assert len(response.errors) == 2
        assert response.probable_cause == "Database overload"
    
    def test_log_response_with_warnings(self):
        """Test log response with warnings."""
        response = LogAnalysisResponse(
            errors=[],
            warnings=["High memory usage", "Slow query detected"],
            anomalies=[],
            probable_cause="None identified",
        )
        
        assert len(response.warnings) == 2
