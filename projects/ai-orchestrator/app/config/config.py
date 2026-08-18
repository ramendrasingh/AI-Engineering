class Settings:
    OLLAMA_BASE_URL = "http://localhost:11434"
    MODEL_NAME = "gemma3:4b"
    EMBEDDING_MODEL = "nomic-embed-text"
    SYSTEM_PROMPT = "You are a helpful AI assistant."
    MAX_HISTORY_MESSAGES = 10
    MAX_TOKEN_COUNT = 4096
    OUTPUT_RESERVE_TOKENS = 512
    SUMMARY_TRIGGER_MESSAGES = 10
    SUMMARY_RETAIN_MESSAGES = 5
    RAG_TOP_K = 3
    RAG_MIN_SIMILARITY = 0.60
    MAX_TOOL_STEPS = 5
    MAX_SEARCH_RESULTS = 50
    DEFAULT_EXCLUDED_DIRS = {
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

    SUMMARY_PROMPT = """
    You are creating long-term memory for an AI assistant.

    Summarize the following conversation for future interactions.

    Preserve:

    - user goals,
    - important decisions,
    - technical constraints,
    - project status,
    - unresolved questions,
    - names,
    - preferences.
    - event occurence with dates

    Do not include greetings, small talk, or repetitive acknowledgements.

    Keep the summary under 150 words.
    use Existing Summary and Conversation section to generate the summary of whole conversation
 
    Existing Summary:
    {existing_summary}

    Conversation: 

    {conversation}

    """

    TOOL_SELECTION_PROMPT = """
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

1. Use read_file when the user asks to read, open, inspect, show, display, or summarize a specific file.

2. Use list_directory when the user asks to list or browse a directory.

3. Use search_files when the user asks to find or locate a file.

4. search_files query MUST be a short filename keyword, NOT a natural-language sentence.

5. If a previous tool result already provides the required information, return no tool.

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


settings = Settings()
