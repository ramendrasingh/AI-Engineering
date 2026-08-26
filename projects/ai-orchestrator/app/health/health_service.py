from app.orchastrator.orchestrator import Orchestrator


class HealthService:
    def __init__(self, oschestrator: Orchestrator):
        self.orchestrator = oschestrator

    def liveness(self) -> dict:
        return {"status": "ok"}

    def readyness(self):
        ollama_ok = self.orchestrator.llm_client.health_check()

        rag_ok = self.orchestrator.retriever is not None

        tool_ok = self.orchestrator.tool_registry is not None

        ready = ollama_ok and rag_ok and tool_ok

        result = {
            "status": "ready" if ready else "not ready",
            "ollama": ollama_ok,
            "rag": rag_ok,
            "tool": tool_ok,
        }

        return result, ready
