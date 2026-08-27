from pathlib import Path

from app.config.config import settings
from app.logger.logger import logger
from app.models.schemas import SearchFilesArguments, ToolCall, ToolResult
from app.tool.base import Tool


class SearchFilesTool(Tool):
    name = "search_files"
    description = (
        "Recursively search the workspace for files matching a filename query."
    )
    args_schema = SearchFilesArguments

    def __init__(
        self,
        workspace_root: str,
        max_result: int,
        excluded_dirs: set[str] | None = None,
    ):
        self.workspace_root = Path(workspace_root).resolve()
        self.excluded_dirs = (
            excluded_dirs
            if excluded_dirs is not None
            else settings.DEFAULT_EXCLUDED_DIRS
        )
        self.max_result = max_result

    def execute(self, tool_call: ToolCall) -> ToolResult:
        logger.info("executing search files Tool")
        query = tool_call.arguments["query"]
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
                if len(matches) >= self.max_result:
                    break

                # Skip excluded directories
                if any(part in self.excluded_dirs for part in path.parts):
                    continue

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

    def validate_arguments(self, arguments: dict) -> None:

        if "query" not in arguments:
            raise ValueError("Missing required argument: query")

        query = arguments["query"]

        if not isinstance(query, str):
            raise ValueError("Argument 'query' must be a string")

        if not query.strip():
            raise ValueError("Argument 'query' cannot be empty")
