    
from pydantic import BaseModel
import os

class Settings():
    OLLAMA_BASE_URL = "http://localhost:11434"
    MODEL_NAME = "gemma3:4b"

settings = Settings()

SYSTEM_PROMPT = "You are a helpful assistant."
MAX_HISTORY_MESSAGES = 10
