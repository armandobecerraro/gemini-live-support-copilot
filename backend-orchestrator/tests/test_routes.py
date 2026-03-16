"""Test API routes."""
import os
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

os.environ["GEMINI_API_KEY"] = "test-key"
os.environ["DEBUG"] = "true"

from app.main import app


client = TestClient(app)


class TestRootRoute:
    """Test root endpoint."""
    
    def test_root_endpoint(self):
        """Test root returns service info."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "backend-orchestrator"
        assert "version" in data


class TestSessionRoutes:
    """Test session endpoints."""
    
    def test_get_session_not_found(self):
        """Test getting non-existent session."""
        with patch("app.routes.session._session_service") as mock_service:
            mock_service.get = AsyncMock(return_value=None)
            
            response = client.get(
                "/session/nonexistent",
                headers={"X-API-Key": "test-key"}
            )
            
            assert response.status_code == 404
    
    def test_get_session_success(self):
        """Test getting existing session."""
        from app.domain.models import SessionState
        
        with patch("app.routes.session._session_service") as mock_service:
            mock_state = SessionState(session_id="test", correlation_id="corr")
            mock_service.get = AsyncMock(return_value=mock_state)
            
            response = client.get(
                "/session/test",
                headers={"X-API-Key": "test-key"}
            )
            
            assert response.status_code == 200
    
    def test_get_session_report(self):
        """Test getting session report."""
        from app.domain.models import SessionState
        
        with patch("app.routes.session._session_service") as mock_service:
            mock_state = SessionState(session_id="test", correlation_id="corr")
            mock_service.get = AsyncMock(return_value=mock_state)
            
            response = client.get(
                "/session/test/report",
                headers={"X-API-Key": "test-key"}
            )
            
            assert response.status_code == 200


class TestLogsRoutes:
    """Test logs endpoints."""
    
    def test_analyze_logs_success(self):
        """Test log analysis endpoint."""
        from app.domain.schemas import LogAnalysisResponse
        
        # Correctly patch the analyze_logs function if we want to bypass it
        # or patch the httpx call
        with patch("app.routes.logs.analyze_logs") as mock_analyze:
            mock_analyze.return_value = LogAnalysisResponse(
                errors=["test error"],
                warnings=[],
                anomalies=[],
                probable_cause="Test analysis"
            )
            
            response = client.post(
                "/logs/analyze",
                json={"raw_logs": "ERROR: test error"},
                headers={"X-API-Key": "test-key"}
            )
            
            assert response.status_code == 200
    
    def test_analyze_logs_empty(self):
        """Test log analysis with empty logs."""
        response = client.post(
            "/logs/analyze",
            json={"raw_logs": ""},
        )
        
        # Should return validation error
        assert response.status_code == 422


class TestHealthRoutes:
    """Test health endpoints."""
    
    def test_health_check(self):
        """Test health endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    def test_readiness_check(self):
        """Test readiness endpoint."""
        response = client.get("/readiness")
        
        assert response.status_code == 200
        assert response.json()["status"] == "ready"


class TestAgentRoutes:
    """Test agent endpoints."""
    
    def test_analyze_issue_endpoint_exists(self):
        """Test analyze issue endpoint exists."""
        from app.domain.schemas import AgentResponse
        
        with patch("app.routes.agent._orchestrator.process_issue") as mock_process:
            mock_process.return_value = AgentResponse(
                session_id="session-123",
                correlation_id="corr-456",
                what_i_understood="Service down",
                recommendations=["Check DB"],
                hypotheses=[],
                suggested_actions=[],
            )
            
            response = client.post(
                "/agent/issue",
                json={"description": "Service is down with 500 errors"},
                headers={"X-API-Key": "test-key"}
            )
            
            assert response.status_code == 200
    
    def test_confirm_action_endpoint_exists(self):
        """Test confirm action endpoint exists."""
        from app.domain.models import SessionState, SuggestedAction
        
        with patch("app.routes.agent._session_service.get") as mock_get:
            action = SuggestedAction(id="action-1", title="Test", description="Test", command="echo test")
            mock_state = SessionState(session_id="test-session", correlation_id="corr")
            mock_state.pending_actions = [action]
            mock_get.return_value = mock_state
            
            with patch("app.routes.agent._session_service.save") as mock_save:
                response = client.post(
                    "/agent/confirm-action",
                    json={
                        "session_id": "test-session",
                        "action_id": "action-1",
                        "approved": True,
                    },
                    headers={"X-API-Key": "test-key"}
                )
                
                assert response.status_code == 200
