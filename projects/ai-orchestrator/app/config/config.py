    
from pydantic import BaseModel
import os

class Settings():
    OLLAMA_BASE_URL = "http://localhost:11434"
    MODEL_NAME = "gemma3:4b"

settings = Settings()

SYSTEM_PROMPT = "You are a helpful AI assistant."
MAX_HISTORY_MESSAGES = 10
MAX_TOKEN_COUNT = 4096
OUTPUT_RESERVE_TOKENS = 512
SUMMARY_TRIGGER_MESSAGES = 10
SUMMARY_RETAIN_MESSAGES = 5

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
