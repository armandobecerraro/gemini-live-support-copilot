import google.generativeai as genai
from typing import List
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = "models/text-embedding-004"

    async def generate_embedding(self, text: str) -> List[float]:
        try:
            # The SDK handles the API call; using synchronous call for simplicity in this context 
            # as the Google GenAI SDK doesn't have a direct async embedding method yet
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise

    async def generate_query_embedding(self, text: str) -> List[float]:
        try:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_query"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            raise
