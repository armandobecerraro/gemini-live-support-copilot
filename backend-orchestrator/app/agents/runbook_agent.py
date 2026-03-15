"""
Runbook/RAG Agent — queries local knowledge base for procedures and commands.
"""
import logging
from pathlib import Path
from app.infrastructure.gemini.client import GeminiClient
from app.infrastructure.gemini.embeddings import EmbeddingService
from app.infrastructure.postgres.models import VectorDBClient
from app.prompts.loader import load_prompt

logger = logging.getLogger("supportsight.agents.runbook")

class RunbookAgent:
    def __init__(self, gemini: GeminiClient, embedding_service: EmbeddingService, vector_db: VectorDBClient):
        self._gemini = gemini
        self._embedding_service = embedding_service
        self._vector_db = vector_db

    async def query(self, incident_description: str, category: str) -> str:
        """Find relevant procedure from runbooks using pgvector similarity search."""
        try:
            # 1. Generate query embedding for the incident description
            query_embedding = await self._embedding_service.generate_query_embedding(incident_description)

            # 2. Retrieve Top-3 relevant chunks from pgvector
            relevant_chunks = await self._vector_db.search_relevant_chunks(query_embedding, limit=3)
            context = "\n\n---\n\n".join(relevant_chunks) if relevant_chunks else "No relevant runbook context found."

            # 3. Augment prompt with retrieved context
            prompt = load_prompt("runbook_query").format(
                runbooks=context,
                description=incident_description,
                category=category,
            )
            return await self._gemini.generate(prompt)
        except Exception as e:
            logger.error(f"Error in RAG retrieval: {str(e)}")
            return "Error retrieving runbook procedures."

