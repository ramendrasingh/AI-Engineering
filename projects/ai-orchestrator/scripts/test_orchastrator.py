from app.llm.client import OllamaClient
from app.memory.conversational import ConversationalMemory
from app.orchastrator.orchestrator import Orchastrator
from app.rag.chunker import SentenceAwareChunker
from app.rag.embedding import EmbeddingService
from app.rag.loader import KnowledgeLoader
from app.rag.retriever import Retriever
from app.rag.vector_store import VectorStore
from app.tool.list_directory import ListDirectoryTool
from app.tool.read_file import ReadFileTool
from app.tool.registry import ToolRegistry
from app.tool.search_files import SearchFilesTool

client = OllamaClient()
memory = ConversationalMemory()

workspace_root = "."
tool_registry = ToolRegistry()

tool_registry.register(
    ReadFileTool(workspace_root=workspace_root)  # "." can be the project root.
)

tool_registry.register(
    ListDirectoryTool(workspace_root=workspace_root)  # "." can be the project root.
)

tool_registry.register(
    SearchFilesTool(workspace_root=workspace_root)  # "." can be the project root.
)

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
    llm_client=client, memory=memory, retriever=retriever, tool_registory=tool_registry
)

# response = orchestrator.process_message(
#    conversation_id="abc", role="user", content="List file of the knowledge directory"
# )

# response = orchestrator.process_message(
#    conversation_id="abc",
#    role="user",
#    content="Find API documentation in local directory",
# )

# RAG path test
response = orchestrator.process_message(
    conversation_id="abc",
    role="user",
    content="My name is Ram",
)

print(response)
