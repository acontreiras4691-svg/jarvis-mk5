import subprocess
import os
from core.logger import log


PROGRAMAS_CONHECIDOS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "notepad": "notepad.exe",
    "calculadora": "calc.exe",
    "explorador": "explorer.exe"
}


def executar_acao_sistema(entities: dict):

    acao = entities.get("acao")
    app = entities.get("app", "").lower()

    try:

        # -------------------------
        # ABRIR
        # -------------------------

        if acao == "abrir":

            for nome, caminho in PROGRAMAS_CONHECIDOS.items():

                if nome in app:

                    log(f"A abrir {nome}")
                    subprocess.Popen(caminho)

                    return f"A abrir {nome}"

            return "Não reconheço esse programa."

        # -------------------------
        # FECHAR
        # -------------------------

        elif acao == "fechar":

            for nome, caminho in PROGRAMAS_CONHECIDOS.items():

                if nome in app:

                    processo = os.path.basename(caminho)

                    log(f"A fechar {nome}")
                    subprocess.call(
                        f"taskkill /f /im {processo}",
                        shell=True
                    )

                    return f"{nome} fechado."

            return "Programa não reconhecido."

        # -------------------------
        # HORA
        # -------------------------

        elif acao == "hora":

            from datetime import datetime
            return f"São {datetime.now().strftime('%H:%M')}."

        # -------------------------
        # DATA
        # -------------------------

        elif acao == "data":

            from datetime import datetime
            return f"Hoje é {datetime.now().strftime('%d/%m/%Y')}."

        # -------------------------

        return "Ação desconhecida."

    except Exception as e:

        log(f"Erro ao executar ação de sistema: {str(e)}")
        return "Erro ao executar ação."