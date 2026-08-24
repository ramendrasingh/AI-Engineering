from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ---------------------------------------------------------
    # Application
    # ---------------------------------------------------------

    APP_NAME: str = "AI Orchestrator"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    # ---------------------------------------------------------
    # LLM
    # ---------------------------------------------------------

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    MODEL_NAME: str = "gemma3:4b"

    # ---------------------------------------------------------
    # Workspace
    # ---------------------------------------------------------

    WORKSPACE_ROOT: str = "."
    KNOWLEDGE_PATH: str = "knowledge"

    # ---------------------------------------------------------
    # Embeddings / RAG
    # ---------------------------------------------------------

    EMBEDDING_MODEL: str = "nomic-embed-text"

    RAG_TOP_K: int = 3
    RAG_MIN_SIMILARITY: float = 0.60

    # ---------------------------------------------------------
    # Conversation / Memory
    # ---------------------------------------------------------

    MAX_HISTORY_MESSAGES: int = 10

    MAX_TOKEN_COUNT: int = 4096
    OUTPUT_RESERVE_TOKENS: int = 512

    SUMMARY_TRIGGER_MESSAGES: int = 10
    SUMMARY_RETAIN_MESSAGES: int = 5

    # ---------------------------------------------------------
    # Tools
    # ---------------------------------------------------------

    MAX_TOOL_STEPS: int = 5
    MAX_SEARCH_RESULTS: int = 50

    DEFAULT_EXCLUDED_DIRS: set[str] = {
        ".venv",
        "venv",
        ".git",
        "__pycache__",
        "node_modules",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "build",
        "dist",
    }

    # ---------------------------------------------------------
    # Prompts
    # ---------------------------------------------------------

    SYSTEM_PROMPT: str = "You are a helpful AI assistant."

    SUMMARY_PROMPT: str = """
You are creating long-term memory for an AI assistant.

Summarize the following conversation for future interactions.

Preserve:

- user goals,
- important decisions,
- technical constraints,
- project status,
- unresolved questions,
- names,
- preferences,
- event occurrence with dates.

Do not include greetings, small talk, or repetitive acknowledgements.

Keep the summary under 150 words.

Use Existing Summary and Conversation sections
to generate the summary of the whole conversation.

Existing Summary:
{existing_summary}

Conversation:

{conversation}
"""

    TOOL_SELECTION_PROMPT: str = """
You are a tool-selection engine.

Your ONLY job is to decide the NEXT tool action.

Available tools:

1. read_file
   argument: path

2. list_directory
   argument: path

3. search_files
   argument: query

Rules:

1. Use read_file when the user asks to read, open, inspect, show,
   display, or summarize a specific file.

2. Use list_directory when the user asks to list or browse a directory.

3. Use search_files when the user asks to find or locate a file.

4. search_files query MUST be a short filename keyword,
   NOT a natural-language sentence.

5. If a previous tool result already provides the required information,
   return no tool.

6. If no tool is required, return:
{"tool":null,"arguments":{}}

7. Return ONLY valid JSON.

8. Never return explanations, markdown, or additional text.

Examples:

Find the API documentation
{"tool":"search_files","arguments":{"query":"api"}}

Find architecture documentation
{"tool":"search_files","arguments":{"query":"architecture"}}

Read knowledge/api.md
{"tool":"read_file","arguments":{"path":"knowledge/api.md"}}

List the knowledge directory
{"tool":"list_directory","arguments":{"path":"knowledge"}}

What is FastAPI?
{"tool":null,"arguments":{}}
"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
