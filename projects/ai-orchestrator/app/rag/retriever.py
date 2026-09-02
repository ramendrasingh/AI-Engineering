from app.logger.logger import logger
from app.observability.timer import Timer
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

    @Timer.timed("rag_retrieval")
    def retrieve(
        self, query: str, top_k: int = 3, min_threshold: int = 0.75
    ) -> list[Chunk]:

        query_embedding = self.embedding_service.embed_text(query)

        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k * 3,
            min_similarity=min_threshold,
        )

        seen_sources = set()

        deduplicated = []

        for item in results:
            source = item.chunk.metadata.get("source")
            if source in seen_sources:
                continue

            seen_sources.add(source)
            deduplicated.append(item)

            if len(deduplicated) >= top_k:
                break

        chunks = [item.chunk for item in deduplicated]
        logger.info(
            f"query : {query}"
            + f"chunks: {len(chunks)}"
            + f"Threshold: {top_k}"
            + f"Top similarity: "
        )
        return chunks
