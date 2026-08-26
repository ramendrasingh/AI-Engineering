from fastapi import APIRouter, HTTPException

from app.health.health_service import HealthService
from app.models.schemas import GenerateRequest, GenerateResponse
from app.orchastrator.orchestrator import Orchestrator


def create_router(orchestrator: Orchestrator) -> APIRouter:
    router = APIRouter()
    health_service = HealthService(orchestrator)

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

    @router.get("/health/live")
    def liveness():
        return health_service.liveness()

    @router.get("/health/ready")
    def health_check() -> dict:
        result, ready = health_service.readyness()

        if ready:
            return result
        else:
            raise HTTPException(status_code=503, detail=result)

    return router
