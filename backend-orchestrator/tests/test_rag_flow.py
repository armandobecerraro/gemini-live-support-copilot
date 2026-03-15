import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.agents.runbook_agent import RunbookAgent
from app.infrastructure.gemini.client import GeminiClient
from app.infrastructure.gemini.embeddings import EmbeddingService
from app.infrastructure.postgres.models import VectorDBClient

@pytest.mark.asyncio
async def test_runbook_agent_retrieval_flow():
    """
    Integration test to verify that RunbookAgent:
    1. Generates an embedding for the incident.
    2. Queries the vector database for relevant chunks.
    3. Augments the Gemini prompt with retrieved context.
    """
    
    # 1. Setup mocks
    mock_gemini = MagicMock(spec=GeminiClient)
    mock_gemini.generate = AsyncMock(return_value="Check DB pool size in values.yaml")
    
    mock_embedding = MagicMock(spec=EmbeddingService)
    mock_embedding.generate_query_embedding = AsyncMock(return_value=[0.1] * 768)
    
    mock_vector_db = MagicMock(spec=VectorDBClient)
    mock_vector_db.search_relevant_chunks = AsyncMock(return_value=[
        "RECOVERY: Scaling up DB connections in Kubernetes...",
        "METRIC: pg_stat_activity shows high waiting counts."
    ])

    # 2. Initialize Agent
    agent = RunbookAgent(
        gemini=mock_gemini,
        embedding_service=mock_embedding,
        vector_db=mock_vector_db
    )

    # 3. Execute Query
    incident = "Payment API — 503 errors, DB connection pool exhausted"
    category = "database"
    response = await agent.query(incident, category)

    # 4. Assertions
    # Verify embedding was generated for the right incident
    mock_embedding.generate_query_embedding.assert_called_once_with(incident)
    
    # Verify vector search was performed
    mock_vector_db.search_relevant_chunks.assert_called_once()
    
    # Verify Gemini was called with a prompt containing the retrieved context
    call_args = mock_gemini.generate.call_args[0][0]
    assert "RECOVERY: Scaling up DB connections" in call_args
    assert "Payment API" in call_args
    assert response == "Check DB pool size in values.yaml"

@pytest.mark.asyncio
async def test_runbook_agent_handles_empty_retrieval():
    """Verify agent behavior when no relevant runbooks are found."""
    mock_gemini = MagicMock(spec=GeminiClient)
    mock_gemini.generate = AsyncMock(return_value="No specific procedure found.")
    
    mock_embedding = MagicMock(spec=EmbeddingService)
    mock_embedding.generate_query_embedding = AsyncMock(return_value=[0.1] * 768)
    
    mock_vector_db = MagicMock(spec=VectorDBClient)
    mock_vector_db.search_relevant_chunks = AsyncMock(return_value=[])

    agent = RunbookAgent(mock_gemini, mock_embedding, mock_vector_db)
    
    await agent.query("Unknown error", "unknown")
    
    call_args = mock_gemini.generate.call_args[0][0]
    assert "No relevant runbook context found." in call_args
