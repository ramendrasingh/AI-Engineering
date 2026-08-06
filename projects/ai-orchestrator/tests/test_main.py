import app.llm.clients as OllamaClient

client = OllamaClient.OllamaClient()
response = client.generate("Explain what an API is.")

print(response)