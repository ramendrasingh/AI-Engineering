from pathlib import Path

from app.logger.logger import logger
from app.models.schemas import ToolResult
from app.tool.base import Tool


class ListDirectoryTool(Tool):
    name = "list_directory"
    description = "List files and folders inside a directory within the workspace."

    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root).resolve()

    def execute(self, path: str = ".") -> ToolResult:
        logger.info("executing List Directory Tool")
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

            if not target.is_dir():
                return ToolResult(
                    success=False,
                    content="",
                    error="Path is not a directory",
                )

            entries = []
            for entry in sorted(target.iterdir()):
                if entry.is_dir():
                    entries.append(f"{entry.name}/")
                else:
                    entries.append(entry.name)

            logger.info("List Directory File Tool return the content")
            return ToolResult(
                success=True,
                content="\n".join(entries),
                metadata={
                    "path": str(target.relative_to(self.workspace_root)),
                    "entry_count": len(entries),
                    "entries": entries,
                    "tool": self.name,
                },
            )

        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=str(e),
            )
