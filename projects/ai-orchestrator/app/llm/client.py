import requests
from app.core.config import settings

class OllamaClient:
    """Client for communicating with the local Ollama server."""

    def __init__(self):
        pass

    def generate(self, prompt: str, model_name: str = None) -> str:
        print(f"Generating response for prompt: {prompt} , base url: {settings.OLLAMA_BASE_URL}, model: {settings.MODEL_NAME}")
        session = requests.session()
        try:
            model_name = model_name or settings.MODEL_NAME
            url = f"{settings.OLLAMA_BASE_URL}/api/generate"
            response = session.post(url, 
                                json={
                                    "model": settings.MODEL_NAME,
                                    "prompt": prompt,
                                    "stream": False,
                                    "max_tokens": 100
                                }, timeout=20)
            return response.json()["response"]
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Error generating response."
      