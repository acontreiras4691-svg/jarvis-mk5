from pathlib import Path
from ia.ia_server import perguntar_ia


def editar_ficheiro(caminho, instrucao):

    caminho = Path(caminho)

    if not caminho.exists():
        return "Ficheiro não encontrado."

    codigo = caminho.read_text(encoding="utf-8")

    prompt = f"""
Edita o seguinte código conforme a instrução.

INSTRUÇÃO:
{instrucao}

CÓDIGO:
{codigo}

Responde apenas com o código final.
"""

    novo_codigo = perguntar_ia(prompt)

    caminho.write_text(novo_codigo, encoding="utf-8")

    return "Ficheiro atualizado com sucesso."