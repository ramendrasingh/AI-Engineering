import pytest

from app.models.schemas import ToolCall, ToolResult
from app.tool.base import Tool
from app.tool.list_directory import ListDirectoryTool
from app.tool.read_file import ReadFileTool
from app.tool.registry import ToolRegistry
from app.tool.search_files import SearchFilesTool


class FakeTool(Tool):
    name = "fake_tool"

    description = "Fake tool used for testing."

    def validate_arguments(self, arguments: dict) -> None:

        if "value" not in arguments:
            raise ValueError("Missing required argument: value")

        if not isinstance(arguments["value"], str):
            raise ValueError("value must be a string")

    def execute(self, **kwargs) -> ToolResult:

        return ToolResult(
            success=True,
            content=kwargs["value"],
            metadata={"tool": self.name},
        )


tool_registry = ToolRegistry()
workspace_root = "."

tool_registry.register(
    ReadFileTool(workspace_root=workspace_root)  # "." can be the project root.
)

tool_registry.register(
    ListDirectoryTool(workspace_root=workspace_root)  # "." can be the project root.
)


def test_tool_registry():
    tool = tool_registry.get_tool("read_file")

    assert tool is not None
    assert tool.name == "read_file"


def test_unknown_tool():
    with pytest.raises(KeyError):
        tool = tool_registry.get_tool("xyz")
        assert tool.name == "Tool xyz not found"


def test_register_and_get_tool():
    registry = ToolRegistry()
    tool = FakeTool()
    registry.register(tool)
    result = registry.get_tool("fake_tool")
    assert result is tool


def test_duplicate_tool_registration():
    registry = ToolRegistry()
    registry.register(FakeTool())
    with pytest.raises(ValueError, match="already registered"):
        registry.register(FakeTool())


def test_execute_valid_tool():

    registry = ToolRegistry()
    registry.register(FakeTool())
    toolCall = ToolCall()
    toolCall.tool = "fake_tool"
    toolCall.arguments = {"value": "hello"}
    result = registry.execute(tool_call=toolCall)
    assert result.success is True
    assert result.content == "hello"


def test_execute_unknown_tool():
    registry = ToolRegistry()
    toolCall = ToolCall()
    toolCall.tool = "unknown_tool"
    toolCall.arguments = {}
    with pytest.raises(KeyError, match="not found"):
        registry.execute(tool_call=toolCall)


def test_execute_invalid_arguments():
    registry = ToolRegistry()
    registry.register(FakeTool())
    toolCall = ToolCall()
    toolCall.tool = "fake_tool"
    toolCall.arguments = {}
    with pytest.raises(ValueError, match="Missing required argument"):
        registry.execute(tool_call=toolCall)


def test_execute_wrong_argument_type():
    registry = ToolRegistry()
    registry.register(FakeTool())
    toolCall = ToolCall()
    toolCall.tool = "fake_tool"
    toolCall.arguments = {"value": 123}
    with pytest.raises(ValueError, match="must be a string"):
        registry.execute(tool_call=toolCall)


def test_registry_validates_before_execution():
    registry = ToolRegistry()
    registry.register(FakeTool())
    toolCall = ToolCall()
    toolCall.tool = "fake_tool"
    toolCall.arguments = {}
    with pytest.raises(ValueError, match="Missing required argument"):
        registry.execute(tool_call=toolCall)


def test_search_files_through_registry(tmp_path):

    test_file = tmp_path / "architecture.md"
    test_file.write_text("architecture documentation")

    registry = ToolRegistry()

    tool = SearchFilesTool(
        workspace_root=str(tmp_path),
        max_result=10,
    )

    registry.register(tool)
    toolCall = ToolCall()
    toolCall.tool = "search_files"
    toolCall.arguments = {"query": "architecture"}
    result = registry.execute(tool_call=toolCall)

    assert result.success is True
    assert "architecture.md" in result.content
