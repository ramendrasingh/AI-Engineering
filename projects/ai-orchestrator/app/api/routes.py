
from dotenv.cli import get
from fastapi import FastAPI, HTTPException
from requests import post
from app.core.config import settings
from app.llm.client import OllamaClient
from app.models.schemas import GenerateResponse, GenerateRequest

class Router():
 
    @get("/health")
    def health_check(self):
        return {
                 "status": "healthy",
                 "model": settings.MODEL_NAME
                }

    @post("/generate", response_model=GenerateResponse)
    def generate(self, request: GenerateRequest) -> GenerateResponse: 
        client = OllamaClient()
        try:
            response = client.generate(request.prompt)
            return GenerateResponse(response=response)
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))