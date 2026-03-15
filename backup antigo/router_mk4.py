# ==================================================
# 🚀 JARVIS MK4 - ROUTER COM EXTRAÇÃO AVANÇADA
# ==================================================

import json
import re
from typing import Dict, Any

from config.configuracoes import MODELO_RAPIDO
from ia.llm_base import chamar_modelo


# ==================================================
# 🧹 Limpeza robusta de JSON
# ==================================================

def _extrair_json_bruto(texto: str) -> str:

    if not texto:
        return "{}"

    texto = texto.replace("```json", "").replace("```", "").strip()

    match = re.search(r"\{.*\}", texto, re.DOTALL)

    return match.group(0) if match else "{}"


# ==================================================
# 🧹 Normalização STT
# ==================================================

def _normalizar(texto: str) -> str:

    texto = texto.lower().strip()

    # remover acentos
    texto = texto.replace("á", "a")
    texto = texto.replace("à", "a")
    texto = texto.replace("ã", "a")

    texto = texto.replace("é", "e")
    texto = texto.replace("ê", "e")

    texto = texto.replace("í", "i")

    texto = texto.replace("ó", "o")
    texto = texto.replace("ô", "o")

    texto = texto.replace("ú", "u")

    # correções comuns STT
    correcoes = {

        "abdo": "abre",
        "abri": "abre",
        "abra": "abre",

        "abre o": "abre",
        "abre um": "abre",
        "abrir o": "abre",

        "abre youtube": "abre youtube",

        "que horas sao": "hora",
        "horas sao": "hora"
    }

    for erro, correto in correcoes.items():
        texto = texto.replace(erro, correto)

    return texto


# ==================================================
# ⚡ HARD ROUTING (super rápido)
# ==================================================

def _hard_routing(texto: str):

    texto = _normalizar(texto)

    # ------------------------------------------------
    # CUMPRIMENTOS
    # ------------------------------------------------

    cumprimentos = [
        "ola",
        "bom dia",
        "boa tarde",
        "boa noite"
    ]

    if texto in cumprimentos:

        return {
            "intent": "FACTUAL",
            "entities": {"tipo": "cumprimento"},
            "confidence": 0.99,
            "risk_level": "LOW"
        }

    # ------------------------------------------------
    # HORA
    # ------------------------------------------------

    if "hora" in texto:

        return {
            "intent": "COMANDO",
            "entities": {"acao": "hora"},
            "confidence": 0.99,
            "risk_level": "LOW"
        }

    # ------------------------------------------------
    # DATA
    # ------------------------------------------------

    if "dia" in texto or "data" in texto:

        return {
            "intent": "COMANDO",
            "entities": {"acao": "data"},
            "confidence": 0.99,
            "risk_level": "LOW"
        }

    # ------------------------------------------------
    # YOUTUBE (qualquer frase)
    # ------------------------------------------------

    if "youtube" in texto:

        return {
            "intent": "COMANDO",
            "entities": {
                "acao": "abrir",
                "app": "youtube"
            },
            "confidence": 0.97,
            "risk_level": "LOW"
        }

    # ------------------------------------------------
    # ABRIR PROGRAMAS
    # ------------------------------------------------

    if "abre" in texto or "abrir" in texto:

        apps = [
            "chrome",
            "spotify",
            "steam",
            "calculadora",
            "notepad",
            "explorador"
        ]

        for app in apps:

            if app in texto:

                return {
                    "intent": "COMANDO",
                    "entities": {
                        "acao": "abrir",
                        "app": app
                    },
                    "confidence": 0.96,
                    "risk_level": "LOW"
                }

    # ------------------------------------------------
    # FECHAR PROGRAMAS
    # ------------------------------------------------

    if "fecha" in texto or "fechar" in texto:

        apps = [
            "chrome",
            "spotify",
            "steam",
            "notepad"
        ]

        for app in apps:

            if app in texto:

                return {
                    "intent": "COMANDO",
                    "entities": {
                        "acao": "fechar",
                        "app": app
                    },
                    "confidence": 0.96,
                    "risk_level": "LOW"
                }

    # ------------------------------------------------
    # DESLIGAR PC
    # ------------------------------------------------

    if "desligar" in texto or "desliga" in texto:

        return {
            "intent": "COMANDO",
            "entities": {"acao": "shutdown"},
            "confidence": 0.9,
            "risk_level": "HIGH"
        }

    return None


# ==================================================
# 🧠 Router MK4 principal
# ==================================================

def analisar_intencao(texto: str) -> Dict[str, Any]:

    # HARD ROUTING
    hard = _hard_routing(texto)

    if hard:
        return hard

    # ------------------------------------------------
    # LLM (fallback inteligente)
    # ------------------------------------------------

    mensagens = [

        {
            "role": "system",
            "content": """
You are an intent classifier.

Return ONLY JSON.

Format:

{
"intent":"COMANDO|FACTUAL|RACIOCINIO|PLANEAMENTO|MEMORIA",
"entities":{},
"confidence":0.0-1.0,
"risk_level":"LOW|MEDIUM|HIGH"
}
"""
        },

        {
            "role": "user",
            "content": texto
        }

    ]

    resposta = chamar_modelo(MODELO_RAPIDO, mensagens)

    try:

        json_limpo = _extrair_json_bruto(resposta)

        dados = json.loads(json_limpo)

        return {
            "intent": dados.get("intent", "RACIOCINIO"),
            "entities": dados.get("entities", {}),
            "confidence": float(dados.get("confidence", 0.6)),
            "risk_level": dados.get("risk_level", "LOW")
        }

    except Exception:

        return {
            "intent": "RACIOCINIO",
            "entities": {},
            "confidence": 0.5,
            "risk_level": "LOW"
        }