"""Test all agents."""
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

os.environ["GEMINI_API_KEY"] = "test-key"
os.environ["DEBUG"] = "true"


class TestVisionAgent:
    """Test VisionAgent."""
    
    @pytest.mark.asyncio
    async def test_vision_agent_analyze(self):
        """Test vision agent analyzes image."""
        from app.agents.vision_agent import VisionAgent
        
        # Mock Gemini client
        mock_gemini = MagicMock()
        mock_gemini.generate = AsyncMock(return_value="I see a stack trace error in the screenshot")
        
        agent = VisionAgent(mock_gemini)
        result = await agent.analyze("base64image", "Error 500 on API")
        
        assert "stack trace" in result.lower() or "error" in result.lower()
        mock_gemini.generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_vision_agent_with_empty_image(self):
        """Test vision agent with no image."""
        from app.agents.vision_agent import VisionAgent
        
        mock_gemini = MagicMock()
        mock_gemini.generate = AsyncMock(return_value="No image provided")
        
        agent = VisionAgent(mock_gemini)
        result = await agent.analyze("", "Service down")
        
        assert result == "No image provided"


class TestIncidentAnalystAgent:
    """Test IncidentAnalystAgent."""
    
    @pytest.mark.asyncio
    async def test_analyst_analyze_returns_hypotheses(self):
        """Test analyst agent returns hypotheses."""
        from app.agents.incident_analyst import IncidentAnalystAgent
        from app.domain.models import IncidentCategory
        import json
        
        mock_gemini = MagicMock()
        mock_gemini.generate = AsyncMock(return_value=json.dumps({
            "category": "database",
            "root_cause_summary": "Connection pool at maximum capacity",
            "hypotheses": [
                {
                    "description": "Database connection pool exhausted",
                    "confidence": 0.85,
                    "evidence": ["log error"],
                    "category": "database",
                    "mitigation_complexity": "low"
                }
            ],
            "is_critical": True
        }))
        
        agent = IncidentAnalystAgent(mock_gemini)
        hypotheses, category, root_cause = await agent.analyze(
            "API returning 500 errors", 
            "Visual shows error page",
            "Logs show connection timeout"
        )
        
        assert len(hypotheses) > 0
        assert category == IncidentCategory.DATABASE
        assert root_cause == "Connection pool at maximum capacity"
    
    @pytest.mark.asyncio
    async def test_analyst_handles_empty_context(self):
        """Test analyst with minimal context."""
        from app.agents.incident_analyst import IncidentAnalystAgent
        
        mock_gemini = MagicMock()
        mock_gemini.generate = AsyncMock(return_value="UNKNOWN")
        
        agent = IncidentAnalystAgent(mock_gemini)
        hypotheses, category, root_cause = await agent.analyze("", "", "")
        
        assert isinstance(hypotheses, list)
        assert category is not None


class TestActionAgent:
    """Test ActionAgent."""
    
    @pytest.mark.asyncio
    async def test_action_agent_prepare(self):
        """Test action agent prepares actions."""
        from app.agents.action_agent import ActionAgent
        import json
        
        mock_gemini = MagicMock()
        mock_gemini.generate = AsyncMock(return_value=json.dumps({
            "actions": [
                {"id": "act-1", "title": "Restart Database", "description": "Restart pg", "command": "kubectl rollout restart deployment/postgres", "requires_confirmation": True, "is_destructive": True}
            ]
        }))
        
        agent = ActionAgent(mock_gemini)
        hypotheses = []
        actions = await agent.prepare("Database down", hypotheses, "Check runbook: restart database")
        
        assert len(actions) > 0
        assert actions[0].title == "Restart Database"
    
    @pytest.mark.asyncio
    async def test_action_agent_parsing(self):
        """Test action parsing logic."""
        from app.agents.action_agent import ActionAgent
        import json
        
        agent = ActionAgent(None)
        
        # Test parsing JSON actions
        raw = json.dumps({
            "actions": [
                {"id": "a1", "title": "Test Action", "description": "Test", "command": "echo test", "requires_confirmation": False, "is_destructive": False}
            ]
        })
        actions = agent._parse_actions(raw)
        
        assert len(actions) > 0
        # Agent generates its own UUIDs for security/consistency
        assert len(actions[0].id) > 10 
    
    @pytest.mark.asyncio
    async def test_action_agent_handles_invalid_json(self):
        """Test action parsing with invalid JSON."""
        from app.agents.action_agent import ActionAgent
        
        agent = ActionAgent(None)
        
        # Should handle non-JSON gracefully
        raw = "No actions available"
        actions = agent._parse_actions(raw)
        
        assert actions == []


class TestRunbookAgent:
    """Test RunbookAgent."""
    
    @pytest.mark.asyncio
    async def test_runbook_agent_query(self):
        """Test runbook agent queries knowledge base."""
        from app.agents.runbook_agent import RunbookAgent
        
        # Mock dependencies
        mock_gemini = MagicMock()
        mock_gemini.generate = AsyncMock(return_value="Found relevant procedure in runbook")
        
        mock_embeddings = MagicMock()
        mock_embeddings.generate_query_embedding = AsyncMock(return_value=[0.1] * 768)
        
        mock_vector_db = MagicMock()
        mock_vector_db.search_relevant_chunks = AsyncMock(return_value=["Restart database procedure"])
        
        agent = RunbookAgent(mock_gemini, mock_embeddings, mock_vector_db)
        result = await agent.query("Database connection issues", "database")
        
        assert result is not None
        mock_vector_db.search_relevant_chunks.assert_called()
    
    @pytest.mark.asyncio
    async def test_runbook_agent_no_results(self):
        """Test runbook agent with no results."""
        from app.agents.runbook_agent import RunbookAgent
        
        mock_gemini = MagicMock()
        mock_embeddings = MagicMock()
        mock_embeddings.generate_query_embedding = AsyncMock(return_value=[0.1] * 768)
        
        mock_vector_db = MagicMock()
        mock_vector_db.search_relevant_chunks = AsyncMock(return_value=[])
        
        agent = RunbookAgent(mock_gemini, mock_embeddings, mock_vector_db)
        result = await agent.query("Unknown issue", "unknown")
        
        # Should still return something
        assert isinstance(result, str)
