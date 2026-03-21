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

        self.location_aliases = {
            "quarto": ["quarto", "meu quarto"],
            "sala": ["sala", "sala de estar"],
            "cozinha": ["cozinha"],
            "escritório": ["escritorio", "escritório", "office"],
            "wc": ["wc", "casa de banho", "casa banho", "banho"],
            "corredor": ["corredor"],
        }

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

    # ==================================================
    # API PRINCIPAL
    # ==================================================

    def detectar_intencao(self, texto: str) -> dict:
        texto_original = (texto or "").strip()
        texto = self.normalizar(texto_original)

        if not texto:
            return {
                "type": "chat",
                "intent": "assistant.chat",
                "entities": {},
                "confidence": 0.0,
                "text": texto_original,
            }

        # ---------------------------------------------
        # SMALL TALK
        # ---------------------------------------------
        if self.is_greeting(texto):
            return {
                "type": "chat",
                "intent": "assistant.greeting",
                "entities": {},
                "confidence": 0.99,
                "text": texto_original,
            }

        if self.is_thanks(texto):
            return {
                "type": "chat",
                "intent": "assistant.thanks",
                "entities": {},
                "confidence": 0.99,
                "text": texto_original,
            }

        if self.is_goodbye(texto):
            return {
                "type": "chat",
                "intent": "assistant.goodbye",
                "entities": {},
                "confidence": 0.99,
                "text": texto_original,
            }

        # ---------------------------------------------
        # CENAS / MODOS
        # ---------------------------------------------
        cena = self.extract_scene(texto)
        if cena:
            return {
                "type": "command",
                "intent": f"smart_home.scene_{cena}",
                "entities": {
                    "scene": cena,
                    "location": self.extract_smart_location(texto),
                    "device_type": "light",
                },
                "confidence": 0.97,
                "requires_confirmation": False,
            }

        # ---------------------------------------------
        # HORAS
        # ---------------------------------------------
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
                "requires_confirmation": False,
            }

        # ---------------------------------------------
        # DATA
        # ---------------------------------------------
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
                "requires_confirmation": False,
            }

        # ---------------------------------------------
        # COR / TEMPERATURA
        # ---------------------------------------------
        if self.is_color_warmer_command(texto):
            return {
                "type": "command",
                "intent": "smart_home.light_warmer",
                "entities": {
                    "location": self.extract_smart_location(texto),
                    "device_type": "light",
                    "color_mode": "warmer",
                },
                "confidence": 0.93,
                "requires_confirmation": False,
            }

        if self.is_color_cooler_command(texto):
            return {
                "type": "command",
                "intent": "smart_home.light_cooler",
                "entities": {
                    "location": self.extract_smart_location(texto),
                    "device_type": "light",
                    "color_mode": "cooler",
                },
                "confidence": 0.93,
                "requires_confirmation": False,
            }

        # ---------------------------------------------
        # BRILHO RELATIVO
        # ---------------------------------------------
        if self.is_brightness_up_command(texto):
            return {
                "type": "command",
                "intent": "smart_home.light_brightness_up",
                "entities": {
                    "location": self.extract_smart_location(texto),
                    "device_type": "light",
                    "direction": "up",
                },
                "confidence": 0.92,
                "requires_confirmation": False,
            }

        if self.is_brightness_down_command(texto):
            return {
                "type": "command",
                "intent": "smart_home.light_brightness_down",
                "entities": {
                    "location": self.extract_smart_location(texto),
                    "device_type": "light",
                    "direction": "down",
                },
                "confidence": 0.92,
                "requires_confirmation": False,
            }

        # ---------------------------------------------
        # BRILHO / INTENSIDADE ABSOLUTO
        # ---------------------------------------------
        if self.is_brightness_command(texto):
            brightness = self.extract_brightness(texto)
            local = self.extract_smart_location(texto)

            if brightness is not None:
                return {
                    "type": "command",
                    "intent": "smart_home.light_set_brightness",
                    "entities": {
                        "location": local,
                        "device_type": "light",
                        "brightness": brightness,
                    },
                    "confidence": 0.93,
                    "requires_confirmation": False,
                }

        # ---------------------------------------------
        # TEMPORIZADOR / DELAY OFF
        # ---------------------------------------------
        if self.is_timer_off_command(texto):
            minutes = self.extract_minutes(texto)
            local = self.extract_smart_location(texto)

            if minutes is not None:
                return {
                    "type": "command",
                    "intent": "smart_home.light_off_timer",
                    "entities": {
                        "location": local,
                        "device_type": "light",
                        "minutes": minutes,
                    },
                    "confidence": 0.92,
                    "requires_confirmation": False,
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
                r"\bdesligar computador\b",
                r"\bdesligar pc\b",
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
                r"\breinicia maquina\b",
                r"\breiniciar maquina\b",
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
                    "entities": {"app": app},
                    "confidence": 0.95,
                    "requires_confirmation": False,
                }

        # ---------------------------------------------
        # SMART HOME - TOMADA ON
        # ---------------------------------------------
        if self.is_plug_on_command(texto):
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
                "requires_confirmation": False,
            }

        # ---------------------------------------------
        # SMART HOME - TOMADA OFF
        # ---------------------------------------------
        if self.is_plug_off_command(texto):
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
                "requires_confirmation": False,
            }

        # ---------------------------------------------
        # SMART HOME - LUZ OFF
        # ---------------------------------------------
        if self.is_light_off_command(texto):
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
                "requires_confirmation": False,
            }

        # ---------------------------------------------
        # SMART HOME - LUZ ON
        # ---------------------------------------------
        if self.is_light_on_command(texto):
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
                "requires_confirmation": False,
            }

        # ---------------------------------------------
        # INFERÊNCIAS MAIS HUMANAS
        # ---------------------------------------------
        inferred = self.infer_human_phrase(texto)
        if inferred:
            return inferred

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

    def route_intent(self, texto: str) -> dict:
        return self.detectar_intencao(texto)

    # ==================================================
    # NORMALIZAR
    # ==================================================

    def normalizar(self, texto: str) -> str:
        texto = (texto or "").lower().strip()

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
            "suíça": "suica",
            "frança": "franca",
            "escritório": "escritorio",
            "amanhã": "amanha",
            "casa de banho": "wc",
            "casa banho": "wc",
            "por": "poe",
            "pôr": "poe",
            "põe": "poe",
            "mínimo": "minimo",
            "máximo": "maximo",
            "quadro": "quarto",
            "cinmea": "cinema",
            "simnea": "cinema",
            "filmea": "filme",
        }

        for erro, correto in correcoes.items():
            texto = texto.replace(erro, correto)

        texto = re.sub(r"[^\w\s%]", " ", texto)
        texto = re.sub(r"\s+", " ", texto).strip()

        return texto

    # ==================================================
    # HELPERS GERAIS
    # ==================================================

    def match_any(self, texto: str, patterns: list[str]) -> bool:
        return any(re.search(pattern, texto) for pattern in patterns)

    def extract_by_alias(self, texto: str, aliases_map: dict):
        for canonical, aliases in aliases_map.items():
            for alias in aliases:
                alias_norm = self.normalizar(alias)
                if alias_norm in texto:
                    return canonical
        return None

    # ==================================================
    # SMALL TALK
    # ==================================================

    def is_greeting(self, texto: str) -> bool:
        return self.match_any(
            texto,
            [
                r"\bola\b",
                r"\bbom dia\b",
                r"\bboa tarde\b",
                r"\bboa noite\b",
                r"\bhello\b",
                r"\bhey\b",
            ],
        )

    def is_thanks(self, texto: str) -> bool:
        return self.match_any(
            texto,
            [
                r"\bobrigado\b",
                r"\bobrigada\b",
                r"\bthanks\b",
                r"\bagradecido\b",
            ],
        )

    def is_goodbye(self, texto: str) -> bool:
        return self.match_any(
            texto,
            [
                r"\badeus\b",
                r"\bate ja\b",
                r"\bate logo\b",
                r"\bsee you\b",
                r"\btchau\b",
                r"\bchau\b",
            ],
        )

    # ==================================================
    # HELPERS DE INTENÇÃO
    # ==================================================

    def is_open_command(self, texto: str) -> bool:
        return self.match_any(
            texto,
            [
                r"\babre\b",
                r"\babrir\b",
                r"\babra\b",
                r"\binicia\b",
                r"\blanca\b",
            ],
        )

    def is_time_question(self, texto: str) -> bool:
        return self.match_any(
            texto,
            [
                r"\bque horas sao\b",
                r"\bque hora e\b",
                r"\bhoras\b",
                r"\bhora\b",
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
                r"\bqual e a data\b",
                r"\bestamos em que dia\b",
                r"\bque dia estamos\b",
                r"\bem que dia estamos\b",
                r"\bhoje e que dia\b",
            ],
        )

    def is_brightness_command(self, texto: str) -> bool:
        return self.match_any(
            texto,
            [
                r"\bbaixa.*\bbrilho\b",
                r"\baumenta.*\bbrilho\b",
                r"\bmete.*\d{1,3}\s*%\b",
                r"\bpoe.*\d{1,3}\s*%\b",
                r"\bbrilho\b",
                r"\bintensidade\b",
                r"\bmetade\b",
                r"\bminimo\b",
                r"\bmaximo\b",
                r"\b\d{1,3}\s*%\b",
                r"\ba\s*\d{1,3}\s*%\b",
            ],
        )

    def is_brightness_up_command(self, texto: str) -> bool:
        return self.match_any(
            texto,
            [
                r"\bmais claro\b",
                r"\bmais luz\b",
                r"\baumenta\b",
                r"\baumenta a luz\b",
                r"\baumenta o brilho\b",
                r"\bsobe o brilho\b",
                r"\bpoe mais luz\b",
            ],
        )

    def is_brightness_down_command(self, texto: str) -> bool:
        return self.match_any(
            texto,
            [
                r"\bmais escuro\b",
                r"\bmenos luz\b",
                r"\bpouca luz\b",
                r"\bbaixa\b",
                r"\bbaixa a luz\b",
                r"\bbaixa o brilho\b",
                r"\besta muito claro\b",
                r"\bta muito claro\b",
            ],
        )

    def is_color_warmer_command(self, texto: str) -> bool:
        return self.match_any(
            texto,
            [
                r"\bmais quente\b",
                r"\bluz quente\b",
                r"\bmais acolhedor\b",
                r"\btom quente\b",
                r"\bpoe mais quente\b",
                r"\bmete mais quente\b",
            ],
        )

    def is_color_cooler_command(self, texto: str) -> bool:
        return self.match_any(
            texto,
            [
                r"\bmais fria\b",
                r"\bluz fria\b",
                r"\btom frio\b",
                r"\bpoe mais fria\b",
                r"\bmete mais fria\b",
                r"\bmais branco\b",
            ],
        )

    def is_timer_off_command(self, texto: str) -> bool:
        return self.match_any(
            texto,
            [
                r"\bapaga.*\bem\b.*\bmin",
                r"\bdesliga.*\bem\b.*\bmin",
                r"\bapaga.*\bminutos?",
                r"\bdesliga.*\bminutos?",
            ],
        )

    def is_light_on_command(self, texto: str) -> bool:
        return self.match_any(
            texto,
            [
                r"\bacende\b",
                r"\bliga a luz\b",
                r"\bligar luz\b",
                r"\bativar luz\b",
                r"\bativa a luz\b",
                r"\bliga luz\b",
                r"\bliga\b",
            ],
        )

    def is_light_off_command(self, texto: str) -> bool:
        return self.match_any(
            texto,
            [
                r"\bapaga\b",
                r"\bdesliga a luz\b",
                r"\bapagar luz\b",
                r"\bdesligar luz\b",
                r"\bdesliga luz\b",
                r"\bdesliga\b",
                r"\bmete as escuras\b",
                r"\bmete as oscuras\b",
            ],
        )

    def is_plug_on_command(self, texto: str) -> bool:
        return self.match_any(
            texto,
            [
                r"\bliga a tomada\b",
                r"\bligar tomada\b",
                r"\bativa a tomada\b",
                r"\bativar tomada\b",
                r"\bliga tomada\b",
            ],
        )

    def is_plug_off_command(self, texto: str) -> bool:
        return self.match_any(
            texto,
            [
                r"\bdesliga a tomada\b",
                r"\bdesligar tomada\b",
                r"\bapaga a tomada\b",
                r"\bdesativar tomada\b",
                r"\bdesliga tomada\b",
            ],
        )

    # ==================================================
    # EXTRAÇÃO
    # ==================================================

    def extract_brightness(self, texto: str):
        match = re.search(r"(\d{1,3})\s*%", texto)
        if match:
            value = int(match.group(1))
            return max(0, min(100, value))

        if "metade" in texto:
            return 50

        if "minimo" in texto:
            return 10

        if "maximo" in texto:
            return 100

        if "baixa o brilho" in texto or "menos brilho" in texto:
            return 40

        if "aumenta o brilho" in texto or "mais brilho" in texto:
            return 80

        return None

    def extract_minutes(self, texto: str):
        match = re.search(r"(\d+)\s*minutos?", texto)
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
        return self.extract_by_alias(texto, self.location_aliases)

    def extract_world_location(self, texto: str):
        for location in self.world_locations:
            location_norm = self.normalizar(location)
            if location_norm in texto:
                return location_norm
        return None

    def extract_scene(self, texto: str):
        if self.match_any(
            texto,
            [
                r"\bmodo cinema\b",
                r"\bcinema\b",
                r"\bmodo filme\b",
                r"\bmodo ver filme\b",
                r"\bmodo ver um filme\b",
                r"\bver filme\b",
                r"\bver um filme\b",
            ],
        ):
            return "cinema"

        if self.match_any(
            texto,
            [
                r"\bmodo relax\b",
                r"\brelax\b",
                r"\bambiente relax\b",
                r"\bquero ambiente\b",
                r"\bluz ambiente\b",
                r"\bmodo ambiente\b",
            ],
        ):
            return "relax"

        if self.match_any(
            texto,
            [
                r"\bmodo gaming\b",
                r"\bgaming\b",
                r"\bjogar\b",
                r"\bmodo jogo\b",
            ],
        ):
            return "gaming"

        return None

    # ==================================================
    # INFERÊNCIA DE FRASES MAIS HUMANAS
    # ==================================================

    def infer_human_phrase(self, texto: str):
        local = self.extract_smart_location(texto)

        # ---------------------------------------------
        # RELAX / CONFORTO
        # ---------------------------------------------
        if self.match_any(
            texto,
            [
                r"\bestou com sono\b",
                r"\bquero descansar\b",
                r"\bquero relaxar\b",
                r"\bquero ambiente\b",
                r"\bquero algo confortavel\b",
                r"\bquero uma coisa suave\b",
                r"\bmete isto mais confortavel\b",
                r"\bquero uma luz suave\b",
            ],
        ):
            return {
                "type": "command",
                "intent": "smart_home.scene_relax",
                "entities": {
                    "scene": "relax",
                    "location": local,
                    "device_type": "light",
                },
                "confidence": 0.89,
                "requires_confirmation": False,
            }

        # ---------------------------------------------
        # GAMING
        # ---------------------------------------------
        if self.match_any(
            texto,
            [
                r"\bestou a jogar\b",
                r"\bquero jogar\b",
                r"\bvou jogar\b",
                r"\bmete modo jogo\b",
                r"\bprepara ambiente de jogo\b",
            ],
        ):
            return {
                "type": "command",
                "intent": "smart_home.scene_gaming",
                "entities": {
                    "scene": "gaming",
                    "location": local,
                    "device_type": "light",
                },
                "confidence": 0.89,
                "requires_confirmation": False,
            }

        # ---------------------------------------------
        # CINEMA / FILME / SÉRIE
        # ---------------------------------------------
        if self.match_any(
            texto,
            [
                r"\bestou a ver um filme\b",
                r"\bquero ver um filme\b",
                r"\bvou ver um filme\b",
                r"\bquero ver uma serie\b",
                r"\bvou ver uma serie\b",
                r"\bmete ambiente de cinema\b",
            ],
        ):
            return {
                "type": "command",
                "intent": "smart_home.scene_cinema",
                "entities": {
                    "scene": "cinema",
                    "location": local,
                    "device_type": "light",
                },
                "confidence": 0.89,
                "requires_confirmation": False,
            }

        # ---------------------------------------------
        # MAIS ESCURO / MENOS LUZ
        # ---------------------------------------------
        if self.match_any(
            texto,
            [
                r"\besta muito claro\b",
                r"\bta muito claro\b",
                r"\bquero menos luz\b",
                r"\bisto esta muito forte\b",
                r"\bbaixa isso\b",
                r"\bmete menos luz\b",
            ],
        ):
            return {
                "type": "command",
                "intent": "smart_home.light_brightness_down",
                "entities": {
                    "location": local,
                    "device_type": "light",
                    "direction": "down",
                },
                "confidence": 0.87,
                "requires_confirmation": False,
            }

        # ---------------------------------------------
        # MAIS LUZ / MAIS CLARO
        # ---------------------------------------------
        if self.match_any(
            texto,
            [
                r"\besta muito escuro\b",
                r"\bquero mais luz\b",
                r"\bmete mais luz\b",
                r"\bisto esta escuro\b",
                r"\baumenta isso\b",
            ],
        ):
            return {
                "type": "command",
                "intent": "smart_home.light_brightness_up",
                "entities": {
                    "location": local,
                    "device_type": "light",
                    "direction": "up",
                },
                "confidence": 0.87,
                "requires_confirmation": False,
            }

        # ---------------------------------------------
        # TOM MAIS QUENTE
        # ---------------------------------------------
        if self.match_any(
            texto,
            [
                r"\bnao gosto desta luz\b",
                r"\bquero isto mais aconchegante\b",
                r"\bquero isto mais quente\b",
                r"\besta muito frio\b",
                r"\bmete isto mais acolhedor\b",
            ],
        ):
            return {
                "type": "command",
                "intent": "smart_home.light_warmer",
                "entities": {
                    "location": local,
                    "device_type": "light",
                    "color_mode": "warmer",
                },
                "confidence": 0.86,
                "requires_confirmation": False,
            }

        return None