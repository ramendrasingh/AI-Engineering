from pathlib import Path

from app.logger.logger import logger
from app.models.schemas import ReadFileArguments, ToolCall, ToolResult
from app.tool.base import Tool


class ReadFileTool(Tool):
    name = "read_file"
    description = "Read the contents of a file inside the workspace."
    args_schema = ReadFileArguments

    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root).resolve()

    def execute(self, tool_call: ToolCall) -> ToolResult:
        logger.info("executing Read File Tool")
        path = tool_call.arguments["path"]
        try:
            target = (self.workspace_root / path).resolve()

            if not str(target).startswith(str(self.workspace_root)):
                return ToolResult(
                    success=False,
                    content="",
                    error="Path is outside the workspace",
                )

            if not target.exists():
                return ToolResult(
                    success=False,
                    content="",
                    error="File does not exist",
                )

            if target.is_dir():
                return ToolResult(
                    success=False,
                    content="",
                    error="Path is a directory",
                )

            text = target.read_text(encoding="utf-8")
            logger.info("Read File Tool return the content")
            return ToolResult(
                success=True,
                content=text,
                metadata={
                    "path": str(target.relative_to(self.workspace_root)),
                    "size_bytes": target.stat().st_size,
                    "tool": self.name,
                },
            )

        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=str(e),
            )

    def validate_arguments(self, arguments: dict) -> None:
        if "path" not in arguments:
            raise ValueError("Missing required argument: path")

        path = arguments["path"]

        if not isinstance(path, str):
            raise ValueError("Argument 'path' must be a string")

        if not path.strip():
            raise ValueError("Argument 'path' cannot be empty")
