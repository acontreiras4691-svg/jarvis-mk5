# ==================================================
# 🚀 JARVIS MK4 - ROUTER COM EXTRAÇÃO AVANÇADA
# ==================================================

import json
import re
from typing import Dict, Any

from config.configuracoes import MODELO_RAPIDO
from ia.llm_base import chamar_modelo  # função genérica para chamar Ollama


# ==================================================
# 🧹 Limpeza robusta de JSON (anti-markdown)
# ==================================================

def _extrair_json_bruto(texto: str) -> str:
    """
    Extrai apenas o conteúdo JSON válido mesmo que venha
    envolvido em ```json ... ``` ou texto extra.
    """
    if not texto:
        return "{}"

    # Remove blocos markdown
    texto = texto.replace("```json", "").replace("```", "").strip()

    # Extrai apenas o primeiro bloco { ... }
    match = re.search(r"\{.*\}", texto, re.DOTALL)
    return match.group(0) if match else "{}"


# ==================================================
# 🏎 Hard Routing mínimo (latência zero)
# ==================================================

def _hard_routing(texto: str) -> Dict[str, Any] | None:
    texto_limpo = texto.lower().strip()

    cumprimentos = ["olá", "ola", "bom dia", "boa tarde", "boa noite"]
    despedidas = ["adeus", "até logo", "ate logo"]

    if texto_limpo in cumprimentos:
        return {
            "intent": "FACTUAL",
            "entities": {},
            "confidence": 0.95,
            "risk_level": "LOW"
        }

    if texto_limpo in despedidas:
        return {
            "intent": "FACTUAL",
            "entities": {},
            "confidence": 0.95,
            "risk_level": "LOW"
        }

    # Frases muito curtas normalmente simples
    if len(texto_limpo.split()) <= 2:
        return {
            "intent": "FACTUAL",
            "entities": {},
            "confidence": 0.7,
            "risk_level": "LOW"
        }

    return None


# ==================================================
# 🧠 Router MK4 Principal
# ==================================================

def analisar_intencao(texto: str) -> Dict[str, Any]:
    """
    Classifica intenção, extrai entidades,
    calcula confiança e nível de risco.
    """

    # 🔹 1. Tentar hard routing primeiro
    hard = _hard_routing(texto)
    if hard:
        return hard

    # 🔹 2. Chamada ao modelo rápido
    mensagens = [
        {
            "role": "system",
            "content": """
You are an advanced intent classifier and entity extractor.

Return ONLY valid JSON.

Format:

{
  "intent": "COMANDO | FACTUAL | RACIOCINIO | PLANEAMENTO | MEMORIA",
  "entities": { extract ALL explicitly mentioned entities },
  "confidence": 0.0-1.0,
  "risk_level": "LOW | MEDIUM | HIGH"
}

Rules:

COMANDO:
- system actions, execution requests.

FACTUAL:
- simple questions or greetings.

RACIOCINIO:
- explanations, deep thinking.

PLANEAMENTO:
- strategic guidance, learning plans, structured tasks.

MEMORIA:
- storing or recalling information.

Risk level:
- HIGH: deletion, system change, critical modification.
- MEDIUM: file/state change.
- LOW: normal explanation or chat.

Confidence:
- Estimate classification certainty.
"""
        },
        {"role": "user", "content": texto}
    ]

    resposta = chamar_modelo(MODELO_RAPIDO, mensagens)

    # 🔹 3. Tentar parse seguro
    try:
        json_limpo = _extrair_json_bruto(resposta)
        dados = json.loads(json_limpo)

        # Garantir campos mínimos
        return {
            "intent": dados.get("intent", "RACIOCINIO"),
            "entities": dados.get("entities", {}),
            "confidence": float(dados.get("confidence", 0.6)),
            "risk_level": dados.get("risk_level", "LOW")
        }

    except Exception:
        # 🔹 4. Fallback inteligente
        return {
            "intent": "RACIOCINIO",
            "entities": {},
            "confidence": 0.5,
            "risk_level": "LOW"
        }