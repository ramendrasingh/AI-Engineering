import pytest

from app.logger.logger import logger
from app.models.schemas import ToolCall
from app.tool.executor import ToolExecutor
from app.tool.read_file import ReadFileTool
from app.tool.registry import ToolRegistry


@pytest.fixture
def toolregistry() -> ToolRegistry:
    return ToolRegistry()


def test_execute_read_file(toolregistry):

    read_tool = ReadFileTool(workspace_root=".")
    toolregistry.register(tool=read_tool)
    toolcall = ToolCall(
        tool="read_file",
        arguments={"path": "knowledge/api.md"},
    )
    executor = ToolExecutor(toolregistry)
    result = executor.execute(tool_call=toolcall)
    logger.info(f"result: {result.metadata}")

    assert result.success is True
    assert "healthy" in result.content
