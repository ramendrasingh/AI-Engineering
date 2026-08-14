from app.rag.chunker import SentenceAwareChunker
from app.rag.embedding import EmbeddingService
from app.rag.loader import KnowledgeLoader
from app.rag.vector_store import VectorStore


def test_vector_store():
    loader = KnowledgeLoader("knowledge")
    docs = loader.load_document()
    chunker = SentenceAwareChunker()

    chunks = []

    for doc in docs:
        chunks.extend(chunker.chunk_document(doc))

    embedder = EmbeddingService()

    embedded = embedder.embed_chunks(chunks)

    store = VectorStore()

    store.add_embedded_chunks(embedded)

    query = embedder.embed_text("What endpoints are available?")

    results = store.search(query, top_k=2)

    for r in results:
        print(r.chunk.metadata["source"])
        print(r.chunk.page_content[:200])
