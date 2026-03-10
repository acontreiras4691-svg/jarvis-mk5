import subprocess
from pathlib import Path

PASTA_PROJETOS = Path("projetos_jarvis")


def executar_script(nome_script):

    caminho = PASTA_PROJETOS / nome_script

    if not caminho.exists():
        return "Script não encontrado."

    if caminho.suffix != ".py":
        return "Só posso executar scripts Python."

    try:

        resultado = subprocess.run(
            ["python", str(caminho)],
            capture_output=True,
            text=True,
            timeout=20
        )

        output = resultado.stdout or resultado.stderr

        return output.strip()

    except Exception as e:

        return f"Erro ao executar script: {e}"