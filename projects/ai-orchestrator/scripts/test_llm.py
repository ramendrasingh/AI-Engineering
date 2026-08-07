
import app
from app.llm.client import OllamaClient
from app.api.routes import Router
from app.models.schemas import GenerateRequest, GenerateRequest

router = Router()


response = router.generate(GenerateRequest(prompt="Hello, how are you?"))

print(response.response)