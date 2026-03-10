import requests
import re
from config.configuracoes import (
    OLLAMA_BASE_URL,
    OLLAMA_GENERATE_ENDPOINT,
    TIMEOUT_OLLAMA
)

MODELO_CLASSIFICADOR = "phi3:mini"


def classificar_prioridade(texto: str) -> int:
    """
    Classifica a importância de um texto de 0 a 4.

    0 = irrelevante
    1 = leve
    2 = normal
    3 = importante
    4 = crítico
    """

    if not texto or len(texto.strip()) < 3:
        return 0

    prompt = f"""
Classifica a importância da seguinte frase de 0 a 4.

Responde apenas com um único número.

Frase:
{texto}
"""

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}{OLLAMA_GENERATE_ENDPOINT}",
            json={
                "model": MODELO_CLASSIFICADOR,
                "prompt": prompt,
                "stream": False,
                "temperature": 0
            },
            timeout=TIMEOUT_OLLAMA
        )

        if response.status_code != 200:
            return 1

        resposta = response.json().get("response", "").strip()

        match = re.search(r"\d", resposta)

        if match:
            prioridade = int(match.group())
        else:
            prioridade = 1

        if prioridade < 0 or prioridade > 4:
            prioridade = 1

        return prioridade

    except Exception:
        return 1