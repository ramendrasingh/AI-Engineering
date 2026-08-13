from typing import List

from app.rag.chunker import Chunk
from app.rag.embedding import EmbeddingService
from app.rag.vector_store import VectorStore


class Retriever:

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
    ) -> List[Chunk]:

        query_embedding = self.embedding_service.embed_text(query)

        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
        )

        return [item.chunk for item in results]