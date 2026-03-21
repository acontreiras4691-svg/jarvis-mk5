# ==================================================
# 🏠 HYBRID SMART HOME - JARVIS MK5
# WC real local + quarto cloud + resto simulado
# ==================================================

from core.logger import log
from smart_home.smart_home_simulator import SmartHomeSimulator
from smart_home.tuya_light import TuyaLight
from smart_home.tuya_cloud_light import TuyaCloudLight


class HybridSmartHome:
    def __init__(self, wc_controller=None):
        """
        wc_controller:
            opcional. Se vier, usa esse controller para o WC.
            Se não vier, usa a configuração Tuya local definida abaixo.
        """
        self.simulator = SmartHomeSimulator()

        # ------------------------------------------------
        # LUZES LOCAIS
        # ------------------------------------------------
        self.real_lights = {}

        if wc_controller is not None:
            self.real_lights["wc"] = wc_controller
            log("💡 WC ligado por wc_controller externo.")
        else:
            # Mantém aqui os teus valores reais locais
            self.real_lights["wc"] = TuyaLight(
                device_id="bfcdaf6c99ef575ce9byxu",
                ip="192.168.1.70",
                local_key="v4TA0[}GqOwMdA;5",
                version=3.5,
            )

        # ------------------------------------------------
        # LUZES CLOUD
        # ------------------------------------------------
        self.cloud_lights = {
            "quarto": TuyaCloudLight(
                api_region="eu",
                api_key="t79faap584qqmpmju4mg",
                api_secret="6c502adadc2a441ebcd3da2a6cc04647",
                api_device_id="bfcdaf6c99ef575ce9byxu",
                virtual_id="2033655062663962625",
            )
        }

        log("🏠 HybridSmartHome iniciado.")
        log(f"🏠 Luzes locais: {list(self.real_lights.keys())}")
        log(f"☁️ Luzes cloud: {list(self.cloud_lights.keys())}")

    # ------------------------------------------------
    # HELPERS
    # ------------------------------------------------

    def _normalizar_local(self, location):
        if not location:
            return None

        original = str(location)
        location = original.lower().strip()

        mapa = {
            "casa de banho": "wc",
            "banho": "wc",
            "escritorio": "escritório",
            "escritório": "escritório",
            "quarto de dormir": "quarto",
        }

        normalizado = mapa.get(location, location)
        log(f"🏠 _normalizar_local -> original='{original}' | normalizado='{normalizado}'")
        return normalizado

    def _tem_luz_local(self, location):
        location = self._normalizar_local(location)
        return location in self.real_lights

    def _tem_luz_cloud(self, location):
        location = self._normalizar_local(location)
        return location in self.cloud_lights

    def _default_location(self, location):
        return self._normalizar_local(location) or "quarto"

    def _sim_set_brightness(self, location, brightness):
        return self.simulator.definir_brilho(location=location, brightness=brightness)

    # ------------------------------------------------
    # LUZ
    # ------------------------------------------------

    def controlar_luz(self, location=None, action="turn_on"):
        location = self._normalizar_local(location)
        log(f"🏠 controlar_luz -> location='{location}' | action='{action}'")

        if self._tem_luz_local(location):
            light = self.real_lights[location]
            log(f"💡 usar LUZ LOCAL em '{location}'")

            try:
                if hasattr(light, "turn_on") and hasattr(light, "turn_off"):
                    if action == "turn_on":
                        ok = light.turn_on()
                        return f"Luz ligada em {location}." if ok else f"Não consegui ligar a luz em {location}."

                    if action == "turn_off":
                        ok = light.turn_off()
                        return f"Luz desligada em {location}." if ok else f"Não consegui desligar a luz em {location}."
                else:
                    if action == "turn_on":
                        ok = light.ligar()
                        return f"Luz ligada em {location}." if ok else f"Não consegui ligar a luz em {location}."

                    if action == "turn_off":
                        ok = light.desligar()
                        return f"Luz desligada em {location}." if ok else f"Não consegui desligar a luz em {location}."
            except Exception as e:
                log(f"⚠️ Erro na luz local '{location}': {e}")
                return f"Não consegui controlar a luz em {location}."

            return "Não percebi o comando para a luz."

        if self._tem_luz_cloud(location):
            light = self.cloud_lights[location]
            log(f"☁️ usar LUZ CLOUD em '{location}'")

            try:
                if action == "turn_on":
                    ok = light.ligar()
                    return f"Luz ligada em {location}." if ok else f"Não consegui ligar a luz em {location}."

                if action == "turn_off":
                    ok = light.desligar()
                    return f"Luz desligada em {location}." if ok else f"Não consegui desligar a luz em {location}."
            except Exception as e:
                log(f"⚠️ Erro na luz cloud '{location}': {e}")
                return f"Não consegui controlar a luz em {location}."

            return "Não percebi o comando para a luz."

        log(f"🧪 fallback simulador para '{location}'")
        return self.simulator.controlar_luz(location=location, action=action)

    # ------------------------------------------------
    # BRILHO
    # ------------------------------------------------

    def definir_brilho(self, location=None, brightness=None):
        location = self._normalizar_local(location)
        log(f"🔆 definir_brilho -> location='{location}' | brightness='{brightness}'")

        if brightness is None:
            return "Não percebi o nível de brilho."

        try:
            brightness = int(brightness)
        except Exception:
            return "O valor do brilho não é válido."

        brightness = max(0, min(100, brightness))

        if self._tem_luz_local(location):
            light = self.real_lights[location]

            try:
                if hasattr(light, "set_brightness"):
                    ok = light.set_brightness(brightness)
                else:
                    ok = light.definir_brilho(brightness)

                return (
                    f"Luz em {location} ajustada para {brightness}%."
                    if ok else
                    f"Não consegui ajustar o brilho da luz em {location}."
                )
            except Exception as e:
                log(f"⚠️ Erro no brilho local '{location}': {e}")
                return f"Não consegui ajustar o brilho da luz em {location}."

        if self._tem_luz_cloud(location):
            light = self.cloud_lights[location]

            try:
                ok = light.definir_brilho(brightness)
                return (
                    f"Luz em {location} ajustada para {brightness}%."
                    if ok else
                    f"Não consegui ajustar o brilho da luz em {location}."
                )
            except Exception as e:
                log(f"⚠️ Erro no brilho cloud '{location}': {e}")
                return f"Não consegui ajustar o brilho da luz em {location}."

        return self.simulator.definir_brilho(location=location, brightness=brightness)

    def controlar_brilho(self, location=None, brightness=None):
        return self.definir_brilho(location=location, brightness=brightness)

    def ajustar_brilho_relativo(self, location=None, direction="up"):
        location = self._normalizar_local(location)
        log(f"🔆 ajustar_brilho_relativo -> location='{location}' | direction='{direction}'")

        if self._tem_luz_local(location):
            light = self.real_lights[location]

            try:
                if direction == "up":
                    if hasattr(light, "brightness_up"):
                        ok = light.brightness_up()
                        return "Brilho aumentado em wc." if ok else "Não consegui aumentar o brilho em wc."
                    # fallback simples
                    return self.definir_brilho(location=location, brightness=80)

                if hasattr(light, "brightness_down"):
                    ok = light.brightness_down()
                    return "Brilho reduzido em wc." if ok else "Não consegui reduzir o brilho em wc."
                return self.definir_brilho(location=location, brightness=40)

            except Exception as e:
                log(f"⚠️ Erro no brilho relativo local '{location}': {e}")
                return f"Não consegui ajustar o brilho em {location}."

        if self._tem_luz_cloud(location):
            # fallback simples por percentagens
            if direction == "up":
                return self.definir_brilho(location=location, brightness=80)
            return self.definir_brilho(location=location, brightness=40)

        return self.simulator.ajustar_brilho_relativo(location=location, direction=direction)

    def aumentar_brilho(self, location=None):
        return self.ajustar_brilho_relativo(location=location, direction="up")

    def diminuir_brilho(self, location=None):
        return self.ajustar_brilho_relativo(location=location, direction="down")

    # ------------------------------------------------
    # TEMPERATURA / COR
    # ------------------------------------------------

    def ajustar_temperatura_luz(self, location=None, mode="warmer"):
        location = self._normalizar_local(location)
        log(f"🌡️ ajustar_temperatura_luz -> location='{location}' | mode='{mode}'")

        if self._tem_luz_local(location):
            light = self.real_lights[location]

            try:
                if mode == "warmer":
                    if hasattr(light, "warmer"):
                        ok = light.warmer()
                        return "Luz mais quente em wc." if ok is not False else "Não consegui aquecer a luz em wc."
                    return "A luz do wc não suporta temperatura de cor."

                if hasattr(light, "cooler"):
                    ok = light.cooler()
                    return "Luz mais fria em wc." if ok is not False else "Não consegui arrefecer a luz em wc."
                return "A luz do wc não suporta temperatura de cor."

            except Exception as e:
                log(f"⚠️ Erro na temperatura local '{location}': {e}")
                return f"Não consegui ajustar a temperatura da luz em {location}."

        if self._tem_luz_cloud(location):
            # se a cloud light ainda não tiver suporte, devolve algo limpo
            return f"A luz em {location} ainda não tem controlo de temperatura implementado."

        return self.simulator.ajustar_temperatura_luz(location=location, mode=mode)

    def luz_mais_quente(self, location=None):
        return self.ajustar_temperatura_luz(location=location, mode="warmer")

    def luz_mais_fria(self, location=None):
        return self.ajustar_temperatura_luz(location=location, mode="cooler")

    # ------------------------------------------------
    # TOMADA
    # ------------------------------------------------

    def controlar_tomada(self, location=None, action="turn_on"):
        return self.simulator.controlar_tomada(location=location, action=action)

    # ------------------------------------------------
    # TIMER
    # ------------------------------------------------

    def agendar_luz_off(self, location=None, minutes=None):
        return self.simulator.agendar_luz_off(location=location, minutes=minutes)

    # ------------------------------------------------
    # CENAS
    # ------------------------------------------------

    def modo_cinema(self, location=None):
        location = self._default_location(location)
        log(f"🎬 modo_cinema -> location='{location}'")

        # comportamento especial do teu setup
        if location == "quarto":
            ok_wc = True
            ok_quarto_on = True
            ok_quarto_brilho = True

            if self._tem_luz_local("wc"):
                wc = self.real_lights["wc"]
                try:
                    if hasattr(wc, "turn_off"):
                        ok_wc = wc.turn_off()
                    else:
                        ok_wc = wc.desligar()
                except Exception:
                    ok_wc = False
                log(f"🎬 modo_cinema -> wc desligar = {ok_wc}")

            if self._tem_luz_cloud("quarto"):
                quarto = self.cloud_lights["quarto"]
                try:
                    ok_quarto_on = quarto.ligar()
                    ok_quarto_brilho = quarto.definir_brilho(20)
                except Exception:
                    ok_quarto_on = False
                    ok_quarto_brilho = False
                log(f"🎬 modo_cinema -> quarto ligar = {ok_quarto_on}")
                log(f"🎬 modo_cinema -> quarto brilho = {ok_quarto_brilho}")

            if ok_wc and ok_quarto_on and ok_quarto_brilho:
                return "Modo cinema ativado em quarto."

            return "Ativei parcialmente o modo cinema."

        # fallback genérico
        self.controlar_luz(location=location, action="turn_on")
        return self.definir_brilho(location=location, brightness=30)

    def modo_relax(self, location=None):
        location = self._default_location(location)
        log(f"😌 modo_relax -> location='{location}'")

        self.controlar_luz(location=location, action="turn_on")
        return self.definir_brilho(location=location, brightness=40)

    def modo_gaming(self, location=None):
        location = self._default_location(location)
        log(f"🎮 modo_gaming -> location='{location}'")

        self.controlar_luz(location=location, action="turn_on")
        return self.definir_brilho(location=location, brightness=70)

    # ------------------------------------------------
    # ESTADO
    # ------------------------------------------------

    def estado_total(self):
        data = self.simulator.estado_total()

        for location in self.real_lights:
            data["luzes"][location] = {
                "backend": "tuya_local"
            }

        for location in self.cloud_lights:
            data["luzes"][location] = {
                "backend": "tuya_cloud"
            }

        return data