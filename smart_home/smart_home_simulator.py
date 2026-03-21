# ==================================================
# 🏠 SMART HOME MANAGER - JARVIS MK5
# WC real + resto simulado
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
            "quarto": {"state": "off"},
            "wc": {"state": "off"},
            "sala": {"state": "off"},
            "cozinha": {"state": "off"},
            "escritório": {"state": "off"},
            "corredor": {"state": "off"},
        }

        self._timers = []

        if self.wc_controller:
            log("🏠 SmartHomeManager iniciado: WC real + resto simulado.")
        else:
            log("🏠 SmartHomeManager iniciado: tudo em modo simulado.")

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

    def _divisao_existe_luz(self, location):
        return location in self.luzes

    def _divisao_existe_tomada(self, location):
        return location in self.tomadas

    def _wc_real_disponivel(self):
        return self.wc_controller is not None

    def _simular_luz_on(self, location):
        self.luzes[location]["state"] = "on"
        if self.luzes[location]["brightness"] <= 0:
            self.luzes[location]["brightness"] = 100
        log(f"💡 [SIM] Luz ligada em {location}")
        return f"Luz ligada em {location}."

    def _simular_luz_off(self, location):
        self.luzes[location]["state"] = "off"
        log(f"💡 [SIM] Luz desligada em {location}")
        return f"Luz desligada em {location}."

    def controlar_luz(self, location=None, action="turn_on"):
        location = self._normalizar_local(location)

        if not location:
            return "Falta dizer-me em que divisão queres mexer na luz, Dudu."

        if not self._divisao_existe_luz(location):
            return f"Não conheço a divisão {location}, Dudu."

        if location == "wc" and self._wc_real_disponivel():
            try:
                if action == "turn_on":
                    self.wc_controller.turn_on()
                    self.luzes["wc"]["state"] = "on"
                    if self.luzes["wc"]["brightness"] <= 0:
                        self.luzes["wc"]["brightness"] = 100
                    log("💡 [REAL] Luz do WC ligada")
                    return "Luz ligada em wc."

                if action == "turn_off":
                    self.wc_controller.turn_off()
                    self.luzes["wc"]["state"] = "off"
                    log("💡 [REAL] Luz do WC desligada")
                    return "Luz desligada em wc."

                return "Não percebi o comando para a luz."
            except Exception as e:
                log(f"⚠️ Erro a controlar luz real do WC: {e}")
                return "Não consegui controlar a luz real do wc."

        if action == "turn_on":
            return self._simular_luz_on(location)

        if action == "turn_off":
            return self._simular_luz_off(location)

        return "Não percebi o comando para a luz."

    def definir_brilho(self, location=None, brightness=None):
        location = self._normalizar_local(location)

        if not location:
            return "Falta dizer-me em que divisão queres ajustar o brilho, Dudu."

        if not self._divisao_existe_luz(location):
            return f"Não conheço a divisão {location}, Dudu."

        if brightness is None:
            return "Não percebi o nível de brilho."

        try:
            brightness = int(brightness)
        except Exception:
            return "O valor do brilho não é válido."

        brightness = max(0, min(100, brightness))

        if location == "wc" and self._wc_real_disponivel():
            try:
                if hasattr(self.wc_controller, "set_brightness"):
                    self.wc_controller.set_brightness(brightness)
                    self.luzes["wc"]["brightness"] = brightness
                    self.luzes["wc"]["state"] = "on" if brightness > 0 else "off"
                    log(f"🔆 [REAL] Brilho do WC ajustado para {brightness}%")
                    return f"Luz em wc ajustada para {brightness}%."
            except Exception as e:
                log(f"⚠️ Erro a ajustar brilho real do WC: {e}")
                return "Não consegui ajustar o brilho real do wc."

        self.luzes[location]["brightness"] = brightness
        self.luzes[location]["state"] = "on" if brightness > 0 else "off"

        log(f"🔆 [SIM] Brilho da luz em {location} ajustado para {brightness}%")
        return f"Luz em {location} ajustada para {brightness}%."

    def controlar_brilho(self, location=None, brightness=None):
        return self.definir_brilho(location=location, brightness=brightness)

    def ajustar_brilho_relativo(self, location=None, direction="up"):
        location = self._normalizar_local(location)

        if not location:
            return "Falta dizer-me em que divisão queres mexer no brilho, Dudu."

        if not self._divisao_existe_luz(location):
            return f"Não conheço a divisão {location}, Dudu."

        if location == "wc" and self._wc_real_disponivel():
            try:
                if direction == "up" and hasattr(self.wc_controller, "brightness_up"):
                    self.wc_controller.brightness_up()
                    log("🔆 [REAL] Brilho do WC aumentado")
                    return "Brilho aumentado em wc."

                if direction == "down" and hasattr(self.wc_controller, "brightness_down"):
                    self.wc_controller.brightness_down()
                    log("🔆 [REAL] Brilho do WC reduzido")
                    return "Brilho reduzido em wc."
            except Exception as e:
                log(f"⚠️ Erro no brilho relativo real do WC: {e}")
                return "Não consegui ajustar o brilho real do wc."

        atual = self.luzes[location]["brightness"]
        passo = 20

        if direction == "up":
            novo = min(100, atual + passo)
            self.luzes[location]["brightness"] = novo
            self.luzes[location]["state"] = "on"
            log(f"🔆 [SIM] Brilho aumentado em {location} para {novo}%")
            return f"Brilho aumentado em {location}."

        novo = max(0, atual - passo)
        self.luzes[location]["brightness"] = novo
        self.luzes[location]["state"] = "on" if novo > 0 else "off"
        log(f"🔆 [SIM] Brilho reduzido em {location} para {novo}%")
        return f"Brilho reduzido em {location}."

    def aumentar_brilho(self, location=None):
        return self.ajustar_brilho_relativo(location=location, direction="up")

    def diminuir_brilho(self, location=None):
        return self.ajustar_brilho_relativo(location=location, direction="down")

    def ajustar_temperatura_luz(self, location=None, mode="warmer"):
        location = self._normalizar_local(location)

        if not location:
            return "Falta dizer-me em que divisão queres ajustar a luz, Dudu."

        if not self._divisao_existe_luz(location):
            return f"Não conheço a divisão {location}, Dudu."

        if location == "wc" and self._wc_real_disponivel():
            try:
                if mode == "warmer" and hasattr(self.wc_controller, "warmer"):
                    self.wc_controller.warmer()
                    log("🌡️ [REAL] Luz do WC mais quente")
                    return "Luz mais quente em wc."

                if mode == "cooler" and hasattr(self.wc_controller, "cooler"):
                    self.wc_controller.cooler()
                    log("🌡️ [REAL] Luz do WC mais fria")
                    return "Luz mais fria em wc."
            except Exception as e:
                log(f"⚠️ Erro a ajustar temperatura real do WC: {e}")
                return "Não consegui ajustar a temperatura da luz do wc."

        if mode == "warmer":
            log(f"🌡️ [SIM] Luz mais quente em {location}")
            return f"Luz mais quente em {location}."

        log(f"🌡️ [SIM] Luz mais fria em {location}")
        return f"Luz mais fria em {location}."

    def luz_mais_quente(self, location=None):
        return self.ajustar_temperatura_luz(location=location, mode="warmer")

    def luz_mais_fria(self, location=None):
        return self.ajustar_temperatura_luz(location=location, mode="cooler")

    def modo_cinema(self, location=None):
        location = self._normalizar_local(location) or "quarto"

        if not self._divisao_existe_luz(location):
            return f"Não conheço a divisão {location}, Dudu."

        if location == "wc" and self._wc_real_disponivel():
            try:
                self.wc_controller.turn_on()
                log("🎬 [REAL] Modo cinema no WC")
                return "Modo cinema ativado em wc."
            except Exception as e:
                log(f"⚠️ Erro no modo cinema real do WC: {e}")
                return "Não consegui ativar o modo cinema no wc."

        self.luzes[location]["state"] = "on"
        self.luzes[location]["brightness"] = 30
        log(f"🎬 [SIM] Modo cinema ativado em {location}")
        return f"Modo cinema ativado em {location}."

    def modo_relax(self, location=None):
        location = self._normalizar_local(location) or "quarto"

        if not self._divisao_existe_luz(location):
            return f"Não conheço a divisão {location}, Dudu."

        if location == "wc" and self._wc_real_disponivel():
            try:
                self.wc_controller.turn_on()
                log("😌 [REAL] Modo relax no WC")
                return "Modo relax ativado em wc."
            except Exception as e:
                log(f"⚠️ Erro no modo relax real do WC: {e}")
                return "Não consegui ativar o modo relax no wc."

        self.luzes[location]["state"] = "on"
        self.luzes[location]["brightness"] = 40
        log(f"😌 [SIM] Modo relax ativado em {location}")
        return f"Modo relax ativado em {location}."

    def modo_gaming(self, location=None):
        location = self._normalizar_local(location) or "quarto"

        if not self._divisao_existe_luz(location):
            return f"Não conheço a divisão {location}, Dudu."

        if location == "wc" and self._wc_real_disponivel():
            try:
                self.wc_controller.turn_on()
                log("🎮 [REAL] Modo gaming no WC")
                return "Modo gaming ativado em wc."
            except Exception as e:
                log(f"⚠️ Erro no modo gaming real do WC: {e}")
                return "Não consegui ativar o modo gaming no wc."

        self.luzes[location]["state"] = "on"
        self.luzes[location]["brightness"] = 70
        log(f"🎮 [SIM] Modo gaming ativado em {location}")
        return f"Modo gaming ativado em {location}."

    def agendar_luz_off(self, location=None, minutes=None):
        location = self._normalizar_local(location)

        if not location:
            return "Falta dizer-me em que divisão queres apagar a luz, Dudu."

        if not self._divisao_existe_luz(location):
            return f"Não conheço a divisão {location}, Dudu."

        if minutes is None:
            return "Não percebi ao fim de quantos minutos."

        try:
            minutes = int(minutes)
        except Exception:
            return "O temporizador não está num formato válido."

        if minutes <= 0:
            return "O temporizador tem de ser maior que zero."

        segundos = max(1, minutes * 60)

        def desligar():
            try:
                if location == "wc" and self._wc_real_disponivel():
                    self.wc_controller.turn_off()
                    self.luzes["wc"]["state"] = "off"
                    log("⏰ [REAL] Luz do WC desligada automaticamente.")
                else:
                    self.luzes[location]["state"] = "off"
                    log(f"⏰ [SIM] Luz desligada automaticamente em {location}.")
            except Exception as e:
                log(f"⚠️ Erro no temporizador da luz em {location}: {e}")

        timer = threading.Timer(segundos, desligar)
        timer.daemon = True
        timer.start()
        self._timers.append(timer)

        return f"Vou apagar a luz em {location} daqui a {minutes} minutos."

    def controlar_tomada(self, location=None, action="turn_on"):
        location = self._normalizar_local(location)

        if not location:
            return "Falta dizer-me em que divisão queres mexer na tomada, Dudu."

        if not self._divisao_existe_tomada(location):
            return f"Não conheço a divisão {location}, Dudu."

        if action == "turn_on":
            self.tomadas[location]["state"] = "on"
            log(f"🔌 Tomada ligada em {location}")
            return f"Tomada ligada em {location}."

        if action == "turn_off":
            self.tomadas[location]["state"] = "off"
            log(f"🔌 Tomada desligada em {location}")
            return f"Tomada desligada em {location}."

        return "Não percebi o comando para a tomada."

    def obter_estado_luz(self, location=None):
        location = self._normalizar_local(location)

        if not location:
            return "Falta dizer-me de que divisão queres o estado da luz, Dudu."

        if not self._divisao_existe_luz(location):
            return f"Não conheço a divisão {location}, Dudu."

        estado = self.luzes[location]["state"]
        brilho = self.luzes[location]["brightness"]

        return {
            "location": location,
            "device": "light",
            "state": estado,
            "brightness": brilho,
        }

    def obter_estado_tomada(self, location=None):
        location = self._normalizar_local(location)

        if not location:
            return "Falta dizer-me de que divisão queres o estado da tomada, Dudu."

        if not self._divisao_existe_tomada(location):
            return f"Não conheço a divisão {location}, Dudu."

        estado = self.tomadas[location]["state"]

        return {
            "location": location,
            "device": "plug",
            "state": estado,
        }

    def estado_total(self):
        return {
            "luzes": self.luzes,
            "tomadas": self.tomadas,
        } 