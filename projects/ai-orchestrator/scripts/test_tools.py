from app.tool.list_directory import ListDirectoryTool
from app.tool.read_file import ReadFileTool
from app.tool.registry import ToolRegistry
from app.tool.search_files import SearchFilesTool

workspace_root = "."
tool_registry = ToolRegistry()

tool_registry.register(
    ReadFileTool(workspace_root=workspace_root)  # "." can be the project root.
)

tool_registry.register(
    ListDirectoryTool(workspace_root=workspace_root)  # "." can be the project root.
)

tool_registry.register(
    SearchFilesTool(workspace_root="knowledge")  # "." can be the project root.
)

# test read file tool

tool = tool_registry.get_tool("read_file")

result = tool.execute(path="knowledge/api.md")

print(result.success)

print(result.metadata)

print(result.content[:200])

# Test list directoy tool
tool = tool_registry.get_tool("list_directory")

result = tool.execute(path=".")

print(result.success)

print(result.metadata)

print(result.content[:200])

# test search files tool

tool = tool_registry.get_tool("search_files")

result = tool.execute(query="api")

print(result.success)

print(result.metadata)

print(result.content[:200])
