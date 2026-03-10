# ==================================================
# 🚀 JARVIS MK4 ROUTER
# Intenção + Conversa + Resposta Inteligente
# ==================================================

import json
from typing import Dict, Any, List

from ia.llm_base import chamar_modelo
from config.configuracoes import MODELO_RAPIDO


# ==================================================
# 🧠 PROMPT ROUTER
# ==================================================

ROUTER_PROMPT = """
You are an AI intent router.

Analyse the user message and return ONLY a valid JSON.

Return format:

{
  "intent": "COMANDO | RACIOCINIO | PLANEAMENTO | CONVERSA",
  "entities": {},
  "risk_level": "LOW | MEDIUM | HIGH",
  "confidence": 0.0
}
"""


# ==================================================
# 🤖 PROMPT DO JARVIS
# ==================================================

ASSISTANT_PROMPT = """
You are Jarvis, the personal AI assistant of Dudu.

You speak Portuguese from Portugal.

Personality:

- intelligent
- calm
- efficient
- slightly witty
- helpful

Behaviour rules:

- Think internally before answering.
- Respond naturally like a human assistant.
- Be concise when possible.
- Explain clearly when reasoning is needed.

Always remain polite.

User name: Dudu.
"""


# ==================================================
# 🧠 ANALISAR INTENÇÃO
# ==================================================

def analisar_intencao(mensagem: str) -> Dict[str, Any]:

    mensagens = [
        {"role": "system", "content": ROUTER_PROMPT},
        {"role": "user", "content": mensagem}
    ]

    resposta = chamar_modelo(
        MODELO_RAPIDO,
        mensagens,
        temperature=0.0
    )

    if not resposta:
        return _fallback()

    try:

        texto_limpo = _limpar_json(resposta)

        dados = json.loads(texto_limpo)

        return {
            "intent": dados.get("intent", "RACIOCINIO"),
            "entities": dados.get("entities", {}),
            "risk_level": dados.get("risk_level", "LOW"),
            "confidence": float(dados.get("confidence", 0.5))
        }

    except Exception:

        return _fallback()


# ==================================================
# 🤖 GERAR RESPOSTA DO JARVIS
# ==================================================

def gerar_resposta_mk4_stream(
    mensagem: str,
    contexto_longo: str,
    historico_curto: List[Dict[str, str]],
    on_token=None
):

    mensagens = [
        {"role": "system", "content": ASSISTANT_PROMPT}
    ]

    # histórico curto da conversa
    mensagens.extend(historico_curto)

    # pergunta atual
    mensagens.append({
        "role": "user",
        "content": mensagem
    })

    resposta = chamar_modelo(
        MODELO_RAPIDO,
        mensagens,
        temperature=0.6,
        stream=True,
        on_token=on_token
    )

    return resposta


# ==================================================
# 🔧 UTILITÁRIOS
# ==================================================

def _limpar_json(texto: str) -> str:

    texto = texto.replace("```json", "")
    texto = texto.replace("```", "")
    texto = texto.strip()

    return texto


def _fallback() -> Dict[str, Any]:

    return {
        "intent": "RACIOCINIO",
        "entities": {},
        "risk_level": "LOW",
        "confidence": 0.5
    }
    