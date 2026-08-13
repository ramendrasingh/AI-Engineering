
from app.rag.chunker import SentenceAwareChunker
from app.rag.embedding import EmbeddingService
from app.rag.loader import KnowledgeLoader


def test_embedding_chunks():
    loader = KnowledgeLoader("knowledge")

    docs = loader.load_document()

    chunker = SentenceAwareChunker()

    chunks = []

    for doc in docs:
        chunks.extend(chunker.chunk_document(doc))
        service = EmbeddingService()
        embedded = service.embed_chunks(chunks)
        print(len(embedded))
        print(len(embedded[0].embedding))
    
    assert len(docs) == 3