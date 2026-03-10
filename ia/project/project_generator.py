from pathlib import Path
from ia.ia_server import perguntar_ia

BASE_PROJETOS = Path("projetos_jarvis")
BASE_PROJETOS.mkdir(exist_ok=True)


def gerar_estrutura(descricao):

    prompt = f"""
Cria a estrutura de ficheiros para este projeto.

Projeto:
{descricao}

Responde apenas com uma lista de ficheiros.
Exemplo:

main.py
requirements.txt
README.md
"""

    resposta = perguntar_ia(prompt)

    ficheiros = [f.strip() for f in resposta.split("\n") if f.strip()]

    return ficheiros


def gerar_codigo(ficheiro, descricao):

    prompt = f"""
Gera o código completo para o ficheiro.

Ficheiro: {ficheiro}

Projeto:
{descricao}

Responde apenas com código.
"""

    return perguntar_ia(prompt)


def criar_projeto(nome_projeto, descricao):

    pasta = BASE_PROJETOS / nome_projeto
    pasta.mkdir(exist_ok=True)

    estrutura = gerar_estrutura(descricao)

    for ficheiro in estrutura:

        caminho = pasta / ficheiro

        codigo = gerar_codigo(ficheiro, descricao)

        caminho.write_text(codigo, encoding="utf-8")

    return f"Projeto criado em {pasta}"