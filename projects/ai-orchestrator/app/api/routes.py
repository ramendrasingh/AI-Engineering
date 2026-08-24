from fastapi import APIRouter, HTTPException

from app.models.schemas import GenerateRequest, GenerateResponse
from app.orchastrator.orchestrator import Orchestrator


def create_router(orchestrator: Orchestrator) -> APIRouter:
    router = APIRouter()

    @router.post("/generate", response_model=GenerateResponse)
    def generate(request: GenerateRequest) -> GenerateResponse:
        try:
            if not request.prompt:
                raise HTTPException(status_code=400, detail="Prompt is required.")

            response = orchestrator.process_message(
                conversation_id=request.user_id, role="user", content=request.prompt
            )
            return GenerateResponse(response=response)
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/chat", response_model=GenerateResponse)
    def chat(request: GenerateRequest) -> GenerateResponse:
        try:
            if not request.prompt:
                raise HTTPException(status_code=400, detail="Prompt is required.")

            response = orchestrator.process_message(
                conversation_id=request.user_id, role="user", content=request.prompt
            )
            return GenerateResponse(response=response)
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/health")
    def health_check() -> dict:
        healthy = orchestrator.llm_client.health_check()

        if healthy:
            return {"status": "healthy", "ollama": "healthy", "model": "gemma3:4b"}
        else:
            return {"status": "Not Running", "ollama": "Not Working", "model": ""}

    return router
