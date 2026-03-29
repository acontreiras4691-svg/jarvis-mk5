# ==================================================
# 🧠 JARVIS SERVER (LOCAL AI)
# ==================================================

from flask import Flask, request, jsonify
import requests
import time

app = Flask(__name__)

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

OLLAMA_URL = "http://localhost:11434/api/generate"

# modelos
MODELO_RAPIDO = "qwen3:4b"
MODELO_INTELIGENTE = "qwen3:8b"

TIMEOUT_OLLAMA = 60


# --------------------------------------------------
# ESCOLHA DE MODELO
# --------------------------------------------------

def escolher_modelo(texto: str):
    texto = texto.lower()

    # comandos simples → modelo rápido
    if len(texto) < 40:
        return MODELO_RAPIDO

    if any(p in texto for p in ["liga", "desliga", "abre", "fecha"]):
        return MODELO_RAPIDO

    # conversa → modelo inteligente
    return MODELO_INTELIGENTE


# --------------------------------------------------
# ROTA PRINCIPAL
# --------------------------------------------------

@app.route("/comando", methods=["POST"])
def comando():
    try:
        data = request.json
        texto = data.get("texto", "")

        if not texto:
            return jsonify({"resposta": "Não recebi texto."})

        modelo = escolher_modelo(texto)

        start = time.time()

        resposta = requests.post(
            OLLAMA_URL,
            json={
                "model": modelo,
                "prompt": texto,
                "stream": False
            },
            timeout=TIMEOUT_OLLAMA
        )

        resposta.raise_for_status()
        data_ollama = resposta.json()

        texto_resposta = data_ollama.get("response", "").strip()

        lat = time.time() - start

        print(f"[SERVER] Modelo: {modelo} | Tempo: {lat:.2f}s")

        return jsonify({
            "resposta": texto_resposta,
            "model": modelo
        })

    except Exception as e:
        print(f"[ERRO SERVER] {e}")
        return jsonify({
            "resposta": "Erro interno no servidor.",
            "model": "erro"
        })


# --------------------------------------------------
# RUN
# --------------------------------------------------

if __name__ == "__main__":
    print("🚀 Jarvis Server a correr...")
    app.run(host="0.0.0.0", port=5000)