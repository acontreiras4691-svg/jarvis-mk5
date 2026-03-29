# ==================================================
# ⚙️ EXECUTOR ENGINE - JARVIS MK5
# ==================================================

import datetime
import platform
import subprocess
import webbrowser

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

        local = str(local).lower().strip()

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
            "espanha": "Europe/Madrid",
            "madrid": "Europe/Madrid",
        }

        tz_name = mapa.get(local)
        if not tz_name:
            return None

        try:
            return ZoneInfo(tz_name)
        except Exception:
            return None

    def _is_windows(self):
        return platform.system().lower().startswith("win")

    def _run_command(self, cmd):
        try:
            subprocess.Popen(cmd)
            return True
        except Exception:
            return False

    # ------------------------------------------------
    # EXECUTAR
    # ------------------------------------------------

    def executar(self, intent_data):
        intent = intent_data.get("intent")
        entities = intent_data.get("entities", {}) or {}

        if not intent:
            return "Intent inválida."

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

            if not app:
                return "Não percebi que aplicação queres abrir."

            if app == "youtube":
                webbrowser.open("https://youtube.com")
                return "A abrir o YouTube."

            if app == "spotify":
                if self._is_windows():
                    if self._run_command(["cmd", "/c", "start", "spotify"]):
                        return "A abrir o Spotify."
                else:
                    if self._run_command(["spotify"]):
                        return "A abrir o Spotify."
                return "Não consegui abrir o Spotify."

            if app == "discord":
                if self._is_windows():
                    if self._run_command(["cmd", "/c", "start", "discord"]):
                        return "A abrir o Discord."
                else:
                    if self._run_command(["discord"]):
                        return "A abrir o Discord."
                return "Não consegui abrir o Discord."

            if app == "chrome":
                if self._is_windows():
                    if self._run_command(["cmd", "/c", "start", "chrome"]):
                        return "A abrir o Chrome."
                else:
                    if self._run_command(["google-chrome"]):
                        return "A abrir o Chrome."
                    if self._run_command(["chrome"]):
                        return "A abrir o Chrome."
                return "Não consegui abrir o Chrome."

            if app == "steam":
                if self._is_windows():
                    if self._run_command(["cmd", "/c", "start", "steam"]):
                        return "A abrir o Steam."
                else:
                    if self._run_command(["steam"]):
                        return "A abrir o Steam."
                return "Não consegui abrir o Steam."

            return "Não encontrei essa aplicação."

        # ---------------------------------------------
        # DESLIGAR PC
        # ---------------------------------------------
        if intent == "system.shutdown":
            if self._is_windows():
                try:
                    subprocess.Popen(["shutdown", "/s", "/t", "0"])
                    return "A desligar o computador."
                except Exception as e:
                    return f"Falhei ao desligar o computador: {e}"

            try:
                subprocess.Popen(["shutdown", "now"])
                return "A desligar o computador."
            except Exception as e:
                return f"Falhei ao desligar o computador: {e}"

        # ---------------------------------------------
        # REINICIAR PC
        # ---------------------------------------------
        if intent == "system.restart":
            if self._is_windows():
                try:
                    subprocess.Popen(["shutdown", "/r", "/t", "0"])
                    return "A reiniciar o computador."
                except Exception as e:
                    return f"Falhei ao reiniciar o computador: {e}"

            try:
                subprocess.Popen(["reboot"])
                return "A reiniciar o computador."
            except Exception as e:
                return f"Falhei ao reiniciar o computador: {e}"

        # ---------------------------------------------
        # SMART HOME - LUZ ON
        # ---------------------------------------------
        if intent == "smart_home.light_on":
            location = entities.get("location")

            if not self.smart_home:
                if location:
                    return f"Luz ligada em {location}. Sistema smart home ainda em modo simulado."
                return "Luz ligada. Sistema smart home ainda em modo simulado."

            return self.smart_home.controlar_luz(
                location=location,
                action="turn_on",
            )

        # ---------------------------------------------
        # SMART HOME - LUZ OFF
        # ---------------------------------------------
        if intent == "smart_home.light_off":
            location = entities.get("location")

            if not self.smart_home:
                if location:
                    return f"Luz desligada em {location}. Sistema smart home ainda em modo simulado."
                return "Luz desligada. Sistema smart home ainda em modo simulado."

            return self.smart_home.controlar_luz(
                location=location,
                action="turn_off",
            )

        # ---------------------------------------------
        # SMART HOME - BRILHO
        # ---------------------------------------------
        if intent == "smart_home.light_set_brightness":
            location = entities.get("location")
            brightness = entities.get("brightness")

            if brightness is None:
                return "Não percebi o valor do brilho."

            if not self.smart_home:
                if location:
                    return f"Brilho da luz em {location} ajustado para {brightness} por cento. Sistema smart home ainda em modo simulado."
                return f"Brilho da luz ajustado para {brightness} por cento. Sistema smart home ainda em modo simulado."

            return self.smart_home.controlar_luz(
                location=location,
                brightness=brightness,
            )

        # ---------------------------------------------
        # SMART HOME - TIMER OFF
        # ---------------------------------------------
        if intent == "smart_home.light_off_timer":
            location = entities.get("location")
            minutes = entities.get("minutes")

            if not minutes:
                return "Não percebi o número de minutos."

            if not self.smart_home:
                if location:
                    return f"Vou apagar a luz em {location} daqui a {minutes} minutos. Sistema smart home ainda em modo simulado."
                return f"Vou apagar a luz daqui a {minutes} minutos. Sistema smart home ainda em modo simulado."

            return self.smart_home.agendar_desligar_luz(
                location=location,
                minutes=minutes,
            )

        # ---------------------------------------------
        # SMART HOME - TOMADA ON
        # ---------------------------------------------
        if intent == "smart_home.plug_on":
            location = entities.get("location")

            if not self.smart_home:
                if location:
                    return f"Tomada ligada em {location}. Sistema smart home ainda em modo simulado."
                return "Tomada ligada. Sistema smart home ainda em modo simulado."

            return self.smart_home.controlar_tomada(
                location=location,
                action="turn_on",
            )

        # ---------------------------------------------
        # SMART HOME - TOMADA OFF
        # ---------------------------------------------
        if intent == "smart_home.plug_off":
            location = entities.get("location")

            if not self.smart_home:
                if location:
                    return f"Tomada desligada em {location}. Sistema smart home ainda em modo simulado."
                return "Tomada desligada. Sistema smart home ainda em modo simulado."

            return self.smart_home.controlar_tomada(
                location=location,
                action="turn_off",
            )

        # ---------------------------------------------
        # APPLE TV
        # ---------------------------------------------
        if intent.startswith("media.apple_tv_"):
            if not self.smart_home:
                return "Apple TV não configurada no smart home."

            action = entities.get("action")
            app_name = entities.get("app_name")

            if not action:
                return "Não percebi a ação da Apple TV."

            return self.smart_home.controlar_apple_tv(
                action=action,
                app_name=app_name,
            )

        return None