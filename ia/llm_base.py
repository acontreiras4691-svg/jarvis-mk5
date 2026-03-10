# ==================================================
# 🔥 LLM BASE MK4 - PERFORMANCE MODE
# ==================================================

import requests
import json

OLLAMA_URL = "http://localhost:11434/api/chat"

session = requests.Session()

DEFAULT_OPTIONS = {
    "temperature": 0.2,
    "top_p": 0.85,
    "repeat_penalty": 1.15,
    "num_predict": 160
}


# ==================================================
# 🔹 CHAMADA NORMAL
# ==================================================

def chamar_modelo(
    modelo,
    mensagens,
    temperature=None,
    num_predict=None
):

    try:

        options = DEFAULT_OPTIONS.copy()

        if temperature is not None:
            options["temperature"] = temperature

        if num_predict is not None:
            options["num_predict"] = num_predict


        response = session.post(
            OLLAMA_URL,
            json={
                "model": modelo,
                "messages": mensagens,
                "stream": False,
                "options": options
            },
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        return data["message"]["content"].strip()

    except Exception:

        return None


# ==================================================
# 🔥 STREAMING OTIMIZADO
# ==================================================

def chamar_modelo_stream(
    modelo,
    mensagens,
    on_token=None,
    temperature=None,
    num_predict=None
):

    try:

        options = DEFAULT_OPTIONS.copy()

        if temperature is not None:
            options["temperature"] = temperature

        if num_predict is not None:
            options["num_predict"] = num_predict


        response = session.post(
            OLLAMA_URL,
            json={
                "model": modelo,
                "messages": mensagens,
                "stream": True,
                "options": options
            },
            stream=True,
            timeout=40
        )

        response.raise_for_status()

        resposta_final = ""

        for linha in response.iter_lines(chunk_size=512):

            if not linha:
                continue

            try:

                chunk = json.loads(linha.decode("utf-8"))

                if chunk.get("done", False):
                    break

                if "message" in chunk:

                    token = chunk["message"]["content"]

                    resposta_final += token

                    if on_token:
                        on_token(token)

            except Exception:
                continue


        return resposta_final.strip()


    except Exception:

        return None