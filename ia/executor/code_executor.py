from pathlib import Path
from ia.ia_server import perguntar_ia

PASTA_PROJETOS = Path("projetos_jarvis")
PASTA_PROJETOS.mkdir(exist_ok=True)


def gerar_codigo(descricao):

    prompt = f"""
Gera código Python limpo e funcional.

Descrição:
{descricao}

Responde apenas com código.
"""

    codigo = perguntar_ia(prompt)

    return codigo


def criar_script(nome, descricao):

    codigo = gerar_codigo(descricao)

    caminho = PASTA_PROJETOS / f"{nome}.py"

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(codigo)

    return caminho