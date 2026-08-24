from app.rag.chunker import Chunk
from tests.test_orchestrator import FakeLLM, create_orchestrator


class FakeRetriever:
    def __init__(self):
        self.retrieve_called = False
        self.calls = []

    def retrieve(self, query, top_k, min_threshold):
        self.retrieve_called = True

        self.calls.append(
            {
                "query": query,
                "top_k": top_k,
                "min_threshold": min_threshold,
            }
        )

        return [
            Chunk(chunk_id="chunk-1", page_content="FastAPI is a Python web framework.")
        ]


def test_rag_query_uses_retriever():
    llm = FakeLLM(['{"tool":null,"arguments":{}}'])

    orchestrator, tools = create_orchestrator(llm)

    response = orchestrator.process_message(
        conversation_id="rag-test", role="user", content="What is FastAPI?"
    )

    assert orchestrator.retriever.retrieve_called is True


def test_tool_query_does_not_use_retriever():

    llm = FakeLLM(
        [
            '{"tool":"read_file","arguments":{"path":"knowledge/api.md"}}',
            '{"tool":null,"arguments":{}}',
        ]
    )

    orchestrator, tools = create_orchestrator(llm)

    response = orchestrator.process_message(
        conversation_id="tool-test", role="user", content="Read knowledge/api.md"
    )

    assert orchestrator.retriever.retrieve_called is False


def test_tool_query_executes_tool():

    llm = FakeLLM(
        [
            '{"tool":"read_file","arguments":{"path":"knowledge/api.md"}}',
            '{"tool":null,"arguments":{}}',
        ]
    )

    orchestrator, tools = create_orchestrator(llm)

    orchestrator.process_message(
        conversation_id="tool-execution", role="user", content="Read knowledge/api.md"
    )

    assert tools["read_file"].execute_called is True


def test_rag_query_does_not_execute_tool():

    llm = FakeLLM(['{"tool":null,"arguments":{}}'])

    orchestrator, tools = create_orchestrator(llm)

    orchestrator.process_message(
        conversation_id="rag-no-tool", role="user", content="What is FastAPI?"
    )

    assert tools["read_file"].execute_called is False
    assert tools["search_files"].execute_called is False
    assert tools["list_directory"].execute_called is False
