# assistant/orchestrator.py

from brain.brain_engine import BrainEngine
from memoria.memoria_manager import MemoriaManager
from memoria.memoria_rag import MemoriaRAG


class JarvisOrchestrator:

    def __init__(self):
        self.memoria = MemoriaManager()
        self.memoria_rag = MemoriaRAG()
        self.brain = BrainEngine(self.memoria, self.memoria_rag)

    def process_text(self, text: str):

        text = (text or "").strip()

        if not text:
            return {
                "ok": False,
                "text": "Não disseste nada."
            }

        result = self.brain.processar(text)

        # normalizar resposta
        if isinstance(result, dict):
            return {
                "ok": True,
                "text": result.get("text", ""),
                "end": result.get("end_conversation", False)
            }

        return {
            "ok": True,
            "text": str(result),
            "end": False
        }