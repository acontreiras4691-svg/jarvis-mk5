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
            "paris",
        ]

    # ==================================================
    # ROUTE
    # ==================================================

    def route_intent(self, texto: str) -> dict:

        texto_original = texto.strip()
        texto = self.normalizar(texto_original)

        # ---------------------------------------------
        # HORAS
        # ---------------------------------------------

        if self.is_time_question(texto):
            local = self.extract_world_location(texto)

            return {
                "type": "command",
                "intent": "assistant.time",
                "entities": {
                    "location": local
                },
                "confidence": 0.98,
            }

        # ---------------------------------------------
        # DATA
        # ---------------------------------------------

        if self.is_date_question(texto):
            local = self.extract_world_location(texto)

            return {
                "type": "command",
                "intent": "assistant.date",
                "entities": {
                    "location": local
                },
                "confidence": 0.98,
            }

        # ---------------------------------------------
        # DESLIGAR PC
        # ---------------------------------------------

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

        # ---------------------------------------------
        # REINICIAR PC
        # ---------------------------------------------

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

        # ---------------------------------------------
        # ABRIR APP
        # ---------------------------------------------

        if self.is_open_command(texto):
            app = self.extract_app(texto)

            if app:
                return {
                    "type": "command",
                    "intent": "system.open_app",
                    "entities": {
                        "app": app
                    },
                    "confidence": 0.95,
                }

        # ---------------------------------------------
        # SMART HOME - LIGAR LUZ
        # ---------------------------------------------

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

        # ---------------------------------------------
        # SMART HOME - DESLIGAR LUZ
        # ---------------------------------------------

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

        # ---------------------------------------------
        # SMART HOME - LIGAR TOMADA
        # ---------------------------------------------

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

        # ---------------------------------------------
        # SMART HOME - DESLIGAR TOMADA
        # ---------------------------------------------

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

        # ---------------------------------------------
        # CHAT / FALLBACK
        # ---------------------------------------------

        return {
            "type": "chat",
            "intent": "assistant.chat",
            "entities": {},
            "confidence": 0.50,
            "text": texto_original,
        }

    # ==================================================
    # NORMALIZAÇÃO
    # ==================================================

    def normalizar(self, texto: str) -> str:
        texto = texto.lower().strip()

        texto = "".join(
            c for c in unicodedata.normalize("NFD", texto)
            if unicodedata.category(c) != "Mn"
        )

        correcoes = {
            "abadi": "abre",
            "breed": "abre",
            "abri": "abre",
            "abra o": "abre",
            "abre o": "abre",
            "abrir o": "abre",
            "abre um": "abre",
            "abrir um": "abre",
            "que horas sao": "que horas sao",
            "horas sao": "horas",
            "suica": "suica",
            "suíça": "suica",
            "frança": "franca",
            "escritório": "escritorio",
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
                r"\blanca o\b",
                r"\blança o\b",
            ],
        )

    def is_time_question(self, texto: str) -> bool:
        return self.match_any(
            texto,
            [
                r"\bque horas sao\b",
                r"\bhoras\b",
                r"\bhora\b",
                r"\bque horas e\b",
            ],
        )

    def is_date_question(self, texto: str) -> bool:
        return self.match_any(
            texto,
            [
                r"\bque dia e hoje\b",
                r"\bque dia e\b",
                r"\bdata\b",
                r"\bdia de hoje\b",
                r"\bque data e hoje\b",
                r"\bque data e\b",
            ],
        )

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
                return location_norm
        return None

    def extract_world_location(self, texto: str):
        for location in self.world_locations:
            location_norm = self.normalizar(location)
            if location_norm in texto:
                if location_norm == "suica":
                    return "portugal" if False else "suica"
                return location_norm
        return None