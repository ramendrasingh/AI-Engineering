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

workspace_root = "."
tool_registry = ToolRegistry()

client = OllamaClient()
memory = ConversationalMemory()
embedder = EmbeddingService()

# Load RAG knowledge once
loader = KnowledgeLoader("knowledge")
docs = loader.load_document()
chunker = SentenceAwareChunker()
chunks = []
for doc in docs:
    chunks.extend(chunker.chunk_document(doc))

embedded_chunks = embedder.embed_chunks(chunks)

vector_store = VectorStore()

vector_store.add_embedded_chunks(embedded_chunks)

retriever = Retriever(embedder, vector_store)

token_counter = TokenCounter()
summary_manager = SummaryManager(client=client)
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


def test_list_directory():
    tool = ListDirectoryTool(workspace_root=workspace_root)
    result = tool.execute(path="knowledge")
    assert result.success is True
    assert "api.md" in result.content


def test_read_file():
    tool = ReadFileTool(workspace_root=workspace_root)
    result = tool.execute(path="knowledge/api.md")

    assert result.success is True
    assert "AI Orchestrator API" in result.content


def test_search_files():
    tool = SearchFilesTool(workspace_root=workspace_root, max_result=10)
    result = tool.execute(query="api")

    assert result.success is True
    assert "knowledge/api.md" in result.content


def test_search_then_read():
    orchestrator = Orchestrator(
        llm_client=client,
        memory=memory,
        retriever=retriever,
        tool_registory=tool_registry,
        token_counter=token_counter,
        summary_manager=summary_manager,
    )
    response = orchestrator.process_message(
        conversation_id="test-1",
        role="user",
        content="Find the API documentation and summarize it.",
    )

    assert response is not None
    assert "endpoint" in response.lower()


def test_rag_question():
    orchestrator = Orchestrator(
        llm_client=client,
        memory=memory,
        retriever=retriever,
        tool_registory=tool_registry,
        token_counter=token_counter,
        summary_manager=summary_manager,
    )

    response = orchestrator.process_message(
        conversation_id="rag-test",
        role="user",
        content="What API endpoints are available?",
    )

    assert response is not None
    assert "/health" in response
    assert "/generate" in response
    assert "/chat" in response
