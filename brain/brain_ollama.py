import requests
from typing import List, Dict

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "mistral-small3.1"   # podes trocar depois

SYSTEM_PROMPT = """
Tu és o Jarvis, um assistente local em português de Portugal.
Falas de forma natural, clara e útil.
És integrado num sistema doméstico com controlo de apps, luzes e ações locais.
Quando o pedido for conversa normal, respondes normalmente.
Quando o pedido parecer uma ação do sistema, deves deixar isso claro na resposta.
Nunca inventes resultados de ações que não foram executadas.
"""

class OllamaBrain:
    def __init__(self, model: str = MODEL_NAME):
        self.model = model
        self.history: List[Dict[str, str]] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    def chat(self, user_text: str) -> str:
        self.history.append({"role": "user", "content": user_text})

        payload = {
            "model": self.model,
            "messages": self.history,
            "stream": False
        }

        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()

            assistant_text = data["message"]["content"].strip()
            self.history.append({"role": "assistant", "content": assistant_text})
            return assistant_text

        except Exception as e:
            return f"Erro ao comunicar com o Ollama: {e}"

    def reset(self):
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]