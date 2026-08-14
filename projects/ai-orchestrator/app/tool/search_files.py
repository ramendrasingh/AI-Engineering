from pathlib import Path

from app.logger.logger import logger
from app.models.schemas import ToolResult
from app.tool.base import Tool


class SearchFilesTool(Tool):
    name = "search_files"
    description = (
        "Recursively search the workspace for files matching a filename query."
    )

    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root).resolve()

    def execute(self, query: str) -> ToolResult:
        logger.info("executing search files Tool")
        try:
            query = query.lower().strip()

            if not query:
                return ToolResult(
                    success=False,
                    content="",
                    error="Query cannot be empty",
                )

            matches = []

            for path in self.workspace_root.rglob("*"):
                if path.is_file() and query in path.name.lower():
                    matches.append(str(path.relative_to(self.workspace_root)))

            matches.sort()

            logger.info("List Directory File Tool return the content")
            return ToolResult(
                success=True,
                content="\n".join(matches),
                metadata={
                    "query": query,
                    "match_count": len(matches),
                    "matches": matches,
                    "tool": self.name,
                },
            )

        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=str(e),
            )
