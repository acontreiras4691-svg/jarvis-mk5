# ==================================================
# 🏠 SMART HOME MANAGER - JARVIS MK5
# WC real + resto simulado
# ==================================================

from core.logger import log
from smart_home.wc_tuya_controller import WcTuyaController


class SmartHomeManager:
    def __init__(self):
        # mete aqui os teus dados reais da luz WC
        self.wc_controller = WcTuyaController(
            device_id="bfcdaf6c99ef575ce9byxu",
            ip="192.168.1.70",
            local_key="v4TA0[}GqOwMdA;5",
            version=3.5,
        )

        self.luzes = {
            "quarto": {"state": "off", "brightness": 100},
            "wc": {"state": "off", "brightness": 100},
            "sala": {"state": "off", "brightness": 100},
            "cozinha": {"state": "off", "brightness": 100},
            "escritorio": {"state": "off", "brightness": 100},
            "corredor": {"state": "off", "brightness": 100},
        }

        self.tomadas = {
            "quarto": {"state": "off"},
            "wc": {"state": "off"},
            "sala": {"state": "off"},
            "cozinha": {"state": "off"},
            "escritorio": {"state": "off"},
            "corredor": {"state": "off"},
        }

        log("🏠 SmartHomeManager iniciado.")

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

    def controlar_luz(self, location=None, action="turn_on"):
        location = self._normalizar_local(location)

        if not location:
            return "Falta dizer-me em que divisão queres mexer na luz, Dudu."

        if location == "wc":
            try:
                if action == "turn_on":
                    self.wc_controller.turn_on()
                    self.luzes["wc"]["state"] = "on"
                    return "Luz ligada em wc."

                if action == "turn_off":
                    self.wc_controller.turn_off()
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

        return f"Não conheço a divisão {location}, Dudu."

    def definir_brilho(self, location=None, brightness=None):
        location = self._normalizar_local(location)

        if brightness is None:
            return "Não percebi o nível de brilho."

        try:
            brightness = int(brightness)
        except Exception:
            return "O valor do brilho não é válido."

        brightness = max(0, min(100, brightness))

        if location == "wc":
            try:
                self.wc_controller.set_brightness(brightness)
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

        if location == "wc":
            try:
                if direction == "up":
                    self.wc_controller.brightness_up()
                    return "Brilho aumentado em wc."
                self.wc_controller.brightness_down()
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

    def ajustar_temperatura_luz(self, location=None, mode="warmer"):
        location = self._normalizar_local(location)

        if location == "wc":
            return "A luz do wc não tem temperatura implementada."

        if location in self.luzes:
            return f"Luz {'mais quente' if mode == 'warmer' else 'mais fria'} em {location}."

        return f"Não conheço a divisão {location}, Dudu."

    def luz_mais_quente(self, location=None):
        return self.ajustar_temperatura_luz(location=location, mode="warmer")

    def luz_mais_fria(self, location=None):
        return self.ajustar_temperatura_luz(location=location, mode="cooler")

    def modo_cinema(self, location=None):
        location = self._normalizar_local(location) or "quarto"
        return self.definir_brilho(location=location, brightness=30)

    def modo_relax(self, location=None):
        location = self._normalizar_local(location) or "quarto"
        return self.definir_brilho(location=location, brightness=40)

    def modo_gaming(self, location=None):
        location = self._normalizar_local(location) or "quarto"
        return self.definir_brilho(location=location, brightness=70)

    def controlar_tomada(self, location=None, action="turn_on"):
        location = self._normalizar_local(location)

        if location in self.tomadas:
            self.tomadas[location]["state"] = "on" if action == "turn_on" else "off"
            return f"Tomada {'ligada' if action == 'turn_on' else 'desligada'} em {location}."

        return f"Não conheço a divisão {location}, Dudu."

    def estado_total(self):
        return {
            "luzes": self.luzes,
            "tomadas": self.tomadas,
        }