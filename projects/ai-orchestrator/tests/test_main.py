import app.llm.client as OllamaClient

client = OllamaClient.OllamaClient()
response = client.generate("Explain what an API is.")

print(response)