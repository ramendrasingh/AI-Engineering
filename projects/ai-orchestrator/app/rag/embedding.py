import numpy as np
import requests
from pydantic import BaseModel, ConfigDict

from app.config.config import settings
from app.logger.logger import logger
from app.rag.chunker import Chunk


class EmbeddedChunk(BaseModel):
    chunk: Chunk
    embedding: np.ndarray
    model_config = ConfigDict(arbitrary_types_allowed=True)


class EmbeddingService:
    def __init__(self):
        self.session = requests.session()
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.EMBEDDING_MODEL

    def embed_text(self, text) -> list[float]:
        embeddings = self.embed_texts([text])
        return embeddings[0]

    def embed_texts(self, texts) -> list[list[float]]:
        response = self.session.post(
            f"{self.base_url}/api/embed",
            json={"model": self.model, "input": texts},
            timeout=120,
        )

        response.raise_for_status()
        data = response.json()
        return data["embeddings"]

    def embed_chunks(self, chunks) -> list[EmbeddedChunk]:
        texts = [chunk.page_content for chunk in chunks]
        embeddings = self.embed_texts(texts)
        embedded_chunks = []
        for chunk, embedding in zip(chunks, embeddings):
            embedded_chunks.append(
                EmbeddedChunk(
                    chunk=chunk, embedding=np.array(embedding, dtype=np.float32)
                )
            )

        logger.info(f"Embedded {len(embedded_chunks)} chunks using model {self.model}")

        return embedded_chunks
