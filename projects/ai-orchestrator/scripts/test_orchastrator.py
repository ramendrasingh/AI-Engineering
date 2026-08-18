from app.config.config import settings
from app.llm.client import OllamaClient
from app.memory.conversational import ConversationalMemory
from app.orchastrator.orchestrator import Orchestrator
from app.rag.chunker import SentenceAwareChunker
from app.rag.embedding import EmbeddingService
from app.rag.loader import KnowledgeLoader
from app.rag.retriever import Retriever
from app.rag.vector_store import VectorStore
from app.summary.conversation_summary import SummaryManager
from app.tokenizer.token_counter import TokenCounter
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
    SearchFilesTool(
        workspace_root=workspace_root,
        max_result=settings.MAX_SEARCH_RESULTS,
        excluded_dirs=settings.DEFAULT_EXCLUDED_DIRS,
    )  # "." can be the project root.
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
token_counter = TokenCounter()
summary_manager = SummaryManager(client=client)


orchestrator = Orchestrator(
    llm_client=client,
    memory=memory,
    retriever=retriever,
    tool_registory=tool_registry,
    token_counter=token_counter,
    summary_manager=summary_manager,
)

response = orchestrator.process_message(
    conversation_id="abc",
    role="user",
    content="Find the API documentation and summarize it.",
)

# response = orchestrator.process_message(
#    conversation_id="abc",
#    role="user",
#    content="Find API documentation in local directory",
# )

# RAG path test
# response = orchestrator.process_message(
#    conversation_id="abc",
#    role="user",
#    content="My name is Ram",
# )

print(response)
