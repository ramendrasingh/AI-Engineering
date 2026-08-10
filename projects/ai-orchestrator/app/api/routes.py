
from fastapi import APIRouter, HTTPException
from requests import post
from app.llm.client import OllamaClient
from app.memory.conversational import ConversationalMemory
from app.orchastrator.Orchestrator import Orchastrator
from app.models.schemas import GenerateResponse, GenerateRequest

router = APIRouter()
client = OllamaClient()
memory = ConversationalMemory()
orchastrator = Orchastrator(llm_client=client, memory=memory)

 
@router.get("/health")
def health_check() -> bool:
        return client.health_check()

@router.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest) -> GenerateResponse: 
        try:
            if not request.prompt:
                raise HTTPException(status_code=400, detail="Prompt is required.")

            response = orchastrator.process_message(conversation_id=request.user_id, role="user", content=request.prompt)
            return GenerateResponse(response=response)
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))