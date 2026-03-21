# ==================================================
# ☁️ TUYA CLOUD LIGHT - JARVIS MK5
# ==================================================

import tinytuya
from core.logger import log


class TuyaCloudLight:
    def __init__(
        self,
        api_region: str,
        api_key: str,
        api_secret: str,
        api_device_id: str,
        virtual_id: str,
    ):
        self.api_region = api_region
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_device_id = api_device_id
        self.virtual_id = virtual_id

        self.cloud = tinytuya.Cloud(
            apiRegion=self.api_region,
            apiKey=self.api_key,
            apiSecret=self.api_secret,
            apiDeviceID=self.api_device_id,
        )

        log(
            f"☁️ TuyaCloudLight criada | "
            f"region={self.api_region} | virtual_id={self.virtual_id}"
        )

    # ------------------------------------------------
    # HELPERS
    # ------------------------------------------------

    def _send(self, commands):
        try:
            resposta = self.cloud.sendcommand(self.virtual_id, commands)
            log(f"☁️ TuyaCloudLight resposta -> {resposta}")

            if not resposta:
                return False, None

            # Tuya costuma devolver success=True quando corre bem
            if isinstance(resposta, dict):
                if resposta.get("success") is True:
                    return True, resposta

                # alguns erros vêm aqui
                if resposta.get("success") is False:
                    return False, resposta

            return True, resposta

        except Exception as e:
            log(f"❌ Erro TuyaCloudLight _send: {e}")
            return False, {"error": str(e)}

    # ------------------------------------------------
    # POWER
    # ------------------------------------------------

    def ligar(self):
        commands = {
            "commands": [
                {"code": "switch_led", "value": True}
            ]
        }
        return self._send(commands)[0]

    def desligar(self):
        commands = {
            "commands": [
                {"code": "switch_led", "value": False}
            ]
        }
        return self._send(commands)[0]

    # ------------------------------------------------
    # BRILHO
    # ------------------------------------------------

    def definir_brilho(self, brightness_percent: int):
        try:
            brightness_percent = max(0, min(100, int(brightness_percent)))
        except Exception:
            return False

        valor = int(10 + ((brightness_percent / 100) * (1000 - 10)))

        commands = {
            "commands": [
                {"code": "switch_led", "value": True},
                {"code": "work_mode", "value": "white"},
                {"code": "bright_value", "value": valor},
            ]
        }
        return self._send(commands)[0]

    # ------------------------------------------------
    # TEMPERATURA
    # ------------------------------------------------

    def definir_temperatura(self, temp_percent: int):
        try:
            temp_percent = max(0, min(100, int(temp_percent)))
        except Exception:
            return False

        valor = int((temp_percent / 100) * 1000)

        commands = {
            "commands": [
                {"code": "switch_led", "value": True},
                {"code": "work_mode", "value": "white"},
                {"code": "temp_value", "value": valor},
            ]
        }
        return self._send(commands)[0]