# ==================================================
# 🎯 INTENT ROUTER - JARVIS MK5
# ==================================================

import re
import unicodedata


class IntentRouter:
    def __init__(self):
        self.apps = {
            "youtube": ["youtube", "you tube"],
            "chrome": ["chrome", "google chrome", "navegador"],
            "discord": ["discord"],
            "steam": ["steam"],
            "spotify": ["spotify"],
        }

        self.smart_locations = [
            "quarto",
            "sala",
            "cozinha",
            "escritorio",
            "escritório",
            "wc",
            "casa de banho",
            "corredor",
        ]

        self.world_locations = [
            "portugal",
            "lisboa",
            "porto",
            "suica",
            "suíça",
            "lausanne",
            "zurique",
            "reino unido",
            "londres",
            "franca",
            "frança",
            "espanha",
            "madrid",
            "paris",
        ]

        self.apple_tv_aliases = [
            "apple tv",
            "appletv",
            "tv",
        ]

    # ==================================================
    # ROUTE
    # ==================================================

    def route_intent(self, texto: str) -> dict:
        texto_original = texto.strip()
        texto = self.normalizar(texto_original)

        apple_tv_intent = self._route_apple_tv(texto)
        if apple_tv_intent:
            return apple_tv_intent

        if self.is_time_question(texto):
            local = self.extract_world_location(texto)
            tomorrow = "amanha" in texto

            return {
                "type": "command",
                "intent": "assistant.time",
                "entities": {
                    "location": local,
                    "tomorrow": tomorrow,
                },
                "confidence": 0.98,
            }

        if self.is_date_question(texto):
            local = self.extract_world_location(texto)
            tomorrow = "amanha" in texto

            return {
                "type": "command",
                "intent": "assistant.date",
                "entities": {
                    "location": local,
                    "tomorrow": tomorrow,
                },
                "confidence": 0.98,
            }

        if self.is_timer_off_command(texto):
            minutes = self.extract_minutes(texto)
            local = self.extract_smart_location(texto)

            return {
                "type": "command",
                "intent": "smart_home.light_off_timer",
                "entities": {
                    "location": local,
                    "device_type": "light",
                    "minutes": minutes,
                },
                "confidence": 0.92,
            }

        if self.is_brightness_command(texto):
            brightness = self.extract_brightness(texto)
            local = self.extract_smart_location(texto)

            return {
                "type": "command",
                "intent": "smart_home.light_set_brightness",
                "entities": {
                    "location": local,
                    "device_type": "light",
                    "brightness": brightness,
                },
                "confidence": 0.93,
            }

        if self.match_any(
            texto,
            [
                r"\bdesliga o computador\b",
                r"\bdesliga computador\b",
                r"\bdesliga o pc\b",
                r"\bdesliga pc\b",
                r"\bencerrar computador\b",
                r"\bencerrar pc\b",
            ],
        ):
            return {
                "type": "command",
                "intent": "system.shutdown",
                "entities": {},
                "confidence": 0.97,
                "requires_confirmation": True,
            }

        if self.match_any(
            texto,
            [
                r"\breinicia o computador\b",
                r"\breinicia computador\b",
                r"\breinicia o pc\b",
                r"\breinicia pc\b",
                r"\breiniciar computador\b",
                r"\breiniciar pc\b",
            ],
        ):
            return {
                "type": "command",
                "intent": "system.restart",
                "entities": {},
                "confidence": 0.97,
                "requires_confirmation": True,
            }

        if self.is_open_command(texto):
            app = self.extract_app(texto)
            if app:
                return {
                    "type": "command",
                    "intent": "system.open_app",
                    "entities": {"app": app},
                    "confidence": 0.95,
                }

        if self.match_any(
            texto,
            [
                r"\bacende\b",
                r"\bliga a luz\b",
                r"\bligar luz\b",
                r"\bativar luz\b",
                r"\bativa a luz\b",
            ],
        ):
            local = self.extract_smart_location(texto)
            return {
                "type": "command",
                "intent": "smart_home.light_on",
                "entities": {
                    "location": local,
                    "device_type": "light",
                    "action": "turn_on",
                },
                "confidence": 0.94,
            }

        if self.match_any(
            texto,
            [
                r"\bapaga\b",
                r"\bdesliga a luz\b",
                r"\bapagar luz\b",
                r"\bdesligar luz\b",
            ],
        ):
            local = self.extract_smart_location(texto)
            return {
                "type": "command",
                "intent": "smart_home.light_off",
                "entities": {
                    "location": local,
                    "device_type": "light",
                    "action": "turn_off",
                },
                "confidence": 0.94,
            }

        if self.match_any(
            texto,
            [
                r"\bliga a tomada\b",
                r"\bligar tomada\b",
                r"\bativa a tomada\b",
                r"\bativar tomada\b",
            ],
        ):
            local = self.extract_smart_location(texto)
            return {
                "type": "command",
                "intent": "smart_home.plug_on",
                "entities": {
                    "location": local,
                    "device_type": "plug",
                    "action": "turn_on",
                },
                "confidence": 0.93,
            }

        if self.match_any(
            texto,
            [
                r"\bdesliga a tomada\b",
                r"\bdesligar tomada\b",
                r"\bapaga a tomada\b",
                r"\bdesativar tomada\b",
            ],
        ):
            local = self.extract_smart_location(texto)
            return {
                "type": "command",
                "intent": "smart_home.plug_off",
                "entities": {
                    "location": local,
                    "device_type": "plug",
                    "action": "turn_off",
                },
                "confidence": 0.93,
            }

        return {
            "type": "chat",
            "intent": "assistant.chat",
            "entities": {},
            "confidence": 0.50,
            "text": texto_original,
        }

    # ==================================================
    # APPLE TV
    # ==================================================

    def _route_apple_tv(self, texto: str):
        texto = self.normalizar(texto)

        if not self.tem_apple_tv(texto):
            return None

        # ------------------------------------------------
        # MACROS DE APPS SUPORTADAS
        # ------------------------------------------------
        if "youtube" in texto:
            return self._apple_tv_intent(
                "media.apple_tv_open_youtube",
                {"action": "open_youtube"},
                0.97,
            )

        if "netflix" in texto:
            return self._apple_tv_intent(
                "media.apple_tv_open_netflix",
                {"action": "open_netflix"},
                0.97,
            )

        # ------------------------------------------------
        # COMANDOS REMOTOS SUPORTADOS
        # ------------------------------------------------
        if self.match_any(texto, [r"\bpausa\b", r"\bpausar\b", r"\bmete em pausa\b"]):
            return self._apple_tv_intent(
                "media.apple_tv_pause",
                {"action": "pause"},
                0.98,
            )

        if self.match_any(texto, [r"\bcontinua\b", r"\bcontinuar\b", r"\bplay\b", r"\breproduz\b"]):
            return self._apple_tv_intent(
                "media.apple_tv_play",
                {"action": "play"},
                0.98,
            )

        if "menu" in texto:
            return self._apple_tv_intent(
                "media.apple_tv_menu",
                {"action": "menu"},
                0.97,
            )

        if self.match_any(texto, [r"\bhome\b", r"\binicio\b", r"\becra principal\b", r"\becran principal\b"]):
            return self._apple_tv_intent(
                "media.apple_tv_home",
                {"action": "home"},
                0.97,
            )

        if "esquerda" in texto:
            return self._apple_tv_intent(
                "media.apple_tv_left",
                {"action": "left"},
                0.97,
            )

        if "direita" in texto:
            return self._apple_tv_intent(
                "media.apple_tv_right",
                {"action": "right"},
                0.97,
            )

        if self.match_any(texto, [r"\bcima\b", r"\bpara cima\b"]):
            return self._apple_tv_intent(
                "media.apple_tv_up",
                {"action": "up"},
                0.97,
            )

        if self.match_any(texto, [r"\bbaixo\b", r"\bpara baixo\b"]):
            return self._apple_tv_intent(
                "media.apple_tv_down",
                {"action": "down"},
                0.97,
            )

        if self.match_any(texto, [r"\bseleciona\b", r"\bconfirma\b", r"\bok\b", r"\benter\b"]):
            return self._apple_tv_intent(
                "media.apple_tv_select",
                {"action": "select"},
                0.96,
            )

        if self.match_any(texto, [r"\bseguinte\b", r"\bproximo\b", r"\bavanca\b"]):
            return self._apple_tv_intent(
                "media.apple_tv_next",
                {"action": "next"},
                0.95,
            )

        if self.match_any(texto, [r"\banterior\b", r"\bvolta atras\b"]):
            return self._apple_tv_intent(
                "media.apple_tv_previous",
                {"action": "previous"},
                0.95,
            )

        # Se disse só "apple tv" ou "na tv" sem ação concreta
        return None

    def tem_apple_tv(self, texto: str) -> bool:
        texto = self.normalizar(texto)

        if "apple tv" in texto or "appletv" in texto:
            return True

        if "na tv" in texto:
            return True

        if "tv" in texto and self.match_any(
            texto,
            [
                r"\bmenu\b",
                r"\bhome\b",
                r"\bpausa\b",
                r"\bplay\b",
                r"\bcontinua\b",
                r"\bseleciona\b",
                r"\bconfirma\b",
                r"\bcima\b",
                r"\bbaixo\b",
                r"\besquerda\b",
                r"\bdireita\b",
                r"\byoutube\b",
                r"\bnetflix\b",
            ],
        ):
            return True

        return False

    def _apple_tv_intent(self, intent: str, entities: dict, confidence: float):
        return {
            "type": "command",
            "intent": intent,
            "entities": entities,
            "confidence": confidence,
        }

    # ==================================================
    # NORMALIZAR
    # ==================================================

    def normalizar(self, texto: str) -> str:
        texto = texto.lower().strip()

        texto = "".join(
            c for c in unicodedata.normalize("NFD", texto)
            if unicodedata.category(c) != "Mn"
        )

        correcoes = {
            "abadi": "abre",
            "abdo": "abre",
            "abro": "abre",
            "abri": "abre",
            "abre o": "abre",
            "abre a": "abre",
            "abra o": "abre",
            "abra a": "abre",
            "abrir o": "abre",
            "abrir a": "abre",
            "abre um": "abre",
            "abrir um": "abre",
            "you tube": "youtube",
            "appletv": "apple tv",
            "suíça": "suica",
            "frança": "franca",
            "escritório": "escritorio",
            "amanhã": "amanha",
            "próximo": "proximo",
            "avança": "avanca",
            "atrás": "atras",
            "ecrã": "ecra",
        }

        for erro, correto in correcoes.items():
            texto = texto.replace(erro, correto)

        texto = re.sub(r"[^\w\s]", " ", texto)
        texto = re.sub(r"\s+", " ", texto).strip()

        return texto

    # ==================================================
    # HELPERS
    # ==================================================

    def match_any(self, texto: str, patterns: list[str]) -> bool:
        return any(re.search(pattern, texto) for pattern in patterns)

    def is_open_command(self, texto: str) -> bool:
        return self.match_any(
            texto,
            [
                r"\babre\b",
                r"\babrir\b",
                r"\babra\b",
                r"\binicia\b",
                r"\blanca\b",
                r"\blança\b",
            ],
        )

    def is_time_question(self, texto: str) -> bool:
        return self.match_any(
            texto,
            [
                r"\bque horas sao\b",
                r"\bhora\b",
                r"\bhoras\b",
            ],
        )

    def is_date_question(self, texto: str) -> bool:
        return self.match_any(
            texto,
            [
                r"\bque dia e hoje\b",
                r"\bque dia e\b",
                r"\bque data e hoje\b",
                r"\bque data e\b",
                r"\bdata\b",
                r"\bdia de hoje\b",
            ],
        )

    def is_brightness_command(self, texto: str) -> bool:
        return self.match_any(
            texto,
            [
                r"\bbaixa\b",
                r"\baumenta\b",
                r"\bmete para\b",
                r"\bpoe para\b",
                r"\bpõe para\b",
                r"\bmetade\b",
                r"\bbrilho\b",
                r"\bintensidade\b",
            ],
        )

    def is_timer_off_command(self, texto: str) -> bool:
        return self.match_any(
            texto,
            [
                r"\bapaga daqui a\b",
                r"\bdesliga daqui a\b",
                r"\bapaga em\b",
                r"\bdesliga em\b",
            ],
        )

    def extract_brightness(self, texto: str):
        if "metade" in texto:
            return 50

        match = re.search(r"(\d{1,3})\s*%", texto)
        if match:
            value = int(match.group(1))
            return max(0, min(100, value))

        match = re.search(r"\b(\d{1,3})\s*por cento\b", texto)
        if match:
            value = int(match.group(1))
            return max(0, min(100, value))

        if "minimo" in texto:
            return 10

        if "maximo" in texto:
            return 100

        if "baixa" in texto:
            return 50

        if "aumenta" in texto:
            return 80

        return None

    def extract_minutes(self, texto: str):
        match = re.search(r"(\d+)\s*minutos\b", texto)
        if match:
            return int(match.group(1))

        match = re.search(r"(\d+)\s*min\b", texto)
        if match:
            return int(match.group(1))

        return None

    def extract_app(self, texto: str):
        for app, aliases in self.apps.items():
            for alias in aliases:
                alias_norm = self.normalizar(alias)
                if alias_norm in texto:
                    return app
        return None

    def extract_smart_location(self, texto: str):
        for location in self.smart_locations:
            location_norm = self.normalizar(location)
            if location_norm in texto:
                if location_norm == "escritorio":
                    return "escritório"
                if location_norm == "casa de banho":
                    return "wc"
                return location_norm
        return None

    def extract_world_location(self, texto: str):
        for location in self.world_locations:
            location_norm = self.normalizar(location)
            if location_norm in texto:
                return location_norm
        return None