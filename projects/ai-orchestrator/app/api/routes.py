
from fastapi import APIRouter, HTTPException
from requests import post
from app.core.config import settings
from app.llm.client import OllamaClient
from app.models.schemas import GenerateResponse, GenerateRequest

router = APIRouter()
client = OllamaClient()
 
@router.get("/health")
def health_check() -> bool:
        return client.health_check()

@router.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest) -> GenerateResponse: 
  
        try:
            if not request.prompt:
                raise HTTPException(status_code=400, detail="Prompt is required.")

            response = client.generate(request.prompt)
            return GenerateResponse(response=response)
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))