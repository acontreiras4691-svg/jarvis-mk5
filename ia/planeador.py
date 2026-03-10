from ia.llm import gerar_resposta


def criar_plano(objetivo: str) -> str:

    prompt = f"""
Cria um plano passo-a-passo claro para executar o seguinte objetivo:

Objetivo: {objetivo}

Responde apenas com passos numerados.
"""

    return gerar_resposta(prompt)