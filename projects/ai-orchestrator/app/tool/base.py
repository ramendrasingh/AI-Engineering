from abc import ABC, abstractmethod

from app.models.schemas import ToolResult


class Tool(ABC):
    name: str
    description: str

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        pass
