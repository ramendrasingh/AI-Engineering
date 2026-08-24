import pytest

from app.models.schemas import ChatMessage
from app.orchastrator.orchestrator import Orchestrator


class FakeLLM:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def generate(self, prompt, *args, **kwargs):
        self.calls.append(
            {
                "prompt": prompt,
                "args": args,
                "kwargs": kwargs,
            }
        )

        if not self.responses:
            raise RuntimeError("No more fake LLM responses available")

        return self.responses.pop(0)

    def chat(self, messages):
        self.calls.append({"messages": messages})

        class Response:
            role = "assistant"
            content = "Final response"

        return Response()


class FakeMemory:
    def __init__(self):
        self.messages = {}
        self.summaries = {}

    def get_conversation(self, conversation_id):
        return self.messages.get(conversation_id, [])

    def add_message(self, conversation_id, role, content):
        self.messages.setdefault(conversation_id, []).append(
            ChatMessage(role=role, content=content)
        )

    def get_summary(self, conversation_id):
        return self.summaries.get(conversation_id, "")

    def set_summary(self, conversation_id, summary):
        self.summaries[conversation_id] = summary

    def replace_messages(self, conversation_id, messages):
        self.messages[conversation_id] = messages


class FakeRetriever:
    def retrieve(self, query, top_k, min_threshold):
        return []


class FakeTool:
    def __init__(self, name, content):
        self.name = name
        self.content = content
        self.calls = []

    def execute(self, **arguments):

        self.calls.append(arguments)

        content = self.content

        class Result:
            success = True

        result = Result()
        result.content = content

        return result


class FakeToolRegistry:
    def __init__(self, tools):
        self.tools = tools

    def get_tool(self, name):
        if name not in self.tools:
            raise ValueError(f"Unknown tool: {name}")

        return self.tools[name]


class FakeTokenCounter:
    def count_text(self, text):
        if not text:
            return 0

        return len(text.split())

    def count_message(self, message):
        return self.count_text(message.content)

    def count_messages(self, messages):
        return sum(self.count_message(message) for message in messages)


class FakeSummaryManager:
    def summarize_messages(self, old_summary, messages):
        return old_summary


def create_orchestrator(llm):

    memory = FakeMemory()
    retriever = FakeRetriever()

    tools = {
        "read_file": FakeTool(
            "read_file", "# API Documentation\n\nGET /health\nPOST /chat"
        ),
        "search_files": FakeTool("search_files", "knowledge/api.md"),
        "list_directory": FakeTool("list_directory", "api.md\narchitecture.md"),
    }

    registry = FakeToolRegistry(tools)

    token_counter = FakeTokenCounter()
    summary_manager = FakeSummaryManager()

    orchestrator = Orchestrator(
        llm_client=llm,
        memory=memory,
        retriever=retriever,
        tool_registory=registry,
        token_counter=token_counter,
        summary_manager=summary_manager,
    )

    return orchestrator, tools


def test_single_tool_execution():

    llm = FakeLLM(
        [
            '{"tool":"read_file","arguments":{"path":"knowledge/api.md"}}',
            '{"tool":null,"arguments":{}}',
        ]
    )

    orchestrator, tools = create_orchestrator(llm)

    response = orchestrator.process_message(
        conversation_id="test-1", role="user", content="Read knowledge/api.md"
    )

    assert response == "Final response"

    assert len(tools["read_file"].calls) == 1

    assert tools["read_file"].calls[0] == {"path": "knowledge/api.md"}


def test_tool_chaining():

    llm = FakeLLM(
        [
            '{"tool":"search_files","arguments":{"query":"api"}}',
            '{"tool":"read_file","arguments":{"path":"knowledge/api.md"}}',
            '{"tool":null,"arguments":{}}',
        ]
    )

    orchestrator, tools = create_orchestrator(llm)

    response = orchestrator.process_message(
        conversation_id="test-chain",
        role="user",
        content="Find the API documentation and summarize it.",
    )

    assert response == "Final response"

    assert tools["search_files"].calls == [{"query": "api"}]

    assert tools["read_file"].calls == [{"path": "knowledge/api.md"}]


def test_no_tool_required():

    llm = FakeLLM(['{"tool":null,"arguments":{}}'])

    orchestrator, tools = create_orchestrator(llm)

    response = orchestrator.process_message(
        conversation_id="test-no-tool", role="user", content="What is FastAPI?"
    )

    assert response == "Final response"

    assert tools["read_file"].calls == []
    assert tools["search_files"].calls == []
    assert tools["list_directory"].calls == []


def test_max_tool_steps():

    llm = FakeLLM(
        [
            '{"tool":"search_files","arguments":{"query":"api"}}',
            '{"tool":"search_files","arguments":{"query":"api"}}',
            '{"tool":"search_files","arguments":{"query":"api"}}',
            '{"tool":"search_files","arguments":{"query":"api"}}',
            '{"tool":"search_files","arguments":{"query":"api"}}',
        ]
    )

    orchestrator, tools = create_orchestrator(llm)

    with pytest.raises(RuntimeError):
        orchestrator.process_message(
            conversation_id="test-limit", role="user", content="Keep searching"
        )
