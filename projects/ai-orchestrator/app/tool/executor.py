from app.models.schemas import ToolCall, ToolResult
from app.tool.registry import ToolRegistry


class ToolExecutor:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def execute(self, tool_call: ToolCall) -> ToolResult:

        tool = self.registry.get_tool(tool_call.tool)

        arguments = tool.args_schema.model_validate(tool_call.arguments)

        return tool.execute(
            ToolCall(
                tool=tool_call.tool,
                arguments=arguments.model_dump(),
            )
        )
