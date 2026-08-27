from app.models.schemas import ToolCall, ToolResult
from app.tool.base import Tool


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool):
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' already registered")
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found")
        return self._tools[name]

    def list_tools(self):
        return list(self._tools.values())

    def execute(self, tool_call: ToolCall) -> ToolResult:
        tool = self.get_tool(tool_call.tool)
        tool.validate_arguments(tool_call.arguments)
        return tool.execute(tool_call=tool_call)

    def get_tool_schema(self, name: str) -> dict:
        tool = self.get_tool(name)
        return {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.args_schema.model_json_schema(),
        }

    def get_all_tool_schemas(self) -> list[dict]:
        return [self.get_tool_schema(tool.name) for tool in self._tools.values()]
