# ==================================================
# 🚿 WC TUYA CONTROLLER - JARVIS MK5
# ==================================================

from core.logger import log
from smart_home.tuya_light import TuyaLight


class WcTuyaController:
    def __init__(
        self,
        device_id: str,
        ip: str,
        local_key: str,
        version: float = 3.5
    ):
        self.light = TuyaLight(
            device_id=device_id,
            ip=ip,
            local_key=local_key,
            version=version,
        )
        log("🚿 WcTuyaController iniciado.")

    def turn_on(self):
        ok = self.light.ligar()
        if not ok:
            raise RuntimeError("Falha ao ligar a luz Tuya do WC.")
        return True

    def turn_off(self):
        ok = self.light.desligar()
        if not ok:
            raise RuntimeError("Falha ao desligar a luz Tuya do WC.")
        return True

    def set_brightness(self, brightness: int):
        ok = self.light.definir_brilho(brightness)
        if not ok:
            raise RuntimeError("Falha ao definir brilho da luz Tuya do WC.")
        return True

    def brightness_up(self, step: int = 20):
        return self.set_brightness(80)

    def brightness_down(self, step: int = 20):
        return self.set_brightness(40)

    def warmer(self):
        log("ℹ️ A luz WC não tem temperatura implementada.")
        return True

    def cooler(self):
        log("ℹ️ A luz WC não tem temperatura implementada.")
        return True