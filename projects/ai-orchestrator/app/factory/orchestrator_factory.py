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
from app.tool.executor import ToolExecutor
from app.tool.list_directory import ListDirectoryTool
from app.tool.read_file import ReadFileTool
from app.tool.registry import ToolRegistry
from app.tool.search_files import SearchFilesTool


def create_orchestrator() -> Orchestrator:
    client = OllamaClient()

    memory = ConversationalMemory()

    tool_registry = create_tool_registry()

    retriever = create_retriever()

    token_counter = TokenCounter()

    summary_manager = SummaryManager(client=client)
    tool_executor = ToolExecutor(tool_registry)

    return Orchestrator(
        llm_client=client,
        memory=memory,
        retriever=retriever,
        token_counter=token_counter,
        summary_manager=summary_manager,
        tool_executor=tool_executor,
    )


def create_tool_registry() -> ToolRegistry:
    tool_registry = ToolRegistry()
    tool_registry.register(
        ReadFileTool(
            workspace_root=settings.WORKSPACE_ROOT
        )  # "." can be the project root.
    )

    tool_registry.register(
        ListDirectoryTool(
            workspace_root=settings.WORKSPACE_ROOT
        )  # "." can be the project root.
    )

    tool_registry.register(
        SearchFilesTool(
            workspace_root=settings.WORKSPACE_ROOT,
            max_result=settings.MAX_SEARCH_RESULTS,
            excluded_dirs=settings.DEFAULT_EXCLUDED_DIRS,
        )  # "." can be the project root.
    )

    return tool_registry


def create_retriever() -> Retriever:
    # Load RAG knowledge once
    loader = KnowledgeLoader(settings.KNOWLEDGE_PATH)
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

    return retriever
