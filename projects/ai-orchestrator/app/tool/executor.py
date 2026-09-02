from app.logger.logger import log_event
from app.models.schemas import ToolCall, ToolResult
from app.observability.timer import Timer
from app.tool.registry import ToolRegistry


class ToolExecutor:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def execute(self, tool_call: ToolCall) -> ToolResult:
        log_event(
            "tool_execution_started",
            tool=tool_call.tool,
        )

        try:
            with Timer("tool_execution") as timer:
                tool = self.registry.get_tool(tool_call.tool)

                arguments = tool.args_schema.model_validate(tool_call.arguments)

                result = tool.execute(
                    ToolCall(
                        tool=tool_call.tool,
                        arguments=arguments.model_dump(),
                    )
                )

            duration_ms = timer.elapsed_ms

            log_event(
                "tool_execution_completed",
                tool=tool_call.tool,
                success=result.success,
                duration_ms=f"{duration_ms:.2f}",
            )

            return result

        except Exception as e:
            duration_ms = timer.elapsed_ms

            log_event(
                "tool_execution_failed",
                tool=tool_call.tool,
                success=False,
                duration_ms=f"{duration_ms:.2f}",
                error=type(e).__name__,
            )

            raise
