
from app.llm.client import OllamaClient

client = OllamaClient()
response = client.generate("Explain what an API is.")

print(response)