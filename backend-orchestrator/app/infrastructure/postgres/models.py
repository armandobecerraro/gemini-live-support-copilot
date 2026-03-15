from typing import List, Optional
import json
import logging
import asyncpg
from pgvector.asyncpg import register_vector
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class RunbookChunk(BaseModel):
    id: Optional[int] = None
    content: str
    metadata: dict
    embedding: List[float]

class VectorDBClient:
    def __init__(self, dsn: str):
        # asyncpg doesn't support 'postgresql+asyncpg://' driver part, only 'postgresql://'
        self.dsn = dsn.replace("postgresql+asyncpg://", "postgresql://")
        self._pool = None

    async def connect(self):
        if not self._pool:
            self._pool = await asyncpg.create_pool(self.dsn)
            async with self._pool.acquire() as conn:
                await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
                await register_vector(conn)
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS runbook_chunks (
                        id SERIAL PRIMARY KEY,
                        content TEXT NOT NULL,
                        metadata JSONB,
                        embedding vector(768)
                    )
                """)
                # Create HNSW index for faster similarity search
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS runbook_chunks_embedding_idx 
                    ON runbook_chunks USING hnsw (embedding vector_cosine_ops)
                """)
        return self._pool

    async def search_relevant_chunks(self, query_embedding: List[float], limit: int = 3) -> List[str]:
        pool = await self.connect()
        async with pool.acquire() as conn:
            await register_vector(conn)
            rows = await conn.fetch(
                """
                SELECT content FROM runbook_chunks
                ORDER BY embedding <=> $1
                LIMIT $2
                """,
                query_embedding,
                limit
            )
            return [row['content'] for row in rows]

    async def insert_chunk(self, content: str, metadata: dict, embedding: List[float]):
        pool = await self.connect()
        async with pool.acquire() as conn:
            await register_vector(conn)
            await conn.execute(
                "INSERT INTO runbook_chunks (content, metadata, embedding) VALUES ($1, $2, $3)",
                content, json.dumps(metadata), embedding
            )
