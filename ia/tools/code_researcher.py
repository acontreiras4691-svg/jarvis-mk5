from ia.tools.web_search import pesquisar_web
from ia.ia_server import perguntar_ia


def gerar_codigo_com_pesquisa(descricao):

    pesquisa = pesquisar_web(descricao)

    prompt = f"""
Usa a seguinte informação da internet para gerar código melhor.

Pesquisa:
{pesquisa}

Pedido:
{descricao}

Gera apenas código Python limpo.
"""

    return perguntar_ia(prompt)