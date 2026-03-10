# ==================================================
# 🚀 JARVIS MK4 - RESPONSE ENGINE (SERVER AI VERSION)
# ==================================================

from typing import Optional, List, Dict
import re

from config.configuracoes import MODELO_INTELIGENTE, MODELO_RAPIDO
from ia.router.router_mk4 import analisar_intencao
from ia.ia_server import perguntar_ia


# ==================================================
# 🧠 SYSTEM PROMPT
# ==================================================

SYSTEM_PROMPT = """
Tu és Jarvis, assistente estratégico de alto nível.

Regras:
- Português europeu natural.
- Trata o utilizador por "Dudu".
- Inteligente, direto e confiante.
- Sarcasmo subtil apenas quando apropriado.
- Máximo 4 frases claras.
- Nunca menciones modelos de linguagem.
"""


# ==================================================
# 🧹 LIMPEZA DE TEXTO
# ==================================================

def _limpar_texto(texto: str) -> str:

    if not texto:
        return texto

    texto = re.sub(r"<.*?>", "", texto)
    texto = texto.replace("```", "")
    return texto.strip()


# ==================================================
# 🧠 SELF-CORRECTION LAYER
# ==================================================

def _avaliar_resposta(resposta: str) -> bool:

    prompt = f"""
Avalia a seguinte resposta.

Responde apenas:

OK
ou
REWRITE

Critérios:
- clareza
- concisão
- tom estratégico

Resposta:
{resposta}
"""

    avaliacao = perguntar_ia(prompt)

    if not avaliacao:
        return True

    return "OK" in avaliacao.upper()


# ==================================================
# 🎯 PREPARAR CONTEXTO
# ==================================================

def _preparar_contexto(
    mensagem: str,
    contexto_longo: str,
    historico_curto: Optional[List[Dict[str, str]]],
):

    mensagens = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    if contexto_longo:
        mensagens.append({
            "role": "system",
            "content": f"Memória relevante:\n{contexto_longo}"
        })

    if historico_curto:
        mensagens.extend(historico_curto[-4:])

    mensagens.append({
        "role": "user",
        "content": mensagem
    })

    return mensagens


# ==================================================
# 🔧 CONVERTER CHAT → PROMPT
# ==================================================

def _mensagens_para_prompt(mensagens):

    prompt = ""

    for m in mensagens:

        if m["role"] == "system":
            prompt += f"[SYSTEM]\n{m['content']}\n\n"

        elif m["role"] == "user":
            prompt += f"[USER]\n{m['content']}\n\n"

        elif m["role"] == "assistant":
            prompt += f"[ASSISTANT]\n{m['content']}\n\n"

    prompt += "[ASSISTANT]\n"

    return prompt


# ==================================================
# 🧠 DECISÃO DE MODELO
# ==================================================

def _decidir_modelo(intent: str) -> str:

    if intent in ["RACIOCINIO", "PLANEAMENTO"]:
        return MODELO_INTELIGENTE

    return MODELO_RAPIDO


# ==================================================
# 🔥 ENGINE NORMAL
# ==================================================

def gerar_resposta_mk4(
    mensagem: str,
    contexto_longo: Optional[str] = "",
    historico_curto: Optional[List[Dict[str, str]]] = None,
) -> str:

    decisao = analisar_intencao(mensagem)

    intent = decisao.get("intent", "RACIOCINIO")
    confidence = decisao.get("confidence", 0.5)
    risk = decisao.get("risk_level", "LOW")

    # 🛑 Travões de segurança
    if confidence < 0.6:
        return "Dudu, queres que eu execute isso ou apenas que te explique melhor?"

    if intent == "COMANDO" and risk == "HIGH":
        return "Isto pode alterar o sistema. Confirmas que devo avançar?"

    mensagens = _preparar_contexto(
        mensagem,
        contexto_longo,
        historico_curto
    )

    prompt = _mensagens_para_prompt(mensagens)

    resposta = perguntar_ia(prompt)

    if not resposta:
        return "Tive um pequeno contratempo interno, Dudu."

    resposta = _limpar_texto(resposta)

    # 🔎 Self-correction
    if not _avaliar_resposta(resposta):

        resposta_revisada = perguntar_ia(prompt)

        if resposta_revisada:
            return _limpar_texto(resposta_revisada)

    return resposta


# ==================================================
# 🚀 ENGINE COM STREAMING
# ==================================================

def gerar_resposta_mk4_stream(
    mensagem: str,
    contexto_longo: Optional[str] = "",
    historico_curto: Optional[List[Dict[str, str]]] = None,
    on_token=None
) -> str:

    resposta = gerar_resposta_mk4(
        mensagem,
        contexto_longo,
        historico_curto
    )

    if on_token and resposta:

        for token in resposta.split():
            on_token(token + " ")

    return resposta