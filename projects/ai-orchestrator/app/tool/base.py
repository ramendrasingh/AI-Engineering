from abc import ABC, abstractmethod

from pydantic import BaseModel

from app.models.schemas import ToolCall, ToolResult


class Tool(ABC):
    name: str
    description: str
    args_schema: type[BaseModel]

    @abstractmethod
    def execute(self, tool_call: ToolCall) -> ToolResult:
        pass

    @abstractmethod
    def validate_arguments(self, arguments: dict) -> None:
        """
        Validate tool arguments.
        Raises:
            ValueError: if arguments are invalid.
        """

    def normalize_arguments(self, arguments: dict) -> dict:
        """
        Normalize tool arguments before execution.
        """
        return arguments
