import asyncio
import os
from pathlib import Path
from app.infrastructure.gemini.embeddings import EmbeddingService
from app.infrastructure.postgres.models import VectorDBClient
from app.config import get_settings

RUNBOOKS_DIR = Path(__file__).parent.parent / "docs" / "runbooks"

async def ingest_runbooks():
    settings = get_settings()
    print(f"Starting ingestion from {RUNBOOKS_DIR}...")
    
    embedding_service = EmbeddingService(api_key=settings.GEMINI_API_KEY)
    vector_db = VectorDBClient(dsn=settings.DATABASE_URL)
    
    if not RUNBOOKS_DIR.exists():
        print("Runbooks directory not found!")
        return

    for f in RUNBOOKS_DIR.glob("*.md"):
        content = f.read_text()
        print(f"Processing {f.name}...")
        
        # Simple chunking by paragraph (could be improved)
        chunks = [c.strip() for c in content.split("\n\n") if len(c.strip()) > 50]
        
        for i, chunk in enumerate(chunks):
            embedding = await embedding_service.generate_embedding(chunk)
            metadata = {"source": f.name, "chunk_index": i}
            await vector_db.insert_chunk(chunk, metadata, embedding)
            print(f"  Ingested chunk {i+1}/{len(chunks)}")

    print("Ingestion complete!")

if __name__ == "__main__":
    asyncio.run(ingest_runbooks())
