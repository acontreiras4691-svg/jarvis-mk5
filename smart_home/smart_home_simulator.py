# ==================================================
# 🏠 SMART HOME MANAGER - JARVIS MK5 (FIXED)
# ==================================================

import threading
from core.logger import log


class SmartHomeManager:
    def __init__(self, wc_controller=None):
        self.wc_controller = wc_controller

        self.luzes = {
            "quarto": {"state": "off", "brightness": 100},
            "wc": {"state": "off", "brightness": 100},
            "sala": {"state": "off", "brightness": 100},
            "cozinha": {"state": "off", "brightness": 100},
            "escritório": {"state": "off", "brightness": 100},
            "corredor": {"state": "off", "brightness": 100},
        }

        self.tomadas = {
            k: {"state": "off"} for k in self.luzes
        }

        self._timers = []

        if self.wc_controller:
            log("🏠 SmartHomeManager: WC real + resto simulado.")
        else:
            log("🏠 SmartHomeManager: modo simulado.")

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
            "escritorio": "escritório",
        }

        return mapa.get(location, location)

    def _luz_existe(self, location):
        return location in self.luzes

    def _tomada_existe(self, location):
        return location in self.tomadas

    def _wc_real(self):
        return self.wc_controller is not None

    # ==================================================
    # LUZ
    # ==================================================

    def controlar_luz(self, location=None, action="turn_on"):
        location = self._normalizar_local(location)

        if not location:
            return "Diz-me onde queres mexer na luz."

        if not self._luz_existe(location):
            return f"Não conheço {location}."

        # WC REAL
        if location == "wc" and self._wc_real():
            try:
                if action == "turn_on":
                    self.wc_controller.turn_on()
                    self.luzes["wc"]["state"] = "on"
                    return "Luz ligada em wc."

                if action == "turn_off":
                    self.wc_controller.turn_off()
                    self.luzes["wc"]["state"] = "off"
                    return "Luz desligada em wc."

            except Exception as e:
                log(f"❌ WC real erro: {e}")
                return "Erro na luz do wc."

        # SIMULADO
        self.luzes[location]["state"] = "on" if action == "turn_on" else "off"

        log(f"💡 {action} em {location}")
        return f"Luz {'ligada' if action=='turn_on' else 'desligada'} em {location}."

    # ==================================================
    # BRILHO
    # ==================================================

    def definir_brilho(self, location=None, brightness=None):
        location = self._normalizar_local(location)

        if not location or not self._luz_existe(location):
            return "Divisão inválida."

        try:
            brightness = int(brightness)
        except:
            return "Brilho inválido."

        brightness = max(0, min(100, brightness))

        self.luzes[location]["brightness"] = brightness
        self.luzes[location]["state"] = "on" if brightness > 0 else "off"

        log(f"🔆 {location} -> {brightness}%")
        return f"Luz em {location} a {brightness}%."

    def controlar_brilho(self, **kwargs):
        return self.definir_brilho(**kwargs)

    # ==================================================
    # MODOS
    # ==================================================

    def modo_cinema(self, location="quarto"):
        return self.definir_brilho(location, 30)

    def modo_relax(self, location="quarto"):
        return self.definir_brilho(location, 40)

    def modo_gaming(self, location="quarto"):
        return self.definir_brilho(location, 70)

    # ==================================================
    # TIMER
    # ==================================================

    def agendar_luz_off(self, location=None, minutes=None):
        location = self._normalizar_local(location)

        if not location or not self._luz_existe(location):
            return "Divisão inválida."

        try:
            minutes = int(minutes)
        except:
            return "Tempo inválido."

        def desligar():
            self.luzes[location]["state"] = "off"
            log(f"⏰ Luz desligada em {location}")

        t = threading.Timer(minutes * 60, desligar)
        t.daemon = True
        t.start()
        self._timers.append(t)

        return f"Vou desligar a luz em {location} em {minutes} minutos."

    # ==================================================
    # TOMADAS
    # ==================================================

    def controlar_tomada(self, location=None, action="turn_on"):
        location = self._normalizar_local(location)

        if not location or not self._tomada_existe(location):
            return "Divisão inválida."

        self.tomadas[location]["state"] = "on" if action == "turn_on" else "off"

        log(f"🔌 {action} em {location}")
        return f"Tomada {'ligada' if action=='turn_on' else 'desligada'} em {location}."

    # ==================================================
    # ESTADO
    # ==================================================

    def obter_estado_luz(self, location=None):
        location = self._normalizar_local(location)

        if not location or not self._luz_existe(location):
            return None

        return self.luzes[location]

    def obter_estado_tomada(self, location=None):
        location = self._normalizar_local(location)

        if not location or not self._tomada_existe(location):
            return None

        return self.tomadas[location]

    def estado_total(self):
        return {
            "luzes": self.luzes,
            "tomadas": self.tomadas,
        }