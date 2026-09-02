import logging

from app.models.schemas import ToolCall, ToolResult
from app.tool.executor import ToolExecutor
from app.tool.registry import ToolRegistry


class FakeTool:
    name = "fake_tool"

    class ArgsSchema:
        @classmethod
        def model_validate(cls, arguments):
            return cls()

        def model_dump(self):
            return {}

    args_schema = ArgsSchema()

    def execute(self, tool_call: ToolCall) -> ToolResult:
        return ToolResult(
            success=True,
            content="success",
        )


class FailingTool:
    name = "failing_tool"

    class ArgsSchema:
        @classmethod
        def model_validate(cls, arguments):

            return cls()

        def model_dump(self):

            return {}

    args_schema = ArgsSchema()

    def execute(self, tool_call: ToolCall) -> ToolResult:

        raise RuntimeError("tool failed")


def test_tool_execution_logs_success(caplog):
    registry = ToolRegistry()
    registry.register(FakeTool())

    executor = ToolExecutor(registry)

    tool_call = ToolCall(
        tool="fake_tool",
        arguments={},
    )

    with caplog.at_level(logging.INFO, logger="AI_Orchestrator"):
        result = executor.execute(tool_call)

    assert result.success is True

    messages = [record.message for record in caplog.records]

    assert any("event=tool_execution_started" in message for message in messages)

    assert any("event=tool_execution_completed" in message for message in messages)

    completed = next(
        message for message in messages if "event=tool_execution_completed" in message
    )

    assert "tool=fake_tool" in completed
    assert "success=True" in completed
    assert "duration_ms=" in completed


def test_tool_execution_logs_failure(caplog):

    registry = ToolRegistry()

    registry.register(FailingTool())

    executor = ToolExecutor(registry)

    tool_call = ToolCall(
        tool="failing_tool",
        arguments={},
    )

    with caplog.at_level(logging.INFO, logger="AI_Orchestrator"):
        try:
            executor.execute(tool_call)

        except RuntimeError:
            pass

    messages = [record.message for record in caplog.records]

    assert any("event=tool_execution_started" in message for message in messages)

    assert any("event=tool_execution_failed" in message for message in messages)

    failed = next(
        message for message in messages if "event=tool_execution_failed" in message
    )

    assert "tool=failing_tool" in failed

    assert "success=False" in failed

    assert "duration_ms=" in failed

    assert "error=RuntimeError" in failed
