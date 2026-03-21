# ==================================================
# 💡 TUYA LIGHT - JARVIS MK5
# ==================================================

import tinytuya
from core.logger import log


class TuyaLight:
    def __init__(
        self,
        device_id: str,
        ip: str,
        local_key: str,
        version: float = 3.5
    ):
        self.device_id = device_id
        self.ip = ip
        self.local_key = local_key
        self.version = version

        # DPS conhecidos desta luz
        self.power_dps = 20
        self.brightness_dps = 22

        # ordem de fallback para evitar erro 914
        self.version_fallbacks = [self.version, 3.5, 3.4, 3.3]

        log(
            f"💡 TuyaLight criada | "
            f"id={self.device_id} | ip={self.ip} | version={self.version}"
        )

    # ------------------------------------------------
    # HELPERS
    # ------------------------------------------------

    def _criar_device(self, version: float | None = None):
        versao = version if version is not None else self.version

        device = tinytuya.Device(
            self.device_id,
            self.ip,
            self.local_key
        )
        device.set_version(versao)
        return device

    def _resposta_tem_erro(self, resposta) -> bool:
        if resposta is None:
            return True

        if isinstance(resposta, dict):
            if "Error" in resposta or "Err" in resposta:
                return True

        return False

    def _executar_com_retry(self, operacao_nome: str, callback):
        tentadas = []
        ultima_resposta = None

        for versao in self.version_fallbacks:
            if versao in tentadas:
                continue
            tentadas.append(versao)

            try:
                device = self._criar_device(versao)
                resposta = callback(device)

                if self._resposta_tem_erro(resposta):
                    log(
                        f"⚠️ TuyaLight {operacao_nome} falhou "
                        f"com version={versao} -> {resposta}"
                    )
                    ultima_resposta = resposta
                    continue

                self.version = versao

                log(
                    f"✅ TuyaLight {operacao_nome} OK "
                    f"com version={versao} -> {resposta}"
                )
                return True, resposta

            except Exception as e:
                log(
                    f"⚠️ TuyaLight {operacao_nome} exception "
                    f"com version={versao} -> {e}"
                )
                ultima_resposta = {"Error": str(e)}

        log(
            f"❌ TuyaLight {operacao_nome} falhou em todas as versões "
            f"{tentadas} | última resposta={ultima_resposta}"
        )
        return False, ultima_resposta

    # ------------------------------------------------
    # STATUS
    # ------------------------------------------------

    def status(self):
        ok, resposta = self._executar_com_retry(
            "status",
            lambda device: device.status()
        )

        if ok:
            return resposta
        return None

    # ------------------------------------------------
    # ENERGIA
    # ------------------------------------------------

    def ligar(self):
        ok, resposta = self._executar_com_retry(
            "ligar",
            lambda device: device.set_status(True, self.power_dps)
        )

        if ok:
            return True

        log(f"❌ Erro a ligar TuyaLight -> {resposta}")
        return False

    def desligar(self):
        ok, resposta = self._executar_com_retry(
            "desligar",
            lambda device: device.set_status(False, self.power_dps)
        )

        if ok:
            return True

        log(f"❌ Erro a desligar TuyaLight -> {resposta}")
        return False

    # ------------------------------------------------
    # BRILHO
    # ------------------------------------------------

    def definir_brilho(self, brightness_percent: int):
        try:
            brightness_percent = max(0, min(100, int(brightness_percent)))
        except Exception:
            log("❌ brilho inválido recebido em TuyaLight")
            return False

        if brightness_percent <= 0:
            return self.desligar()

        valor_tuya = int(10 + ((brightness_percent / 100) * (1000 - 10)))

        def _callback(device):
            resp_on = device.set_status(True, self.power_dps)
            if self._resposta_tem_erro(resp_on):
                return resp_on

            resp_brightness = device.set_value(self.brightness_dps, valor_tuya)
            return resp_brightness

        ok, resposta = self._executar_com_retry(
            f"definir_brilho_{brightness_percent}",
            _callback
        )

        if ok:
            log(
                f"🔆 TuyaLight brilho definido -> "
                f"{brightness_percent}% | raw={valor_tuya}"
            )
            return True

        log(f"❌ Erro a definir brilho TuyaLight -> {resposta}")
        return False