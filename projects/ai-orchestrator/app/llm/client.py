import requests
from app.core.config import settings

class OllamaClient:
    """Client for communicating with the local Ollama server."""

    def __init__(self):
        self.session = requests.session()

    def health_check(self) -> bool:
        """Check if the Ollama server is reachable."""
        try:
            url = f"{settings.OLLAMA_BASE_URL}/api/health"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Health check failed: {e}")
            return False

    def generate(self, prompt: str, model_name: str = None) -> str:
        print(f"Generating response for prompt: {prompt} , base url: {settings.OLLAMA_BASE_URL}, model: {settings.MODEL_NAME}")
        try:
            model_name = model_name or settings.MODEL_NAME
            url = f"{settings.OLLAMA_BASE_URL}/api/generate"
            response = self.session.post(url, 
                                json={
                                    "model": settings.MODEL_NAME,
                                    "prompt": prompt,
                                    "stream": False
                                }, timeout=20)
            response.raise_for_status()
            return response.json()["response"]
        except requests.RequestException as e:
            print(f"Error generating response: {e}")
            raise RuntimeError(f"Failed to communicate with Ollama: {e}")