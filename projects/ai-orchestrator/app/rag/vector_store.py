import numpy as np

from app.rag.embedding import EmbeddedChunk


class VectorStore:
    def __init__(self):
        self.embedded_chunks: list[EmbeddedChunk] = []

    def add_embedded_chunks(self, chunks: list[EmbeddedChunk]):
        self.embedded_chunks.extend(chunks)

    def add_chunks(self, chunks):
        pass

    def search(
        self, query_embedding: np.ndarray, top_k: int = 3, min_similarity: float = 0.75
    ) -> list[EmbeddedChunk]:
        scored_chunks = []
        query_norm = np.linalg.norm(query_embedding)
        for item in self.embedded_chunks:
            chunk_norm = np.linalg.norm(item.embedding)
            similarity = np.dot(query_embedding, item.embedding) / (
                query_norm * chunk_norm
            )
            if similarity > min_similarity:
                scored_chunks.append((similarity, item))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)

        return [item for _, item in scored_chunks[:top_k]]

    def clear(self):
        self.embedded_chunks.clear()

    def size(self) -> int:
        return len(self.embedded_chunks)
