# ==================================================
# ⚙️ EXECUTOR ENGINE - JARVIS MK5
# ==================================================

import datetime
import webbrowser
import subprocess
from zoneinfo import ZoneInfo


class Executor:

    def __init__(self, smart_home=None):
        self.smart_home = smart_home

    # ------------------------------------------------
    # HELPERS
    # ------------------------------------------------

    def _formatar_hora(self, dt: datetime.datetime) -> str:
        return f"São {dt.hour} horas e {dt.minute:02d} minutos."

    def _formatar_data(self, dt: datetime.datetime) -> str:
        return f"Hoje é dia {dt.day} do mês {dt.month} de {dt.year}."

    def _resolver_timezone(self, local: str | None):
        if not local:
            return None

        local = local.lower().strip()

        mapa = {
            "portugal": "Europe/Lisbon",
            "lisboa": "Europe/Lisbon",
            "porto": "Europe/Lisbon",

            "suica": "Europe/Zurich",
            "suíça": "Europe/Zurich",
            "switzerland": "Europe/Zurich",
            "zurique": "Europe/Zurich",
            "lausanne": "Europe/Zurich",

            "reino unido": "Europe/London",
            "londres": "Europe/London",

            "franca": "Europe/Paris",
            "frança": "Europe/Paris",
            "paris": "Europe/Paris",
        }

        tz_name = mapa.get(local)

        if not tz_name:
            return None

        return ZoneInfo(tz_name)

    # ------------------------------------------------
    # EXECUTAR
    # ------------------------------------------------

    def executar(self, intent_data):

        intent = intent_data.get("intent")
        entities = intent_data.get("entities", {}) or {}

        # ---------------------------------------------
        # HORAS
        # ---------------------------------------------

        if intent == "assistant.time":

            local = entities.get("location")
            tz = self._resolver_timezone(local)

            if tz:
                agora = datetime.datetime.now(tz)

                if local:
                    return f"Em {local}, {self._formatar_hora(agora).lower()}"

                return self._formatar_hora(agora)

            agora = datetime.datetime.now()
            return self._formatar_hora(agora)

        # ---------------------------------------------
        # DATA
        # ---------------------------------------------

        if intent == "assistant.date":

            local = entities.get("location")
            tz = self._resolver_timezone(local)

            if tz:
                agora = datetime.datetime.now(tz)

                if local:
                    return f"Em {local}, {self._formatar_data(agora).lower()}"

                return self._formatar_data(agora)

            hoje = datetime.datetime.now()
            return self._formatar_data(hoje)

        # ---------------------------------------------
        # ABRIR APP
        # ---------------------------------------------

        if intent == "system.open_app":

            app = entities.get("app")

            if app == "youtube":
                webbrowser.open("https://youtube.com")
                return "A abrir o YouTube."

            if app == "spotify":
                subprocess.Popen("spotify")
                return "A abrir o Spotify."

            if app == "discord":
                subprocess.Popen("discord")
                return "A abrir o Discord."

            if app == "chrome":
                subprocess.Popen("chrome")
                return "A abrir o Chrome."

            if app == "steam":
                subprocess.Popen("steam")
                return "A abrir o Steam."

            return "Não encontrei essa aplicação."

        # ---------------------------------------------
        # SMART HOME
        # ---------------------------------------------

        if intent == "smart_home.light_on":

            if not self.smart_home:
                return "O sistema de luzes ainda não está ligado."

            location = entities.get("location")
            return self.smart_home.controlar_luz(location=location, action="turn_on")

        if intent == "smart_home.light_off":

            if not self.smart_home:
                return "O sistema de luzes ainda não está ligado."

            location = entities.get("location")
            return self.smart_home.controlar_luz(location=location, action="turn_off")

        if intent == "smart_home.plug_on":

            if not self.smart_home:
                return "O sistema de tomadas ainda não está ligado."

            location = entities.get("location")
            return self.smart_home.controlar_tomada(location=location, action="turn_on")

        if intent == "smart_home.plug_off":

            if not self.smart_home:
                return "O sistema de tomadas ainda não está ligado."

            location = entities.get("location")
            return self.smart_home.controlar_tomada(location=location, action="turn_off")

        return None