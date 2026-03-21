# ==================================================
# ⚙️ EXECUTOR ENGINE - JARVIS MK5
# ==================================================

import datetime
import os
import subprocess
import threading
import webbrowser

from core.logger import log

try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None


class Executor:
    def __init__(self, smart_home=None):
        self.smart_home = smart_home
        self._timers = []

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
            "suíça": "Europe/Zurich",
            "lausanne": "Europe/Zurich",
            "zurique": "Europe/Zurich",
            "reino unido": "Europe/London",
            "londres": "Europe/London",
            "franca": "Europe/Paris",
            "frança": "Europe/Paris",
            "paris": "Europe/Paris",
            "espanha": "Europe/Madrid",
            "madrid": "Europe/Madrid",
        }

        tz_name = mapa.get(local)
        if not tz_name:
            return None

        try:
            return ZoneInfo(tz_name)
        except Exception as e:
            log(f"⚠️ Erro a carregar timezone '{local}': {e}")
            return None

    def _executar_subprocesso(self, comando, nome_app: str) -> bool:
        try:
            subprocess.Popen(comando, shell=isinstance(comando, str))
            return True
        except Exception as e:
            log(f"⚠️ Falha a abrir {nome_app}: {e}")
            return False

    def _abrir_app(self, app: str) -> str:
        """
        Retorna:
        - OK_APP_OPEN      -> abriu mesmo
        - ERR_APP_OPEN     -> tentou mas falhou
        - ERR_APP_UNKNOWN  -> app desconhecida
        """

        caminhos_startfile = {
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "spotify": r"C:\Users\acont\AppData\Roaming\Spotify\Spotify.exe",
            "steam": r"C:\Program Files (x86)\Steam\Steam.exe",
        }

        caminhos_subprocess = {
            "discord": r'"C:\Users\acont\AppData\Local\Discord\Update.exe" --processStart Discord.exe',
        }

        # ---------------------------------------------
        # YOUTUBE
        # ---------------------------------------------
        if app == "youtube":
            try:
                webbrowser.open("https://youtube.com")
                return "OK_APP_OPEN"
            except Exception as e:
                log(f"⚠️ Falha a abrir YouTube: {e}")
                return "ERR_APP_OPEN"

        if app in caminhos_startfile:
            caminho = caminhos_startfile[app]

            try:
                os.startfile(caminho)
                return "OK_APP_OPEN"
            except Exception as e:
                log(f"⚠️ Falha a abrir {app}: {e}")
                return "ERR_APP_OPEN"

        if app in caminhos_subprocess:
            comando = caminhos_subprocess[app]

            try:
                subprocess.Popen(comando, shell=True)
                return "OK_APP_OPEN"
            except Exception as e:
                log(f"⚠️ Falha a abrir {app}: {e}")
                return "ERR_APP_OPEN"

        return "ERR_APP_UNKNOWN"

    def _timer_desligar_luz(self, location: str | None, minutes: int):
        def job():
            try:
                if self.smart_home:
                    self.smart_home.controlar_luz(
                        location=location,
                        action="turn_off"
                    )
                    if location:
                        log(f"⏱️ Temporizador executado: luz apagada em {location}")
                    else:
                        log("⏱️ Temporizador executado: luz apagada")
            except Exception as e:
                log(f"⚠️ Erro no temporizador da luz: {e}")

        segundos = max(1, int(minutes * 60))
        timer = threading.Timer(segundos, job)
        timer.daemon = True
        timer.start()
        self._timers.append(timer)

    def _smart_home_indisponivel(
        self,
        mensagem_com_local: str,
        mensagem_sem_local: str,
        location: str | None
    ):
        if location:
            return mensagem_com_local
        return mensagem_sem_local

    def _ajustar_brilho_relativo_simulado(self, location: str | None, direction: str | None):
        if direction == "up":
            return self._smart_home_indisponivel(
                f"Brilho aumentado em {location}. Sistema smart home ainda em modo simulado.",
                "Brilho aumentado. Sistema smart home ainda em modo simulado.",
                location,
            )

        return self._smart_home_indisponivel(
            f"Brilho reduzido em {location}. Sistema smart home ainda em modo simulado.",
            "Brilho reduzido. Sistema smart home ainda em modo simulado.",
            location,
        )

    def _temperatura_luz_simulada(self, location: str | None, mode: str | None):
        if mode == "warmer":
            return self._smart_home_indisponivel(
                f"Luz mais quente em {location}. Sistema smart home ainda em modo simulado.",
                "Luz mais quente. Sistema smart home ainda em modo simulado.",
                location,
            )

        return self._smart_home_indisponivel(
            f"Luz mais fria em {location}. Sistema smart home ainda em modo simulado.",
            "Luz mais fria. Sistema smart home ainda em modo simulado.",
            location,
        )

    def _ativar_cena_simulada(self, scene: str, location: str | None):
        nomes = {
            "cinema": "Modo cinema",
            "relax": "Modo relax",
            "gaming": "Modo gaming",
        }

        nome_cena = nomes.get(scene, "Modo")
        return self._smart_home_indisponivel(
            f"{nome_cena} ativado em {location} em modo simulado.",
            f"{nome_cena} ativado em modo simulado.",
            location,
        )

    # ------------------------------------------------
    # EXECUTAR
    # ------------------------------------------------

    def executar(self, intent_data):
        intent = intent_data.get("intent")
        entities = intent_data.get("entities", {}) or {}

        log(f"⚙️ Executor -> intent={intent} | entities={entities}")

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

            resultado = self._abrir_app(app)

            if resultado == "OK_APP_OPEN":
                return "OK_APP_OPEN"

            if resultado == "ERR_APP_UNKNOWN":
                return "Não encontrei essa aplicação."

            return f"Não consegui abrir {app}."

        # ---------------------------------------------
        # DESLIGAR PC
        # ---------------------------------------------
        if intent == "system.shutdown":
            try:
                os.system("shutdown /s /t 5")
                return "Vou desligar o computador em 5 segundos."
            except Exception as e:
                log(f"⚠️ Erro a desligar computador: {e}")
                return "Não consegui desligar o computador."

        # ---------------------------------------------
        # REINICIAR PC
        # ---------------------------------------------
        if intent == "system.restart":
            try:
                os.system("shutdown /r /t 5")
                return "Vou reiniciar o computador em 5 segundos."
            except Exception as e:
                log(f"⚠️ Erro a reiniciar computador: {e}")
                return "Não consegui reiniciar o computador."

        # ---------------------------------------------
        # SMART HOME - LUZ ON
        # ---------------------------------------------
        if intent == "smart_home.light_on":
            location = entities.get("location")

            if not self.smart_home:
                return self._smart_home_indisponivel(
                    f"Luz ligada em {location}. Sistema smart home ainda em modo simulado.",
                    "Luz ligada. Sistema smart home ainda em modo simulado.",
                    location,
                )

            try:
                resposta = self.smart_home.controlar_luz(location=location, action="turn_on")
                log(f"⚙️ Executor light_on -> resposta={resposta}")
                return resposta
            except Exception as e:
                log(f"⚠️ Erro smart_home light_on: {e}")
                return "Não consegui ligar a luz."

        # ---------------------------------------------
        # SMART HOME - LUZ OFF
        # ---------------------------------------------
        if intent == "smart_home.light_off":
            location = entities.get("location")

            if not self.smart_home:
                return self._smart_home_indisponivel(
                    f"Luz desligada em {location}. Sistema smart home ainda em modo simulado.",
                    "Luz desligada. Sistema smart home ainda em modo simulado.",
                    location,
                )

            try:
                resposta = self.smart_home.controlar_luz(location=location, action="turn_off")
                log(f"⚙️ Executor light_off -> resposta={resposta}")
                return resposta
            except Exception as e:
                log(f"⚠️ Erro smart_home light_off: {e}")
                return "Não consegui desligar a luz."

        # ---------------------------------------------
        # SMART HOME - TOMADA ON
        # ---------------------------------------------
        if intent == "smart_home.plug_on":
            location = entities.get("location")

            if not self.smart_home:
                return self._smart_home_indisponivel(
                    f"Tomada ligada em {location}. Sistema smart home ainda em modo simulado.",
                    "Tomada ligada. Sistema smart home ainda em modo simulado.",
                    location,
                )

            try:
                resposta = self.smart_home.controlar_tomada(location=location, action="turn_on")
                log(f"⚙️ Executor plug_on -> resposta={resposta}")
                return resposta
            except Exception as e:
                log(f"⚠️ Erro smart_home plug_on: {e}")
                return "Não consegui ligar a tomada."

        # ---------------------------------------------
        # SMART HOME - TOMADA OFF
        # ---------------------------------------------
        if intent == "smart_home.plug_off":
            location = entities.get("location")

            if not self.smart_home:
                return self._smart_home_indisponivel(
                    f"Tomada desligada em {location}. Sistema smart home ainda em modo simulado.",
                    "Tomada desligada. Sistema smart home ainda em modo simulado.",
                    location,
                )

            try:
                resposta = self.smart_home.controlar_tomada(location=location, action="turn_off")
                log(f"⚙️ Executor plug_off -> resposta={resposta}")
                return resposta
            except Exception as e:
                log(f"⚠️ Erro smart_home plug_off: {e}")
                return "Não consegui desligar a tomada."

        # ---------------------------------------------
        # SMART HOME - BRILHO ABSOLUTO
        # ---------------------------------------------
        if intent == "smart_home.light_set_brightness":
            location = entities.get("location")
            brightness = entities.get("brightness")

            if brightness is None:
                return "Não percebi o nível de brilho."

            try:
                brightness = int(brightness)
            except Exception:
                return "O valor do brilho é inválido."

            brightness = max(0, min(100, brightness))

            if not self.smart_home:
                return self._smart_home_indisponivel(
                    f"Brilho da luz em {location} ajustado para {brightness}%. Sistema smart home ainda em modo simulado.",
                    f"Brilho da luz ajustado para {brightness}%. Sistema smart home ainda em modo simulado.",
                    location,
                )

            try:
                resposta = self.smart_home.definir_brilho(location=location, brightness=brightness)
                log(f"⚙️ Executor brightness -> resposta={resposta}")
                return resposta
            except Exception as e:
                log(f"⚠️ Erro smart_home brightness: {e}")
                return "Não consegui ajustar o brilho da luz."

        # ---------------------------------------------
        # SMART HOME - BRILHO RELATIVO PARA CIMA
        # ---------------------------------------------
        if intent == "smart_home.light_brightness_up":
            location = entities.get("location")

            if not self.smart_home:
                return self._ajustar_brilho_relativo_simulado(location, "up")

            try:
                if hasattr(self.smart_home, "ajustar_brilho_relativo"):
                    resposta = self.smart_home.ajustar_brilho_relativo(location=location, direction="up")
                    log(f"⚙️ Executor light_brightness_up -> resposta={resposta}")
                    return resposta

                if hasattr(self.smart_home, "aumentar_brilho"):
                    resposta = self.smart_home.aumentar_brilho(location=location)
                    log(f"⚙️ Executor light_brightness_up -> resposta={resposta}")
                    return resposta

                return "A função de aumentar brilho ainda não está disponível."
            except Exception as e:
                log(f"⚠️ Erro smart_home light_brightness_up: {e}")
                return "Não consegui aumentar o brilho da luz."

        # ---------------------------------------------
        # SMART HOME - BRILHO RELATIVO PARA BAIXO
        # ---------------------------------------------
        if intent == "smart_home.light_brightness_down":
            location = entities.get("location")

            if not self.smart_home:
                return self._ajustar_brilho_relativo_simulado(location, "down")

            try:
                if hasattr(self.smart_home, "ajustar_brilho_relativo"):
                    resposta = self.smart_home.ajustar_brilho_relativo(location=location, direction="down")
                    log(f"⚙️ Executor light_brightness_down -> resposta={resposta}")
                    return resposta

                if hasattr(self.smart_home, "diminuir_brilho"):
                    resposta = self.smart_home.diminuir_brilho(location=location)
                    log(f"⚙️ Executor light_brightness_down -> resposta={resposta}")
                    return resposta

                return "A função de reduzir brilho ainda não está disponível."
            except Exception as e:
                log(f"⚠️ Erro smart_home light_brightness_down: {e}")
                return "Não consegui reduzir o brilho da luz."

        # ---------------------------------------------
        # SMART HOME - LUZ MAIS QUENTE
        # ---------------------------------------------
        if intent == "smart_home.light_warmer":
            location = entities.get("location")

            if not self.smart_home:
                return self._temperatura_luz_simulada(location, "warmer")

            try:
                if hasattr(self.smart_home, "ajustar_temperatura_luz"):
                    resposta = self.smart_home.ajustar_temperatura_luz(location=location, mode="warmer")
                    log(f"⚙️ Executor light_warmer -> resposta={resposta}")
                    return resposta

                if hasattr(self.smart_home, "luz_mais_quente"):
                    resposta = self.smart_home.luz_mais_quente(location=location)
                    log(f"⚙️ Executor light_warmer -> resposta={resposta}")
                    return resposta

                return "A função de luz mais quente ainda não está disponível."
            except Exception as e:
                log(f"⚠️ Erro smart_home light_warmer: {e}")
                return "Não consegui tornar a luz mais quente."

        # ---------------------------------------------
        # SMART HOME - LUZ MAIS FRIA
        # ---------------------------------------------
        if intent == "smart_home.light_cooler":
            location = entities.get("location")

            if not self.smart_home:
                return self._temperatura_luz_simulada(location, "cooler")

            try:
                if hasattr(self.smart_home, "ajustar_temperatura_luz"):
                    resposta = self.smart_home.ajustar_temperatura_luz(location=location, mode="cooler")
                    log(f"⚙️ Executor light_cooler -> resposta={resposta}")
                    return resposta

                if hasattr(self.smart_home, "luz_mais_fria"):
                    resposta = self.smart_home.luz_mais_fria(location=location)
                    log(f"⚙️ Executor light_cooler -> resposta={resposta}")
                    return resposta

                return "A função de luz mais fria ainda não está disponível."
            except Exception as e:
                log(f"⚠️ Erro smart_home light_cooler: {e}")
                return "Não consegui tornar a luz mais fria."

        # ---------------------------------------------
        # SMART HOME - TEMPORIZADOR PARA DESLIGAR LUZ
        # ---------------------------------------------
        if intent == "smart_home.light_off_timer":
            location = entities.get("location")
            minutes = entities.get("minutes")

            if minutes is None:
                return "Não percebi em quantos minutos queres apagar a luz."

            try:
                minutes = int(minutes)
            except Exception:
                return "O valor do temporizador é inválido."

            if minutes <= 0:
                return "O temporizador tem de ser maior que zero."

            if not self.smart_home:
                return self._smart_home_indisponivel(
                    f"Vou apagar a luz em {location} daqui a {minutes} minutos. Sistema smart home ainda em modo simulado.",
                    f"Vou apagar a luz daqui a {minutes} minutos. Sistema smart home ainda em modo simulado.",
                    location,
                )

            try:
                self._timer_desligar_luz(location=location, minutes=minutes)
            except Exception as e:
                log(f"⚠️ Erro ao criar temporizador da luz: {e}")
                return "Não consegui criar o temporizador da luz."

            if location:
                return f"Vou apagar a luz em {location} daqui a {minutes} minutos."

            return f"Vou apagar a luz daqui a {minutes} minutos."

        # ---------------------------------------------
        # SMART HOME - CENA CINEMA
        # ---------------------------------------------
        if intent == "smart_home.scene_cinema":
            location = entities.get("location")

            if not self.smart_home:
                return self._ativar_cena_simulada("cinema", location)

            if hasattr(self.smart_home, "modo_cinema"):
                try:
                    resposta = self.smart_home.modo_cinema(location=location)
                    log(f"⚙️ Executor scene_cinema -> resposta={resposta}")
                    return resposta
                except TypeError:
                    try:
                        resposta = self.smart_home.modo_cinema()
                        log(f"⚙️ Executor scene_cinema -> resposta={resposta}")
                        return resposta
                    except Exception as e:
                        log(f"⚠️ Erro smart_home scene_cinema: {e}")
                        return "Não consegui ativar o modo cinema."
                except Exception as e:
                    log(f"⚠️ Erro smart_home scene_cinema: {e}")
                    return "Não consegui ativar o modo cinema."

            return "O modo cinema ainda não está disponível."

        # ---------------------------------------------
        # SMART HOME - CENA RELAX
        # ---------------------------------------------
        if intent == "smart_home.scene_relax":
            location = entities.get("location")

            if not self.smart_home:
                return self._ativar_cena_simulada("relax", location)

            if hasattr(self.smart_home, "modo_relax"):
                try:
                    resposta = self.smart_home.modo_relax(location=location)
                    log(f"⚙️ Executor scene_relax -> resposta={resposta}")
                    return resposta
                except TypeError:
                    try:
                        resposta = self.smart_home.modo_relax()
                        log(f"⚙️ Executor scene_relax -> resposta={resposta}")
                        return resposta
                    except Exception as e:
                        log(f"⚠️ Erro smart_home scene_relax: {e}")
                        return "Não consegui ativar o modo relax."
                except Exception as e:
                    log(f"⚠️ Erro smart_home scene_relax: {e}")
                    return "Não consegui ativar o modo relax."

            return "O modo relax ainda não está disponível."

        # ---------------------------------------------
        # SMART HOME - CENA GAMING
        # ---------------------------------------------
        if intent == "smart_home.scene_gaming":
            location = entities.get("location")

            if not self.smart_home:
                return self._ativar_cena_simulada("gaming", location)

            if hasattr(self.smart_home, "modo_gaming"):
                try:
                    resposta = self.smart_home.modo_gaming(location=location)
                    log(f"⚙️ Executor scene_gaming -> resposta={resposta}")
                    return resposta
                except TypeError:
                    try:
                        resposta = self.smart_home.modo_gaming()
                        log(f"⚙️ Executor scene_gaming -> resposta={resposta}")
                        return resposta
                    except Exception as e:
                        log(f"⚠️ Erro smart_home scene_gaming: {e}")
                        return "Não consegui ativar o modo gaming."
                except Exception as e:
                    log(f"⚠️ Erro smart_home scene_gaming: {e}")
                    return "Não consegui ativar o modo gaming."

            return "O modo gaming ainda não está disponível."

        return "Ainda não sei executar esse comando."