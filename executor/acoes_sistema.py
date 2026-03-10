import subprocess
import os
from core.logger import log


PROGRAMAS_CONHECIDOS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "notepad": "notepad.exe",
    "calculadora": "calc.exe",
    "explorador": "explorer.exe"
}


def executar_acao_sistema(comando: dict):

    acao = comando.get("acao")
    detalhes = comando.get("detalhes", "").lower().strip()

    try:

        if acao == "abrir":

            for nome, caminho in PROGRAMAS_CONHECIDOS.items():
                if nome in detalhes:
                    log(f"A abrir {nome}")
                    subprocess.Popen(caminho)
                    return f"{nome} aberto."

            return "Programa não reconhecido."

        elif acao == "fechar":

            for nome, caminho in PROGRAMAS_CONHECIDOS.items():
                if nome in detalhes:

                    # 🔥 Aqui está a correção
                    processo = os.path.basename(caminho)

                    log(f"A fechar {nome}")
                    subprocess.call(f"taskkill /f /im {processo}", shell=True)
                    return f"{nome} fechado."

            return "Programa não reconhecido."

        else:
            return "Ação desconhecida."

    except Exception as e:
        log(f"Erro ao executar ação de sistema: {str(e)}")
        return "Erro ao executar ação."