# ==================================================
# 🏠 SMART HOME MANAGER - JARVIS MK5
# WC real + resto simulado
# ==================================================

from core.logger import log

# --------------------------------------------------
# IMPORT FLEXÍVEL DO CONTROLADOR WC
# --------------------------------------------------
# Isto evita crash caso o nome real da classe varie
# entre WcTuyaController / WCTuyaController / etc.
# --------------------------------------------------

try:
    from smart_home.wc_tuya_controller import WcTuyaController
except ImportError:
    try:
        from smart_home.wc_tuya_controller import WCTuyaController as WcTuyaController
    except ImportError:
        WcTuyaController = None


class SmartHomeManager:
    def __init__(self):
        self.wc_controller = None

        # mete aqui os teus dados reais da luz WC
        if WcTuyaController is not None:
            try:
                self.wc_controller = WcTuyaController(
                    device_id="bfcdaf6c99ef575ce9byxu",
                    ip="192.168.1.70",
                    local_key="v4TA0[}GqOwMdA;5",
                    version=3.5,
                )
                log("💡 WC real inicializado com sucesso.")
            except Exception as e:
                log(f"⚠️ Falha ao iniciar controlador real do WC: {e}")
                self.wc_controller = None
        else:
            log("⚠️ Controlador WC não encontrado em wc_tuya_controller.py")

        self.luzes = {
            "quarto": {"state": "off", "brightness": 100},
            "wc": {"state": "off", "brightness": 100},
            "sala": {"state": "off", "brightness": 100},
            "cozinha": {"state": "off", "brightness": 100},
            "escritorio": {"state": "off", "brightness": 100},
            "escritório": {"state": "off", "brightness": 100},
            "corredor": {"state": "off", "brightness": 100},
        }

        self.tomadas = {
            "quarto": {"state": "off"},
            "wc": {"state": "off"},
            "sala": {"state": "off"},
            "cozinha": {"state": "off"},
            "escritorio": {"state": "off"},
            "escritório": {"state": "off"},
            "corredor": {"state": "off"},
        }

        log("🏠 SmartHomeManager iniciado.")

    # ==================================================
    # HELPERS
    # ==================================================

    def _normalizar_local(self, location):
        if not location:
            return None

        location = str(location).lower().strip()
        mapa = {
            "casa de banho": "wc",
            "banho": "wc",
            "escritório": "escritorio",
        }
        return mapa.get(location, location)

    def _wc_disponivel(self):
        return self.wc_controller is not None

    def _wc_turn_on(self):
        if hasattr(self.wc_controller, "turn_on"):
            return self.wc_controller.turn_on()
        if hasattr(self.wc_controller, "ligar"):
            return self.wc_controller.ligar()
        raise AttributeError("Controlador WC sem método turn_on/ligar")

    def _wc_turn_off(self):
        if hasattr(self.wc_controller, "turn_off"):
            return self.wc_controller.turn_off()
        if hasattr(self.wc_controller, "desligar"):
            return self.wc_controller.desligar()
        raise AttributeError("Controlador WC sem método turn_off/desligar")

    def _wc_set_brightness(self, brightness):
        if hasattr(self.wc_controller, "set_brightness"):
            return self.wc_controller.set_brightness(brightness)
        if hasattr(self.wc_controller, "definir_brilho"):
            return self.wc_controller.definir_brilho(brightness)
        raise AttributeError("Controlador WC sem método set_brightness/definir_brilho")

    def _wc_brightness_up(self):
        if hasattr(self.wc_controller, "brightness_up"):
            return self.wc_controller.brightness_up()
        raise AttributeError("Controlador WC sem método brightness_up")

    def _wc_brightness_down(self):
        if hasattr(self.wc_controller, "brightness_down"):
            return self.wc_controller.brightness_down()
        raise AttributeError("Controlador WC sem método brightness_down")

    # ==================================================
    # LUZ
    # ==================================================

    def controlar_luz(self, location=None, action="turn_on"):
        location = self._normalizar_local(location)

        if not location:
            return "Falta dizer-me em que divisão queres mexer na luz, Dudu."

        if location == "wc":
            if not self._wc_disponivel():
                return "O controlador real do wc não está disponível."

            try:
                if action == "turn_on":
                    self._wc_turn_on()
                    self.luzes["wc"]["state"] = "on"
                    return "Luz ligada em wc."

                if action == "turn_off":
                    self._wc_turn_off()
                    self.luzes["wc"]["state"] = "off"
                    return "Luz desligada em wc."

                return "Não percebi o comando para a luz."

            except Exception as e:
                log(f"⚠️ Erro a controlar luz real do WC: {e}")
                return "Não consegui controlar a luz real do wc."

        if location in self.luzes:
            if action == "turn_on":
                self.luzes[location]["state"] = "on"
                return f"Luz ligada em {location}."

            if action == "turn_off":
                self.luzes[location]["state"] = "off"
                return f"Luz desligada em {location}."

            return "Não percebi o comando para a luz."

        return f"Não conheço a divisão {location}, Dudu."

    # ==================================================
    # BRILHO
    # ==================================================

    def definir_brilho(self, location=None, brightness=None):
        location = self._normalizar_local(location)

        if not location:
            return "Falta dizer-me a divisão."

        if brightness is None:
            return "Não percebi o nível de brilho."

        try:
            brightness = int(brightness)
        except Exception:
            return "O valor do brilho não é válido."

        brightness = max(0, min(100, brightness))

        if location == "wc":
            if not self._wc_disponivel():
                return "O controlador real do wc não está disponível."

            try:
                self._wc_set_brightness(brightness)
                self.luzes["wc"]["brightness"] = brightness
                self.luzes["wc"]["state"] = "on" if brightness > 0 else "off"
                return f"Luz em wc ajustada para {brightness}%."
            except Exception as e:
                log(f"⚠️ Erro a ajustar brilho real do WC: {e}")
                return "Não consegui ajustar o brilho real do wc."

        if location in self.luzes:
            self.luzes[location]["brightness"] = brightness
            self.luzes[location]["state"] = "on" if brightness > 0 else "off"
            return f"Luz em {location} ajustada para {brightness}%."

        return f"Não conheço a divisão {location}, Dudu."

    def controlar_brilho(self, location=None, brightness=None):
        return self.definir_brilho(location=location, brightness=brightness)

    def ajustar_brilho_relativo(self, location=None, direction="up"):
        location = self._normalizar_local(location)

        if not location:
            return "Falta dizer-me a divisão."

        if location == "wc":
            if not self._wc_disponivel():
                return "O controlador real do wc não está disponível."

            try:
                if direction == "up":
                    self._wc_brightness_up()
                    return "Brilho aumentado em wc."

                self._wc_brightness_down()
                return "Brilho reduzido em wc."

            except Exception as e:
                log(f"⚠️ Erro no brilho relativo real do WC: {e}")
                return "Não consegui ajustar o brilho real do wc."

        if location in self.luzes:
            atual = self.luzes[location]["brightness"]
            passo = 20
            novo = min(100, atual + passo) if direction == "up" else max(0, atual - passo)
            self.luzes[location]["brightness"] = novo
            self.luzes[location]["state"] = "on" if novo > 0 else "off"
            return f"Brilho {'aumentado' if direction == 'up' else 'reduzido'} em {location}."

        return f"Não conheço a divisão {location}, Dudu."

    def aumentar_brilho(self, location=None):
        return self.ajustar_brilho_relativo(location=location, direction="up")

    def diminuir_brilho(self, location=None):
        return self.ajustar_brilho_relativo(location=location, direction="down")

    # ==================================================
    # TEMPERATURA / COR
    # ==================================================

    def ajustar_temperatura_luz(self, location=None, mode="warmer"):
        location = self._normalizar_local(location)

        if not location:
            return "Falta dizer-me a divisão."

        if location == "wc":
            return "A luz do wc não tem temperatura implementada."

        if location in self.luzes:
            return f"Luz {'mais quente' if mode == 'warmer' else 'mais fria'} em {location}."

        return f"Não conheço a divisão {location}, Dudu."

    def luz_mais_quente(self, location=None):
        return self.ajustar_temperatura_luz(location=location, mode="warmer")

    def luz_mais_fria(self, location=None):
        return self.ajustar_temperatura_luz(location=location, mode="cooler")

    # ==================================================
    # CENAS
    # ==================================================

    def modo_cinema(self, location=None):
        location = self._normalizar_local(location) or "quarto"
        return self.definir_brilho(location=location, brightness=30)

    def modo_relax(self, location=None):
        location = self._normalizar_local(location) or "quarto"
        return self.definir_brilho(location=location, brightness=40)

    def modo_gaming(self, location=None):
        location = self._normalizar_local(location) or "quarto"
        return self.definir_brilho(location=location, brightness=70)

    # ==================================================
    # TOMADA
    # ==================================================

    def controlar_tomada(self, location=None, action="turn_on"):
        location = self._normalizar_local(location)

        if not location:
            return "Falta dizer-me a divisão."

        if location in self.tomadas:
            self.tomadas[location]["state"] = "on" if action == "turn_on" else "off"
            return f"Tomada {'ligada' if action == 'turn_on' else 'desligada'} em {location}."

        return f"Não conheço a divisão {location}, Dudu."

    # ==================================================
    # TIMER
    # ==================================================

    def agendar_luz_off(self, location=None, minutes=None):
        location = self._normalizar_local(location)

        if not location:
            return "Falta dizer-me a divisão."

        if minutes is None:
            return "Não percebi o número de minutos."

        try:
            minutes = int(minutes)
        except Exception:
            return "O número de minutos não é válido."

        if minutes <= 0:
            return "O número de minutos tem de ser maior que zero."

        return f"Vou desligar a luz em {location} daqui a {minutes} minutos."

    def agendar_desligar_luz(self, location=None, minutes=None):
        return self.agendar_luz_off(location=location, minutes=minutes)

    # ==================================================
    # ESTADO
    # ==================================================

    def obter_estado_luz(self, location=None):
        location = self._normalizar_local(location)

        if location in self.luzes:
            return {
                "location": location,
                "device": "light",
                "state": self.luzes[location]["state"],
                "brightness": self.luzes[location]["brightness"],
            }

        return {
            "location": location,
            "device": "light",
            "state": "unknown",
            "brightness": None,
        }

    def obter_estado_tomada(self, location=None):
        location = self._normalizar_local(location)

        if location in self.tomadas:
            return {
                "location": location,
                "device": "plug",
                "state": self.tomadas[location]["state"],
            }

        return {
            "location": location,
            "device": "plug",
            "state": "unknown",
        }

    def estado_total(self):
        return {
            "luzes": self.luzes,
            "tomadas": self.tomadas,
        }