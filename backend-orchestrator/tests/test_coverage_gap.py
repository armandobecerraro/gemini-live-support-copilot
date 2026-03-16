import pytest
import base64
from app.config import Settings
from app.domain.schemas import IssueRequest
from app.prompts.loader import load_prompt
from app.infrastructure.gemini.client import GeminiClient
from app.infrastructure.gemini.embeddings import EmbeddingService
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from app.routes.agent import confirm_action
from app.routes.session import get_report
from app.security.api_key import require_api_key
import httpx

def test_settings_invalid_allowed_origins():
    with pytest.raises(ValueError):
        Settings(ALLOWED_ORIGINS=123)

def test_issue_request_invalid_base64():
    with pytest.raises(ValueError, match="image_base64 must be valid base64"):
        IssueRequest(description="valid description", image_base64="invalid-base64-!!!")

def test_load_prompt_not_found():
    with pytest.raises(FileNotFoundError):
        load_prompt("non_existent_prompt_123")

@pytest.mark.asyncio
async def test_gemini_client_error_logging():
    client = GeminiClient()
    client._model.generate_content_async = AsyncMock(side_effect=Exception("API Error"))
    with pytest.raises(Exception):
        await client.generate("test")

@pytest.mark.asyncio
async def test_gemini_client_stream_image():
    client = GeminiClient()
    mock_gen = AsyncMock()
    mock_gen.__aiter__.return_value = [MagicMock(text="chunk1")]
    client._model.generate_content_async = AsyncMock(return_value=mock_gen)
    
    chunks = []
    async for chunk in client.stream_generate("test", image_base64="YmFzZTY0"):
        chunks.append(chunk)
    assert chunks == ["chunk1"]

@pytest.mark.asyncio
async def test_embedding_service_error():
    service = EmbeddingService(api_key="test")
    with patch("google.generativeai.embed_content", side_effect=Exception("Embed Error")):
        with pytest.raises(Exception):
            await service.generate_embedding("test")
        with pytest.raises(Exception):
            await service.generate_query_embedding("test")

@pytest.mark.asyncio
async def test_confirm_action_session_not_found():
    mock_session_service = MagicMock()
    mock_session_service.get = AsyncMock(return_value=None)
    
    body = MagicMock(session_id="s1", action_id="a1", approved=True)
    with patch("app.routes.agent._session_service", mock_session_service):
        with pytest.raises(HTTPException) as exc:
            await confirm_action(body, MagicMock())
        assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_gemini_client_generate_image():
    client = GeminiClient()
    client._model.generate_content_async = AsyncMock(return_value=MagicMock(text="ok"))
    res = await client.generate("test", image_base64="YmFzZTY0")
    assert res == "ok"

def test_main_lifespan():
    from app.main import app
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_confirm_action_not_found():
    mock_session_service = MagicMock()
    mock_session_service.get = AsyncMock(return_value=MagicMock(pending_actions=[]))
    
    body = MagicMock(session_id="s1", action_id="a1", approved=True)
    with patch("app.routes.agent._session_service", mock_session_service):
        with pytest.raises(HTTPException) as exc:
            await confirm_action(body, MagicMock())
        assert exc.value.status_code == 404

def test_orchestrator_cloud_logging_success():
    mock_client = MagicMock()
    with patch("google.cloud.logging.Client", return_value=mock_client):
        import importlib
        import app.services.orchestrator
        importlib.reload(app.services.orchestrator)
        mock_client.setup_logging.assert_called_once()

@pytest.mark.asyncio
async def test_get_report_not_found():
    mock_session_service = MagicMock()
    mock_session_service.get = AsyncMock(return_value=None)
    with patch("app.routes.session._session_service", mock_session_service):
        with pytest.raises(HTTPException) as exc:
            await get_report("s1", MagicMock())
        assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_require_api_key_invalid():
    with patch("app.security.api_key.settings") as mock_settings:
        mock_settings.SECRET_KEY = "prod-key"
        mock_settings.DEBUG = False
        mock_settings.API_KEY_HEADER = "X-API-Key"
        with pytest.raises(HTTPException) as exc:
            await require_api_key(api_key="wrong-key")
        assert exc.value.status_code == 401

@pytest.mark.asyncio
async def test_orchestrator_logs_service_success():
    from app.services.orchestrator import OrchestratorService
    service = OrchestratorService(MagicMock())
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"errors": ["e1"], "probable_cause": "test"}
    
    with patch("httpx.AsyncClient.post", AsyncMock(return_value=mock_response)):
        res = await service._call_logs_service("logs", "s1")
        assert "e1" in res
        assert "test" in res

@pytest.mark.asyncio
async def test_routes_logs_success():
    from app.routes.logs import analyze_logs
    body = MagicMock()
    body.model_dump.return_value = {}
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"errors": [], "warnings": [], "anomalies": [], "probable_cause": "ok"}
    
    with patch("httpx.AsyncClient.post", AsyncMock(return_value=mock_response)):
        res = await analyze_logs(body)
        assert res["probable_cause"] == "ok"

def test_main_exception_handler():
    from app.main import global_exception_handler
    request = MagicMock()
    request.state.correlation_id = "test-id"
    exc = Exception("error")
    
    import asyncio
    response = asyncio.run(global_exception_handler(request, exc))
    assert response.status_code == 500
