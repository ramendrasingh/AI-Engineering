
from fastapi import FastAPI

from app.api.routes import create_router
from app.llm.client import OllamaClient
from app.memory.conversational import ConversationalMemory
from app.orchastrator.orchestrator import Orchastrator
from app.rag.chunker import SentenceAwareChunker
from app.rag.embedding import EmbeddingService
from app.rag.loader import KnowledgeLoader
from app.rag.retriever import Retriever
from app.rag.vector_store import VectorStore

client = OllamaClient()
memory = ConversationalMemory()



# Load RAG knowledge once
loader = KnowledgeLoader("knowledge")
docs = loader.load_document()
chunker = SentenceAwareChunker()
chunks = []
for doc in docs:
    chunks.extend(chunker.chunk_document(doc))

embedder = EmbeddingService()

embedded_chunks = embedder.embed_chunks(chunks)

vector_store = VectorStore()

vector_store.add_embedded_chunks(embedded_chunks)

retriever = Retriever(embedder, vector_store)


orchestrator = Orchastrator(
    llm_client=client,
    memory=memory,
    retriever=retriever
)


app = FastAPI(
    title="AI Orchastrator",
    description="AI service to orchestrate multiple AI models and provide a unified interface for generating responses.",
    version="1.0.0"
)

app.include_router(create_router(orchestrator= orchestrator))

