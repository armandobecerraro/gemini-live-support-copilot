"""Test orchestrator service."""
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

os.environ["GEMINI_API_KEY"] = "test-key"
os.environ["DEBUG"] = "true"

from app.services.orchestrator import OrchestratorService
from app.services.session_service import SessionService
from app.domain.models import IncidentCategory, Hypothesis, SuggestedAction


class TestOrchestratorService:
    """Test OrchestratorService."""
    
    @pytest.mark.asyncio
    async def test_process_issue_basic(self):
        """Test basic issue processing."""
        from app.domain.schemas import IssueRequest
        
        # Mock all dependencies
        with patch("app.services.orchestrator.GeminiClient") as mock_gemini_cls, \
             patch("app.services.orchestrator.EmbeddingService") as mock_emb_cls, \
             patch("app.services.orchestrator.VectorDBClient") as mock_vec_cls, \
             patch("app.services.orchestrator.SessionService") as mock_sess_cls:
            
            # Setup mocks
            mock_gemini = MagicMock()
            mock_gemini_cls.return_value = mock_gemini
            
            mock_session_service = MagicMock(spec=SessionService)
            mock_session_service.get_or_create = AsyncMock()
            from app.domain.models import SessionState
            mock_session_service.get_or_create.return_value = SessionState(
                session_id="test", correlation_id="corr"
            )
            mock_session_service.save = AsyncMock()
            
            # Create orchestrator
            orchestrator = OrchestratorService(mock_session_service)
            
            # Mock agents
            orchestrator._vision_agent.analyze = AsyncMock(return_value="")
            orchestrator._analyst_agent.analyze = AsyncMock(return_value=(
                [Hypothesis(description="Test", confidence=0.8, evidence=[])],
                IncidentCategory.BACKEND,
                "Test cause"
            ))
            orchestrator._runbook_agent.query = AsyncMock(return_value="Runbook info")
            orchestrator._action_agent.prepare = AsyncMock(return_value=[])
            
            # Test
            request = IssueRequest(description="Test service is down")
            result = await orchestrator.process_issue(request, "corr-123")
            
            assert result.session_id is not None
            assert result.what_i_understood == "Test service is down"
    
    @pytest.mark.asyncio
    async def test_process_issue_with_image(self):
        """Test issue processing with image."""
        from app.domain.schemas import IssueRequest
        
        with patch("app.services.orchestrator.GeminiClient") as mock_gemini_cls, \
             patch("app.services.orchestrator.EmbeddingService"), \
             patch("app.services.orchestrator.VectorDBClient"), \
             patch("app.services.orchestrator.SessionService"):
            
            mock_session_service = MagicMock(spec=SessionService)
            from app.domain.models import SessionState
            mock_session_service.get_or_create = AsyncMock(return_value=SessionState(
                session_id="test", correlation_id="corr"
            ))
            mock_session_service.save = AsyncMock()
            
            orchestrator = OrchestratorService(mock_session_service)
            
            # Mock vision agent
            orchestrator._vision_agent.analyze = AsyncMock(return_value="I see error 500")
            orchestrator._analyst_agent.analyze = AsyncMock(return_value=(
                [], IncidentCategory.BACKEND, None
            ))
            orchestrator._runbook_agent.query = AsyncMock(return_value="")
            orchestrator._action_agent.prepare = AsyncMock(return_value=[])
            
            request = IssueRequest(
                description="Service down",
                image_base64="iVBORw0KGgoAAAANSUhEUgAAAA=="
            )
            result = await orchestrator.process_issue(request, "corr")
            
            assert result.what_i_see is not None
            orchestrator._vision_agent.analyze.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_issue_with_logs(self):
        """Test issue processing with logs."""
        from app.domain.schemas import IssueRequest
        
        with patch("app.services.orchestrator.GeminiClient") as mock_gemini_cls, \
             patch("app.services.orchestrator.EmbeddingService"), \
             patch("app.services.orchestrator.VectorDBClient"), \
             patch("app.services.orchestrator.SessionService") as mock_sess_cls:
            
            mock_session_service = MagicMock(spec=SessionService)
            from app.domain.models import SessionState
            mock_session_service.get_or_create = AsyncMock(return_value=SessionState(
                session_id="test", correlation_id="corr"
            ))
            mock_session_service.save = AsyncMock()
            
            orchestrator = OrchestratorService(mock_session_service)
            
            # Mock agents
            orchestrator._vision_agent.analyze = AsyncMock(return_value="")
            orchestrator._analyst_agent.analyze = AsyncMock(return_value=(
                [], IncidentCategory.BACKEND, None
            ))
            orchestrator._runbook_agent.query = AsyncMock(return_value="")
            orchestrator._action_agent.prepare = AsyncMock(return_value=[])
            
            request = IssueRequest(
                description="API failing",
                logs="ERROR: Connection refused at line 45"
            )
            result = await orchestrator.process_issue(request, "corr")
            
            # Logs should trigger needs_more_info to be False
            assert result.needs_more_info is False
    
    def test_assess_severity(self):
        """Test severity assessment."""
        with patch("app.services.orchestrator.GeminiClient"), \
             patch("app.services.orchestrator.EmbeddingService"), \
             patch("app.services.orchestrator.VectorDBClient"), \
             patch("app.services.orchestrator.SessionService"):
            
            from app.domain.models import IncidentSeverity
            
            # Critical severity
            result = OrchestratorService._assess_severity([
                Hypothesis(description="Test", confidence=0.9, evidence=[])
            ])
            assert result == IncidentSeverity.CRITICAL
            
            # High severity
            result = OrchestratorService._assess_severity([
                Hypothesis(description="Test", confidence=0.7, evidence=[])
            ])
            assert result == IncidentSeverity.HIGH
            
            # Medium severity
            result = OrchestratorService._assess_severity([
                Hypothesis(description="Test", confidence=0.4, evidence=[])
            ])
            assert result == IncidentSeverity.MEDIUM
            
            # Low severity
            result = OrchestratorService._assess_severity([
                Hypothesis(description="Test", confidence=0.2, evidence=[])
            ])
            assert result == IncidentSeverity.LOW
            
            # No hypotheses
            result = OrchestratorService._assess_severity([])
            assert result == IncidentSeverity.MEDIUM
    
    @pytest.mark.asyncio
    async def test_logs_service_unavailable(self):
        """Test handling when logs service is unavailable."""
        from app.domain.schemas import IssueRequest
        
        with patch("app.services.orchestrator.GeminiClient") as mock_gemini_cls, \
             patch("app.services.orchestrator.EmbeddingService"), \
             patch("app.services.orchestrator.VectorDBClient"), \
             patch("app.services.orchestrator.SessionService") as mock_sess_cls, \
             patch("app.services.orchestrator.httpx.AsyncClient") as mock_http:
            
            mock_session_service = MagicMock(spec=SessionService)
            from app.domain.models import SessionState
            mock_session_service.get_or_create = AsyncMock(return_value=SessionState(
                session_id="test", correlation_id="corr"
            ))
            mock_session_service.save = AsyncMock()
            
            # Make HTTP call fail
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(side_effect=Exception("Service down"))
            mock_http.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_http.return_value.__aexit__ = AsyncMock(return_value=None)
            
            orchestrator = OrchestratorService(mock_session_service)
            
            # Mock other agents
            orchestrator._vision_agent.analyze = AsyncMock(return_value="")
            orchestrator._analyst_agent.analyze = AsyncMock(return_value=(
                [], IncidentCategory.BACKEND, None
            ))
            orchestrator._runbook_agent.query = AsyncMock(return_value="")
            orchestrator._action_agent.prepare = AsyncMock(return_value=[])
    
            request = IssueRequest(description="Long enough description", logs="ERROR")
            result = await orchestrator.process_issue(request, "corr")
            
            # Should still work, just without log analysis
            assert result.session_id is not None
