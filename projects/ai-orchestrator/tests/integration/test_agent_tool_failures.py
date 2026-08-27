import pytest

from app.config.config import settings
from app.models.schemas import ToolCall
from app.tool.executor import ToolExecutor
from app.tool.list_directory import ListDirectoryTool
from app.tool.read_file import ReadFileTool
from app.tool.registry import ToolRegistry
from app.tool.search_files import SearchFilesTool


@pytest.fixture
def tool_registry() -> ToolRegistry:
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


def test_read_nonexistent_file(tool_registry):
    tool_call = ToolCall(
        tool="read_file",
        arguments={"path": "knowledge/does-not-exist.md"},
    )

    executor = ToolExecutor(tool_registry)

    result = executor.execute(tool_call)

    assert result.success is False
    assert result.error == "File does not exist"


def test_read_file_outside_workspace(tool_registry):
    tool_call = ToolCall(
        tool="read_file",
        arguments={"path": "../../secret.txt"},
    )

    executor = ToolExecutor(tool_registry)

    result = executor.execute(tool_call)

    assert result.success is False
    assert result.error == "Path is outside the workspace"


def test_list_nonexistent_directory(tool_registry):
    tool_call = ToolCall(
        tool="list_directory",
        arguments={"path": "knowledge/does-not-exist"},
    )

    executor = ToolExecutor(tool_registry)

    result = executor.execute(tool_call)

    assert result.success is False
    assert result.error == "File does not exist"
