from unittest.mock import Mock

from app.models.schemas import ChatMessage
from app.orchastrator.orchestrator import Orchestrator
from app.tool.executor import ToolExecutor
from app.tool.read_file import ReadFileTool
from app.tool.registry import ToolRegistry
from app.tool.search_files import SearchFilesTool


class FakeLLM:
    def __init__(self):
        self.generate_calls = []
        self.chat_calls = []
        self.generate_count = 0

    def generate(self, prompt, json_mode=False):

        self.generate_calls.append(prompt)
        self.generate_count += 1

        if self.generate_count == 1:
            return '{"tool":"read_file","arguments":{"path":"knowledge/api.md"}}'

        return '{"tool":null,"arguments":{}}'

    def chat(self, messages):

        self.chat_calls.append(messages)

        return ChatMessage(
            role="assistant",
            content="The API documentation contains the health endpoint.",
        )


def test_agent_read_file():

    registry = ToolRegistry()

    registry.register(ReadFileTool(workspace_root="."))

    executor = ToolExecutor(registry)

    llm = FakeLLM()
    memory = Mock()
    retriever = Mock()
    token_counter = Mock()
    summary_manager = Mock()

    # No existing conversation

    memory.get_conversation.return_value = []

    # Token counter should not interfere with this test

    token_counter.count_text.return_value = 0

    token_counter.count_message.return_value = 0

    token_counter.count_messages.return_value = 0

    orchestrator = Orchestrator(
        llm_client=llm,
        memory=memory,
        retriever=retriever,
        token_counter=token_counter,
        summary_manager=summary_manager,
        tool_executor=executor,
    )

    response = orchestrator.process_message(
        conversation_id="test-conversation",
        role="user",
        content="Read knowledge/api.md",
    )

    assert response == ("The API documentation contains the health endpoint.")

    assert len(llm.generate_calls) >= 1

    assert len(llm.chat_calls) == 1

    memory.add_message.assert_called()


def test_agent_multi_step_tool_loop():

    registry = ToolRegistry()

    registry.register(ReadFileTool(workspace_root="."))

    registry.register(
        SearchFilesTool(
            workspace_root=".",
            max_result=50,
        )
    )

    executor = ToolExecutor(registry)

    class MultiStepFakeLLM:
        def __init__(self):
            self.generate_calls = []
            self.chat_calls = []
            self.generate_count = 0

        def generate(self, prompt, json_mode=False):

            self.generate_calls.append(prompt)
            self.generate_count += 1

            # Step 1 → search
            if self.generate_count == 1:
                return '{"tool":"search_files","arguments":{"query":"architecture"}}'

            # Step 2 → read discovered file
            if self.generate_count == 2:
                return (
                    '{"tool":"read_file",'
                    '"arguments":{"path":"knowledge/architecture.md"}}'
                )

            # Step 3 → no more tools
            return '{"tool":null,"arguments":{}}'

        def chat(self, messages):

            self.chat_calls.append(messages)

            return ChatMessage(
                role="assistant",
                content=(
                    "The architecture documentation describes "
                    "the AI orchestrator architecture."
                ),
            )

    llm = MultiStepFakeLLM()

    memory = Mock()
    retriever = Mock()
    token_counter = Mock()
    summary_manager = Mock()

    memory.get_conversation.return_value = []

    token_counter.count_text.return_value = 0
    token_counter.count_message.return_value = 0
    token_counter.count_messages.return_value = 0

    orchestrator = Orchestrator(
        llm_client=llm,
        memory=memory,
        retriever=retriever,
        tool_executor=executor,
        token_counter=token_counter,
        summary_manager=summary_manager,
    )

    # ---------------------------------------------------------
    # Execute
    # ---------------------------------------------------------

    response = orchestrator.process_message(
        conversation_id="multi-step-test",
        role="user",
        content="Find the architecture documentation and explain it.",
    )

    # ---------------------------------------------------------
    # Assertions
    # ---------------------------------------------------------

    assert response == (
        "The architecture documentation describes the AI orchestrator architecture."
    )

    # Three tool-selection decisions:
    #
    # 1. search_files
    # 2. read_file
    # 3. no more tools
    #
    assert len(llm.generate_calls) == 3

    # Final response generation
    assert len(llm.chat_calls) == 1

    # Conversation persisted
    assert memory.add_message.called


def test_agent_max_tool_steps():

    registry = ToolRegistry()

    registry.register(
        SearchFilesTool(
            workspace_root=".",
            max_result=50,
        )
    )

    executor = ToolExecutor(registry)

    class InfiniteToolFakeLLM:
        def __init__(self):
            self.generate_calls = []

        def generate(self, prompt, json_mode=False):

            self.generate_calls.append(prompt)

            # Always request another tool.
            return '{"tool":"search_files","arguments":{"query":"architecture"}}'

        def chat(self, messages):
            raise AssertionError("Final LLM response should never be generated")

    llm = InfiniteToolFakeLLM()

    memory = Mock()
    retriever = Mock()
    token_counter = Mock()
    summary_manager = Mock()

    memory.get_conversation.return_value = []

    token_counter.count_text.return_value = 0
    token_counter.count_message.return_value = 0
    token_counter.count_messages.return_value = 0

    orchestrator = Orchestrator(
        llm_client=llm,
        memory=memory,
        retriever=retriever,
        tool_executor=executor,
        token_counter=token_counter,
        summary_manager=summary_manager,
    )

    try:
        orchestrator.process_message(
            conversation_id="max-step-test",
            role="user",
            content="Keep searching for architecture",
        )

        assert False, "Expected maximum tool steps exception"

    except RuntimeError as error:
        assert str(error) == "Maximum tool steps exceeded: 5"

    # Initial tool selection + 5 loop decisions
    assert len(llm.generate_calls) == 6
