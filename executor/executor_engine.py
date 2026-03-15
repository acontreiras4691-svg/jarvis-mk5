# ==================================================
# ⚙️ EXECUTOR ENGINE - JARVIS MK5
# ==================================================

import datetime
import webbrowser
import subprocess

try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None


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
        if not local or ZoneInfo is None:
            return None

        local = local.lower().strip()

        mapa = {
            "portugal": "Europe/Lisbon",
            "lisboa": "Europe/Lisbon",
            "porto": "Europe/Lisbon",

            "suica": "Europe/Zurich",
            "lausanne": "Europe/Zurich",
            "zurique": "Europe/Zurich",

            "reino unido": "Europe/London",
            "londres": "Europe/London",

            "franca": "Europe/Paris",
            "paris": "Europe/Paris",
        }

        tz_name = mapa.get(local)
        if not tz_name:
            return None

        try:
            return ZoneInfo(tz_name)
        except Exception:
            return None

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
                return f"Em {local}, são {agora.hour} horas e {agora.minute:02d} minutos."

            agora = datetime.datetime.now()

            if local:
                return f"Não consegui carregar o fuso horário de {local}, Dudu."

            return self._formatar_hora(agora)

        # ---------------------------------------------
        # DATA
        # ---------------------------------------------

        if intent == "assistant.date":
            local = entities.get("location")
            tz = self._resolver_timezone(local)

            if tz:
                hoje = datetime.datetime.now(tz)
                return f"Em {local}, hoje é dia {hoje.day} do mês {hoje.month} de {hoje.year}."

            hoje = datetime.datetime.now()

            if local:
                return f"Não consegui carregar a data local de {local}, Dudu."

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
        # SMART HOME - LUZ ON
        # ---------------------------------------------

        if intent == "smart_home.light_on":
            location = entities.get("location")

            if not self.smart_home:
                if location:
                    return f"Luz ligada em {location}. Sistema smart home ainda em modo simulado."
                return "Luz ligada. Sistema smart home ainda em modo simulado."

            return self.smart_home.controlar_luz(location=location, action="turn_on")

        # ---------------------------------------------
        # SMART HOME - LUZ OFF
        # ---------------------------------------------

        if intent == "smart_home.light_off":
            location = entities.get("location")

            if not self.smart_home:
                if location:
                    return f"Luz desligada em {location}. Sistema smart home ainda em modo simulado."
                return "Luz desligada. Sistema smart home ainda em modo simulado."

            return self.smart_home.controlar_luz(location=location, action="turn_off")

        # ---------------------------------------------
        # SMART HOME - TOMADA ON
        # ---------------------------------------------

        if intent == "smart_home.plug_on":
            location = entities.get("location")

            if not self.smart_home:
                if location:
                    return f"Tomada ligada em {location}. Sistema smart home ainda em modo simulado."
                return "Tomada ligada. Sistema smart home ainda em modo simulado."

            return self.smart_home.controlar_tomada(location=location, action="turn_on")

        # ---------------------------------------------
        # SMART HOME - TOMADA OFF
        # ---------------------------------------------

        if intent == "smart_home.plug_off":
            location = entities.get("location")

            if not self.smart_home:
                if location:
                    return f"Tomada desligada em {location}. Sistema smart home ainda em modo simulado."
                return "Tomada desligada. Sistema smart home ainda em modo simulado."

            return self.smart_home.controlar_tomada(location=location, action="turn_off")

        return None