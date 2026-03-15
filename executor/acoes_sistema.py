import os
import subprocess
from datetime import datetime

from core.logger import log


PROGRAMAS_CONHECIDOS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "notepad": "notepad.exe",
    "bloco de notas": "notepad.exe",
    "calculadora": "calc.exe",
    "explorador": "explorer.exe",
    "discord": "discord.exe",
    "steam": "steam.exe",
}


def executar_acoes_sistema(intent: str, entities: dict):
    app = entities.get("app", "").lower().strip()

    try:
        # ------------------------------------------------
        # HORA
        # ------------------------------------------------
        if intent == "assistant.time":
            return f"São {datetime.now().strftime('%H:%M')}, Dudu."

        # ------------------------------------------------
        # DATA
        # ------------------------------------------------
        if intent == "assistant.date":
            return f"Hoje é {datetime.now().strftime('%d/%m/%Y')}, Dudu."

        # ------------------------------------------------
        # ABRIR APP
        # ------------------------------------------------
        if intent == "system.open_app":
            for nome, caminho in PROGRAMAS_CONHECIDOS.items():
                if nome in app:
                    log(f"A abrir {nome}")
                    subprocess.Popen(caminho, shell=True)
                    return f"A abrir {nome}."

            return "Não reconheço essa aplicação."

        # ------------------------------------------------
        # DESLIGAR PC
        # ------------------------------------------------
        if intent == "system.shutdown":
            log("A desligar o computador")
            os.system("shutdown /s /t 5")
            return "A desligar o computador em 5 segundos."

        # ------------------------------------------------
        # REINICIAR PC
        # ------------------------------------------------
        if intent == "system.restart":
            log("A reiniciar o computador")
            os.system("shutdown /r /t 5")
            return "A reiniciar o computador em 5 segundos."

        return "Ação de sistema desconhecida."

    except Exception as e:
        log(f"Erro ao executar ação de sistema: {str(e)}")
        return "Erro ao executar ação."