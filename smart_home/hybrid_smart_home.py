# ==================================================
# 🏠 HYBRID SMART HOME - JARVIS MK5
# WC real local + quarto cloud + resto simulado
# + Apple TV
# ==================================================

import threading

from core.logger import log
from smart_home.tuya_light import TuyaLight
from smart_home.tuya_cloud_light import TuyaCloudLight
from smart_home.smart_home_manager import SmartHomeManager
from smart_home.apple_tv_controller import AppleTVController


class HybridSmartHome:
    def __init__(self, wc_controller=None, apple_tv_controller=None):
        self.simulator = SmartHomeManager()

        # -------------------------
        # LOCAL (WC)
        # -------------------------
        self.real_lights = {}

        if wc_controller:
            self.real_lights["wc"] = wc_controller
            log("💡 WC ligado por wc_controller externo.")
        else:
            self.real_lights["wc"] = TuyaLight(
                device_id="bfcdaf6c99ef575ce9byxu",
                ip="192.168.1.70",
                local_key="v4TA0[}GqOwMdA;5",
                version=3.5,
            )

        # -------------------------
        # CLOUD (QUARTO)
        # -------------------------
        self.cloud_lights = {
            "quarto": TuyaCloudLight(
                api_region="eu",
                api_key="t79faap584qqmpmju4mg",
                api_secret="6c502adadc2a441ebcd3da2a6cc04647",
                api_device_id="bfcdaf6c99ef575ce9byxu",
                virtual_id="2033655062663962625",
            )
        }

        # -------------------------
        # APPLE TV
        # -------------------------
        self.apple_tv = apple_tv_controller or AppleTVController()

        log("🏠 HybridSmartHome pronto.")
        log(f"🏠 Luzes locais: {list(self.real_lights.keys())}")
        log(f"☁️ Luzes cloud: {list(self.cloud_lights.keys())}")
        log("📺 Apple TV integrada.")

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
            "quarto de dormir": "quarto",
            "escritorio": "escritório",
        }

        return mapa.get(location, location)

    def _run_async(self, fn, descricao="ação"):
        def runner():
            try:
                log(f"⚡ Async start -> {descricao}")
                fn()
                log(f"✅ Async done -> {descricao}")
            except Exception as e:
                log(f"❌ Async erro ({descricao}): {e}")

        t = threading.Thread(target=runner, daemon=True)
        t.start()

    def _ligar_local(self, light):
        if hasattr(light, "turn_on"):
            return light.turn_on()
        if hasattr(light, "ligar"):
            return light.ligar()
        raise AttributeError("Luz local sem método para ligar")

    def _desligar_local(self, light):
        if hasattr(light, "turn_off"):
            return light.turn_off()
        if hasattr(light, "desligar"):
            return light.desligar()
        raise AttributeError("Luz local sem método para desligar")

    def _set_brilho_local(self, light, brightness):
        if hasattr(light, "set_brightness"):
            return light.set_brightness(brightness)
        if hasattr(light, "definir_brilho"):
            return light.definir_brilho(brightness)
        raise AttributeError("Luz local sem método de brilho")

    # ==================================================
    # LUZ
    # ==================================================

    def controlar_luz(self, location=None, action=None, brightness=None):
        location = self._normalizar_local(location)

        if not location:
            return "Não disseste a divisão."

        # Se vier brightness, redireciona para brilho
        if brightness is not None:
            return self.definir_brilho(location=location, brightness=brightness)

        if not action:
            return "Não percebi o comando para a luz."

        # -------------------------
        # LOCAL (WC)
        # -------------------------
        if location in self.real_lights:
            light = self.real_lights[location]

            try:
                if action == "turn_on":
                    self._run_async(
                        lambda: self._ligar_local(light),
                        f"ligar luz local {location}",
                    )
                    return f"A ligar a luz em {location}."

                if action == "turn_off":
                    self._run_async(
                        lambda: self._desligar_local(light),
                        f"desligar luz local {location}",
                    )
                    return f"A desligar a luz em {location}."

            except Exception as e:
                log(f"❌ Erro luz local: {e}")
                return "Erro a controlar luz."

            return "Não percebi o comando para a luz."

        # -------------------------
        # CLOUD (QUARTO)
        # -------------------------
        if location in self.cloud_lights:
            light = self.cloud_lights[location]

            try:
                if action == "turn_on":
                    self._run_async(
                        lambda: light.ligar(),
                        f"ligar luz cloud {location}",
                    )
                    return f"A ligar a luz em {location}."

                if action == "turn_off":
                    self._run_async(
                        lambda: light.desligar(),
                        f"desligar luz cloud {location}",
                    )
                    return f"A desligar a luz em {location}."

            except Exception as e:
                log(f"❌ Erro luz cloud: {e}")
                return "Erro a controlar luz."

            return "Não percebi o comando para a luz."

        # -------------------------
        # SIMULADOR
        # -------------------------
        if hasattr(self.simulator, "controlar_luz"):
            return self.simulator.controlar_luz(location=location, action=action)

        return f"A luz em {location} ainda não está configurada."

    # ==================================================
    # BRILHO
    # ==================================================

    def definir_brilho(self, location=None, brightness=None):
        location = self._normalizar_local(location)

        if not location:
            return "Não disseste a divisão."

        if brightness is None:
            return "Não percebi o brilho."

        try:
            brightness = int(brightness)
        except Exception:
            return "O valor do brilho não é válido."

        brightness = max(0, min(100, brightness))

        if location in self.real_lights:
            light = self.real_lights[location]

            try:
                self._run_async(
                    lambda: self._set_brilho_local(light, brightness),
                    f"brilho local {location} -> {brightness}%",
                )
                return f"A ajustar o brilho para {brightness}% em {location}."
            except Exception as e:
                log(f"❌ Erro brilho local: {e}")
                return "Erro a ajustar brilho."

        if location in self.cloud_lights:
            light = self.cloud_lights[location]

            try:
                self._run_async(
                    lambda: light.definir_brilho(brightness),
                    f"brilho cloud {location} -> {brightness}%",
                )
                return f"A ajustar o brilho para {brightness}% em {location}."
            except Exception as e:
                log(f"❌ Erro brilho cloud: {e}")
                return "Erro a ajustar brilho."

        if hasattr(self.simulator, "definir_brilho"):
            return self.simulator.definir_brilho(location=location, brightness=brightness)

        return f"O brilho da luz em {location} ainda não está configurado."

    def controlar_brilho(self, location=None, brightness=None):
        return self.definir_brilho(location=location, brightness=brightness)

    def ajustar_brilho_relativo(self, location=None, direction="up"):
        location = self._normalizar_local(location)

        if not location:
            return "Não disseste a divisão."

        if location in self.real_lights:
            light = self.real_lights[location]

            try:
                if direction == "up":
                    if hasattr(light, "brightness_up"):
                        self._run_async(
                            lambda: light.brightness_up(),
                            f"brightness_up local {location}",
                        )
                        return f"A aumentar o brilho em {location}."
                    return self.definir_brilho(location=location, brightness=80)

                if hasattr(light, "brightness_down"):
                    self._run_async(
                        lambda: light.brightness_down(),
                        f"brightness_down local {location}",
                    )
                    return f"A reduzir o brilho em {location}."

                return self.definir_brilho(location=location, brightness=40)

            except Exception as e:
                log(f"❌ Erro brilho relativo local: {e}")
                return "Erro a ajustar brilho."

        if location in self.cloud_lights:
            if direction == "up":
                return self.definir_brilho(location=location, brightness=80)
            return self.definir_brilho(location=location, brightness=40)

        if hasattr(self.simulator, "ajustar_brilho_relativo"):
            return self.simulator.ajustar_brilho_relativo(location=location, direction=direction)

        return f"O brilho da luz em {location} ainda não está configurado."

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
            return "Não disseste a divisão."

        if location in self.real_lights:
            light = self.real_lights[location]

            try:
                if mode == "warmer":
                    if hasattr(light, "warmer"):
                        self._run_async(
                            lambda: light.warmer(),
                            f"warmer local {location}",
                        )
                        return f"A aquecer a luz em {location}."
                    return f"A luz em {location} não suporta temperatura de cor."

                if hasattr(light, "cooler"):
                    self._run_async(
                        lambda: light.cooler(),
                        f"cooler local {location}",
                    )
                    return f"A arrefecer a luz em {location}."

                return f"A luz em {location} não suporta temperatura de cor."

            except Exception as e:
                log(f"❌ Erro temperatura local: {e}")
                return "Erro a ajustar temperatura."

        if location in self.cloud_lights:
            return f"A luz em {location} ainda não tem controlo de temperatura implementado."

        if hasattr(self.simulator, "ajustar_temperatura_luz"):
            return self.simulator.ajustar_temperatura_luz(location=location, mode=mode)

        return f"A temperatura da luz em {location} ainda não está configurada."

    def luz_mais_quente(self, location=None):
        return self.ajustar_temperatura_luz(location=location, mode="warmer")

    def luz_mais_fria(self, location=None):
        return self.ajustar_temperatura_luz(location=location, mode="cooler")

    # ==================================================
    # TOMADA
    # ==================================================

    def controlar_tomada(self, location=None, action="turn_on"):
        location = self._normalizar_local(location)

        if hasattr(self.simulator, "controlar_tomada"):
            return self.simulator.controlar_tomada(location=location, action=action)

        if location:
            return f"A tomada em {location} ainda não está configurada."
        return "Essa tomada ainda não está configurada."

    # ==================================================
    # TIMER
    # ==================================================

    def agendar_luz_off(self, location=None, minutes=None):
        location = self._normalizar_local(location)

        if not location:
            return "Não disseste a divisão."

        if not minutes:
            return "Não percebi o número de minutos."

        try:
            minutes = int(minutes)
        except Exception:
            return "O número de minutos não é válido."

        if minutes <= 0:
            return "O número de minutos tem de ser maior que zero."

        if hasattr(self.simulator, "agendar_luz_off"):
            return self.simulator.agendar_luz_off(location=location, minutes=minutes)

        return f"O temporizador da luz em {location} ainda não está configurado."

    def agendar_desligar_luz(self, location=None, minutes=None):
        return self.agendar_luz_off(location=location, minutes=minutes)

    # ==================================================
    # APPLE TV
    # ==================================================

    def controlar_apple_tv(self, action=None, app_name=None):
        if not action:
            return "Não percebi a ação da Apple TV."

        try:
            return self.apple_tv.executar(action=action, app_name=app_name)
        except Exception as e:
            log(f"❌ Erro Apple TV: {e}")
            return "Erro a controlar a Apple TV."

    # ==================================================
    # CENAS
    # ==================================================

    def modo_cinema(self, location=None):
        location = self._normalizar_local(location) or "quarto"

        if location == "quarto":
            if "wc" in self.real_lights:
                self._run_async(
                    lambda: self._desligar_local(self.real_lights["wc"]),
                    "modo cinema -> desligar wc",
                )

            if "quarto" in self.cloud_lights:
                self._run_async(
                    lambda: self.cloud_lights["quarto"].ligar(),
                    "modo cinema -> ligar quarto",
                )
                self._run_async(
                    lambda: self.cloud_lights["quarto"].definir_brilho(20),
                    "modo cinema -> brilho quarto 20%",
                )

            return "Modo cinema ativado."

        if hasattr(self.simulator, "modo_cinema"):
            return self.simulator.modo_cinema(location)

        return "Modo cinema não configurado."

    def modo_relax(self, location=None):
        location = self._normalizar_local(location) or "quarto"
        return self.definir_brilho(location=location, brightness=40)

    def modo_gaming(self, location=None):
        location = self._normalizar_local(location) or "quarto"
        return self.definir_brilho(location=location, brightness=70)

    # ==================================================
    # ESTADO
    # ==================================================

    def obter_estado_luz(self, location=None):
        location = self._normalizar_local(location)

        if location in self.real_lights:
            return {
                "location": location,
                "device": "light",
                "backend": "tuya_local",
                "state": "unknown",
            }

        if location in self.cloud_lights:
            return {
                "location": location,
                "device": "light",
                "backend": "tuya_cloud",
                "state": "unknown",
            }

        if hasattr(self.simulator, "obter_estado_luz"):
            return self.simulator.obter_estado_luz(location=location)

        return {
            "location": location,
            "device": "light",
            "backend": "unknown",
            "state": "unknown",
        }

    def obter_estado_tomada(self, location=None):
        if hasattr(self.simulator, "obter_estado_tomada"):
            return self.simulator.obter_estado_tomada(location=location)

        return {
            "location": location,
            "device": "plug",
            "backend": "unknown",
            "state": "unknown",
        }

    def estado_total(self):
        if hasattr(self.simulator, "estado_total"):
            data = self.simulator.estado_total()
        else:
            data = {"luzes": {}, "tomadas": {}}

        if "luzes" not in data:
            data["luzes"] = {}
        if "tomadas" not in data:
            data["tomadas"] = {}

        for location in self.real_lights:
            base = data["luzes"].get(location, {})
            base["backend"] = "tuya_local"
            data["luzes"][location] = base

        for location in self.cloud_lights:
            base = data["luzes"].get(location, {})
            base["backend"] = "tuya_cloud"
            data["luzes"][location] = base

        return data