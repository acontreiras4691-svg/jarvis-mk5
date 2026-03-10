import requests
import re
from config.configuracoes import (
    MODELO_LLM,
    OLLAMA_BASE_URL,
    OLLAMA_CHAT_ENDPOINT,
    TEMPERATURA,
    TIMEOUT_OLLAMA
)

SYSTEM_PROMPT = """
Tu és Jarvis, assistente pessoal ultra inteligente inspirado no estilo de Tony Stark.

Regras:
- Fala sempre em português europeu.
- Trata o utilizador por "Dudu".
- Confiante, sofisticado, ligeiramente sarcástico.
- Nunca infantil.
- Máximo 4 frases.
- Nunca digas que és um modelo de linguagem.
- Responde sempre de forma elegante e direta.
"""

def limpar_resposta(texto: str) -> str:
    texto = re.sub(r"<.*?>", "", texto)
    return texto.strip()


def gerar_resposta(mensagem: str, contexto_longo: str = "", historico_curto=None) -> str:
    try:

        mensagens = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

        # 🔹 Contexto longo (RAG)
        if contexto_longo:
            mensagens.append({
                "role": "system",
                "content": f"Notas relevantes:\n{contexto_longo}"
            })

        # 🔹 Histórico curto (memória recente)
        if historico_curto:
            mensagens.extend(historico_curto)

        mensagens.append({
            "role": "user",
            "content": mensagem
        })

        response = requests.post(
            f"{OLLAMA_BASE_URL}{OLLAMA_CHAT_ENDPOINT}",
            json={
                "model": MODELO_LLM,
                "messages": mensagens,
                "temperature": TEMPERATURA,
                "stream": False
            },
            timeout=TIMEOUT_OLLAMA
        )

        if response.status_code != 200:
            return "Algo falhou. Irritantemente."

        resposta = response.json()["message"]["content"]
        resposta = limpar_resposta(resposta)

        if not resposta:
            return "Curioso… fiquei momentaneamente sem palavras."

        return resposta

    except Exception:
        return "Tive um contratempo técnico. Nada que comprometa a minha superioridade."