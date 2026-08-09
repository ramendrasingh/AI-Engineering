
from fastapi import FastAPI

from app.api.routes import router


app = FastAPI(
    title="AI Orchastrator",
    description="AI service to orchestrate multiple AI models and provide a unified interface for generating responses.",
    version="1.0.0"
)

app.include_router(router=router)