"""Test infrastructure components."""
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

os.environ["GEMINI_API_KEY"] = "test-key"
os.environ["DEBUG"] = "true"


class TestGeminiClient:
    """Test GeminiClient."""
    
    @pytest.mark.asyncio
    async def test_client_generate(self):
        """Test generate method."""
        from app.infrastructure.gemini.client import GeminiClient
        
        with patch("app.infrastructure.gemini.client.genai") as mock_genai:
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "Test response"
            mock_model.generate_content_async = AsyncMock(return_value=mock_response)
            mock_genai.GenerativeModel.return_value = mock_model
            
            client = GeminiClient()
            result = await client.generate("Test prompt")
            
            assert result == "Test response"
    
    @pytest.mark.asyncio
    async def test_client_stream_generate(self):
        """Test streaming generate method."""
        from app.infrastructure.gemini.client import GeminiClient
        
        with patch("app.infrastructure.gemini.client.genai") as mock_genai:
            mock_model = MagicMock()
            
            async def mock_stream_gen():
                mock_chunk = MagicMock()
                mock_chunk.text = "Streaming response"
                yield mock_chunk
                
            mock_model.generate_content_async = AsyncMock(return_value=mock_stream_gen())
            mock_genai.GenerativeModel.return_value = mock_model
            
            client = GeminiClient()
            result_gen = client.stream_generate("Test prompt")
            results = [r async for r in result_gen]
            
            assert "Streaming response" in "".join(results)
    
    @pytest.mark.asyncio
    async def test_client_chat(self):
        """Test chat method."""
        from app.infrastructure.gemini.client import GeminiClient
        
        with patch("app.infrastructure.gemini.client.genai") as mock_genai:
            mock_model = MagicMock()
            mock_session = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "Chat response"
            mock_session.send_message_async = AsyncMock(return_value=mock_response)
            mock_model.start_chat.return_value = mock_session
            mock_genai.GenerativeModel.return_value = mock_model
            
            client = GeminiClient()
            result = await client.chat([], "Hello")
            
            assert result == "Chat response"


class TestEmbeddingService:
    """Test EmbeddingService."""
    
    @pytest.mark.asyncio
    async def test_generate_embedding(self):
        """Test generating embeddings."""
        from app.infrastructure.gemini.embeddings import EmbeddingService
        
        with patch("app.infrastructure.gemini.embeddings.genai") as mock_genai:
            mock_genai.embed_content.return_value = {"embedding": [0.1] * 768}
            
            service = EmbeddingService("test-key")
            result = await service.generate_embedding("Test text")
            
            assert len(result) == 768
            assert result[0] == 0.1
    
    @pytest.mark.asyncio
    async def test_generate_query_embedding(self):
        """Test query embedding generation."""
        from app.infrastructure.gemini.embeddings import EmbeddingService
        
        with patch("app.infrastructure.gemini.embeddings.genai") as mock_genai:
            mock_genai.embed_content.return_value = {"embedding": [0.2] * 768}
            
            service = EmbeddingService("test-key")
            result = await service.generate_query_embedding("Query text")
            
            assert len(result) == 768


class TestVectorDBClient:
    """Test VectorDBClient."""
    
    @pytest.mark.asyncio
    async def test_search_chunks(self):
        """Test searching relevant chunks."""
        from app.infrastructure.postgres.models import VectorDBClient
        
        with patch("app.infrastructure.postgres.models.asyncpg") as mock_asyncpg:
            mock_pool = MagicMock()
            mock_conn = MagicMock()
            mock_conn.fetch = AsyncMock(return_value=[
                {"content": "Runbook content 1", "metadata": '{"title": "Restart DB"}'},
                {"content": "Runbook content 2", "metadata": '{"title": "Scale Service"}'},
            ])
            mock_conn.execute = AsyncMock()
            mock_conn.set_type_codec = AsyncMock()
            
            class AsyncContextManagerMock:
                async def __aenter__(self): return mock_conn
                async def __aexit__(self, *args): pass
            
            mock_pool.acquire.return_value = AsyncContextManagerMock()
            mock_asyncpg.create_pool = AsyncMock(return_value=mock_pool)
            
            with patch("app.infrastructure.postgres.models.register_vector", new_callable=AsyncMock):
                client = VectorDBClient("postgresql://test:test@localhost/testdb")
                result = await client.search_relevant_chunks([0.1] * 768, limit=3)
                
                assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_insert_chunk(self):
        """Test inserting a chunk."""
        from app.infrastructure.postgres.models import VectorDBClient
        
        with patch("app.infrastructure.postgres.models.asyncpg") as mock_asyncpg:
            mock_pool = MagicMock()
            mock_conn = MagicMock()
            mock_conn.execute = AsyncMock(return_value="INSERT 0 1")
            mock_conn.set_type_codec = AsyncMock()
            
            class AsyncContextManagerMock:
                async def __aenter__(self): return mock_conn
                async def __aexit__(self, *args): pass
                
            mock_pool.acquire.return_value = AsyncContextManagerMock()
            mock_asyncpg.create_pool = AsyncMock(return_value=mock_pool)
            
            with patch("app.infrastructure.postgres.models.register_vector", new_callable=AsyncMock):
                client = VectorDBClient("postgresql://test:test@localhost/testdb")
                await client.insert_chunk(
                    "Test content",
                    {"title": "Test"},
                    [0.1] * 768
                )
                
                mock_conn.execute.assert_called()


class TestPromptsLoader:
    """Test prompts loader."""
    
    def test_load_prompt(self):
        """Test loading a prompt."""
        from app.prompts.loader import load_prompt
        
        # Should load vision_analysis prompt
        prompt = load_prompt("vision_analysis")
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
    
    def test_load_incident_analysis_prompt(self):
        """Test loading incident analysis prompt."""
        from app.prompts.loader import load_prompt
        
        prompt = load_prompt("incident_analysis")
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
    
    def test_load_runbook_query_prompt(self):
        """Test loading runbook query prompt."""
        from app.prompts.loader import load_prompt
        
        prompt = load_prompt("runbook_query")
        
        assert isinstance(prompt, str)
    
    def test_prompt_caching(self):
        """Test that prompts are cached."""
        from app.prompts.loader import load_prompt, _CACHE
        
        # Clear cache first
        _CACHE.clear()
        
        # Load same prompt twice
        prompt1 = load_prompt("vision_analysis")
        prompt2 = load_prompt("vision_analysis")
        
        # Should be the same object (cached)
        assert prompt1 == prompt2
