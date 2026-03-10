import datetime
import json
from ia.classificador import classificar_modo
from ia.llm import gerar_resposta


def extrair_json_valido(raw: str):
    try:
        inicio = raw.index("{")
        fim = raw.rindex("}") + 1
        return json.loads(raw[inicio:fim])
    except Exception:
        return None


def interpretar_comando(texto: str):

    texto_lower = texto.lower().strip()

    # 🔹 RESPOSTAS LOCAIS (rápidas e offline)

    if "que horas" in texto_lower:
        agora = datetime.datetime.now()
        return {
            "modo": "resposta_local",
            "resposta": f"São {agora.hour} horas e {agora.minute} minutos."
        }

    if "que dia" in texto_lower:
        agora = datetime.datetime.now()
        return {
            "modo": "resposta_local",
            "resposta": f"Hoje é dia {agora.day} do mês {agora.month} de {agora.year}."
        }

    # 🔹 BLOCO DOMÉSTICO (SEM LLM)

    if texto_lower.startswith("abre"):
        return {
            "modo": "domestico",
            "acao": "abrir",
            "detalhes": texto_lower.replace("abre", "", 1).strip()
        }

    if texto_lower.startswith("fecha"):
        return {
            "modo": "domestico",
            "acao": "fechar",
            "detalhes": texto_lower.replace("fecha", "", 1).strip()
        }

    if texto_lower.startswith("liga"):
        return {
            "modo": "domestico",
            "acao": "ligar",
            "detalhes": texto_lower.replace("liga", "", 1).strip()
        }

    if texto_lower.startswith("desliga"):
        return {
            "modo": "domestico",
            "acao": "desligar",
            "detalhes": texto_lower.replace("desliga", "", 1).strip()
        }

    # 🔹 RESTO → LLM estruturado

    prompt = f"""
Responde apenas com JSON estruturado:

{{
    "tipo": "",
    "acao": "",
    "detalhes": ""
}}

Texto: {texto}
"""

    resposta = gerar_resposta(prompt)
    dados = extrair_json_valido(resposta)

    if not dados:
        return {
            "modo": "erro",
            "descricao": "Falha ao interpretar comando"
        }

    return dados