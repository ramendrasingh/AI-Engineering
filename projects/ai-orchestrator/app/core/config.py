    
from pydantic import BaseModel

class Settings(BaseModel):
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    MODEL_NAME: str = "gemma3:4b"

settings = Settings()
