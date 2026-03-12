# ==================================================
# 🎯 INTENT ROUTER - JARVIS MK5 (IMPROVED)
# ==================================================

import datetime
import os
import webbrowser


# ==================================================
# ROUTER
# ==================================================

def route_intent(texto):

    texto = normalizar(texto.lower())

    # ---------------------------------------------
    # HORAS
    # ---------------------------------------------

    if "hora" in texto:

        return {
            "type": "command",
            "action": get_time
        }

    # ---------------------------------------------
    # DATA
    # ---------------------------------------------

    if "dia" in texto or "data" in texto:

        return {
            "type": "command",
            "action": get_date
        }

    # ---------------------------------------------
    # DESLIGAR PC
    # ---------------------------------------------

    if "desliga" in texto and "computador" in texto:

        return {
            "type": "command",
            "action": shutdown_pc
        }

    # ---------------------------------------------
    # REINICIAR PC
    # ---------------------------------------------

    if "reinicia" in texto and "computador" in texto:

        return {
            "type": "command",
            "action": restart_pc
        }

    # ---------------------------------------------
    # ABRIR YOUTUBE
    # ---------------------------------------------

    if "youtube" in texto and abrir_comando(texto):

        return {
            "type": "command",
            "action": open_youtube
        }

    # ---------------------------------------------
    # ABRIR CHROME
    # ---------------------------------------------

    if "chrome" in texto and abrir_comando(texto):

        return {
            "type": "command",
            "action": open_chrome
        }

    # ---------------------------------------------
    # ABRIR DISCORD
    # ---------------------------------------------

    if "discord" in texto and abrir_comando(texto):

        return {
            "type": "command",
            "action": open_discord
        }

    # ---------------------------------------------
    # ABRIR STEAM
    # ---------------------------------------------

    if "steam" in texto and abrir_comando(texto):

        return {
            "type": "command",
            "action": open_steam
        }

    # ---------------------------------------------
    # CHAT (LLM)
    # ---------------------------------------------

    return {
        "type": "chat"
    }


# ==================================================
# NORMALIZAÇÃO STT
# ==================================================

def normalizar(texto):

    correcoes = {

        "abadi": "abre",
        "breed": "abre",
        "abri": "abre",

        "abre o": "abre",
        "abrir o": "abre",
        "abra o": "abre",

        "abre um": "abre",
        "abrir um": "abre",

        "horas sao": "hora",
        "que horas sao": "hora"
    }

    for erro, correto in correcoes.items():
        texto = texto.replace(erro, correto)

    return texto


# ==================================================
# DETETAR COMANDO DE ABRIR
# ==================================================

def abrir_comando(texto):

    palavras = ["abre", "abrir", "abra"]

    for p in palavras:
        if p in texto:
            return True

    return False


# ==================================================
# AÇÕES
# ==================================================

def get_time(_):

    agora = datetime.datetime.now()

    return f"São {agora.hour} horas e {agora.minute:02d}, Dudu."


def get_date(_):

    hoje = datetime.datetime.now()

    meses = [
        "janeiro","fevereiro","março","abril","maio","junho",
        "julho","agosto","setembro","outubro","novembro","dezembro"
    ]

    return f"Hoje é dia {hoje.day} de {meses[hoje.month-1]} de {hoje.year}, Dudu."


# ==================================================
# SISTEMA
# ==================================================

def shutdown_pc(_):

    os.system("shutdown /s /t 5")

    return "A desligar o computador em 5 segundos."


def restart_pc(_):

    os.system("shutdown /r /t 5")

    return "A reiniciar o computador em 5 segundos."


# ==================================================
# ABRIR PROGRAMAS
# ==================================================

def open_youtube(_):

    webbrowser.open("https://www.youtube.com")

    return "A abrir o YouTube."


def open_chrome(_):

    os.system("start chrome")

    return "A abrir o Chrome."


def open_discord(_):

    os.system("start discord")

    return "A abrir o Discord."


def open_steam(_):

    os.system("start steam")

    return "A abrir o Steam."
    