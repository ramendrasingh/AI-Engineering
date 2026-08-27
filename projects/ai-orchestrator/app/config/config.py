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

Decide whether the user's request requires a file-system tool.

Available tools:

1. read_file(path)

   Use when the user explicitly asks to read, open, show, inspect,

   or summarize a specific file.

   The path must be workspace-relative.

   Knowledge documents are under the "knowledge/" directory.

2. list_directory(path)

   Use when the user asks to list or browse a directory.

3. search_files(query)

   Use when the user explicitly asks to find, locate, or search for files.

   IMPORTANT:

   query is matched against file/path names.

   Use a SHORT filename keyword, not the user's full sentence.

Rules:

- Normal conversation → no tool.

- Conceptual questions → no tool.

- Mentioning a technical term does NOT mean search.

- If uncertain → no tool.

- Return ONLY valid JSON.

Examples:

"My name is Ram"

→ {"tool":null,"arguments":{}}

"What is RAG?"

→ {"tool":null,"arguments":{}}

"Explain embeddings"

→ {"tool":null,"arguments":{}}

"Find the API documentation"

→ {"tool":"search_files","arguments":{"query":"api"}}

"Locate the embedding documentation"

→ {"tool":"search_files","arguments":{"query":"embedding"}}

"Read knowledge/api.md"

→ {"tool":"read_file","arguments":{"path":"knowledge/api.md"}}

"Show me architecture.md"

→ {"tool":"read_file","arguments":{"path":"knowledge/architecture.md"}}

"List the knowledge directory"

→ {"tool":"list_directory","arguments":{"path":"knowledge"}}

Return ONLY:

{"tool":null,"arguments":{}}

or

{"tool":"<tool_name>","arguments":{...}}

No markdown.
No explanation.
"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
