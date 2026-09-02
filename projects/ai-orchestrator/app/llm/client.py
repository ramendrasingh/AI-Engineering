import requests

from app.config.config import settings
from app.logger.logger import logger
from app.models.schemas import ChatMessage
from app.observability.timer import Timer


class OllamaClient:
    """Client for communicating with the local Ollama server."""

    def __init__(self):
        self.session = requests.session()

    def health_check(self) -> bool:
        """Check the health of the Ollama server."""
        try:
            url = f"{settings.OLLAMA_BASE_URL}/api/tags"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            logger.error(f"Health check failed: {e}")
            return False

    def generate(self, prompt: str, json_format: bool = False) -> str:
        logger.info(
            f"Generating response for prompt: {prompt} , base url: {settings.OLLAMA_BASE_URL}, model: {settings.MODEL_NAME}"
        )
        model_name = settings.MODEL_NAME
        url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        options = {}

        if json_format:
            options = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "format": "json",
            }
        else:
            options = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
            }

        try:
            response = self.session.post(
                url,
                json=options,
                timeout=120,
            )
            response.raise_for_status()
            return response.json()["response"]
        except requests.RequestException as e:
            logger.error(f"Error generating response: {e}")
            raise RuntimeError(f"Failed to communicate with Ollama: {e}")

    @Timer.timed("llm_call")
    def chat(self, messages) -> ChatMessage:
        logger.info(
            f"Generating response for prompt:, base url: {settings.OLLAMA_BASE_URL}, model: {settings.MODEL_NAME}"
        )
        try:
            model_name = settings.MODEL_NAME
            url = f"{settings.OLLAMA_BASE_URL}/api/chat"
            response = self.session.post(
                url,
                json={"model": model_name, "messages": messages, "stream": False},
                timeout=20,
            )
            response.raise_for_status()

            data = response.json()
            logger.info("Ollama chat completed successfully")
            role, content = data["message"]["role"], data["message"]["content"]
            return ChatMessage(role=role, content=content)
        except requests.RequestException as e:
            logger.error(f"Error generating response: {e}")
            raise RuntimeError(f"Failed to communicate with Ollama: {e}")
