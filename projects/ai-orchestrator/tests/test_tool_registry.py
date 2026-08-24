import pytest

from app.tool.list_directory import ListDirectoryTool
from app.tool.read_file import ReadFileTool
from app.tool.registry import ToolRegistry

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
