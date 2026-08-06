import requests
from core.config import settings

class OllamaClient:
    """Client for communicating with the local Ollama server."""

    def __init__(self):
        pass

    def generate(self, prompt: str, model_name: str = None) -> str:
        response = requests.post(f"{settings.OLLAMA_BASE_URL}/api/generate", 
                                json={
                                    "model": settings.MODEL_NAME,
                                    "prompt": prompt,
                                    "stream": False,
                                    "max_tokens": 100
                                })
        return response.json()["response"]