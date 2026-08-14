from app.rag.chunker import SentenceAwareChunker
from app.rag.embedding import EmbeddingService
from app.rag.loader import KnowledgeLoader
from app.rag.retriever import Retriever
from app.rag.vector_store import VectorStore

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

retriever = Retriever(embedder, store)

results = retriever.retrieve(
    "What API endpoints are available?",
    top_k=3,
)

for chunk in results:
    print(chunk.metadata["source"])
    print(chunk.page_content)
