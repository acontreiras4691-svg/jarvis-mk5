import json

def router_mk4(texto):

    texto_limpo = texto.lower().strip()

    # 🏎 Hard Routing ultra básico
    if texto_limpo in ["olá", "bom dia", "boa tarde", "adeus"]:
        return {
            "intent": "FACTUAL",
            "entities": {}
        }

    mensagens = [
        {
            "role": "system",
            "content": """
You are an intent classifier and entity extractor.

Return ONLY valid JSON in this format:

{
  "intent": "COMANDO | FACTUAL | RACIOCINIO | PLANEAMENTO | MEMORIA",
  "entities": {
      "topic": "...",
      "timeframe": "...",
      "priority": "...",
      "other": "..."
  }
}

Rules:
- COMANDO: system actions.
- FACTUAL: simple questions.
- RACIOCINIO: explanations or deep reasoning.
- PLANEAMENTO: strategy, learning plans, structured guidance.
- MEMORIA: storing or recalling information.
"""
        },
        {"role": "user", "content": texto}
    ]

    resposta = chamar_modelo(MODELO_RAPIDO, mensagens)

    try:
        dados = json.loads(resposta)
        return dados
    except:
        return {
            "intent": "RACIOCINIO",
            "entities": {}
        }