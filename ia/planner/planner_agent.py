from ia.ia_server import perguntar_ia


def gerar_plano(tarefa):

    prompt = f"""
Transforma o pedido do utilizador num plano de execução.

Pedido:
{tarefa}

Responde apenas com passos numerados.
"""

    resposta = perguntar_ia(prompt)

    passos = [p.strip() for p in resposta.split("\n") if p.strip()]

    return passos