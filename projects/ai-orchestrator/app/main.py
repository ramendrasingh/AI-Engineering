from fastapi import FastAPI

from app.api.routes import create_router
from app.factory.orchestrator_factory import create_orchestrator


def create_app() -> FastAPI:

    orchestrator = create_orchestrator()

    app = FastAPI(
        title="AI Orchestrator",
        description="AI service to orchestrate multiple AI models and provide a unified interface.",
        version="1.0.0",
    )

    app.include_router(create_router(orchestrator))

    return app


app = create_app()
