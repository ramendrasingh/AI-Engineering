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

    Available tools:
    1. read_file(path)
    Read the contents of a file.

    2. list_directory(path)
    List files and folders in a directory.

    3. search_files(query)
    Search recursively for files by filename.

    Rules:
    - If the user asks to read, open, show, display, or inspect a file, use read_file.
    - Otherwise answer directly.
    - Return ONLY valid JSON.

    Examples:

    User: Read knowledge/api.md
    Response:
    {"tool":"read_file","arguments":{"path":"knowledge/api.md"}}

    User: What is FastAPI?
    Response:
    {"tool":null,"arguments":{}}

    User: Show README.md
    Response:
    {"tool":"read_file","arguments":{"path":"README.md"}}
    
    User: List the knowledge folder
    {"tool":"list_directory","arguments":{"path":"knowledge"}}

    User: Find API documentation
    {"tool":"search_files","arguments":{"query":"api"}}

    Return ONLY a valid JSON object. Do NOT wrap your response in markdown code blocks like ```json ... ```. Your output must begin directly with { and end directly with }.

    User request:
    """


settings = Settings()
