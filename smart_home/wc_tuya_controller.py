# ==================================================
# WC CONTROLLER - JARVIS MK5
# ==================================================
# Controla a luz do WC via servidor Linux.
#
# IMPORTANTE:
# Este ficheiro tenta vários endpoints por ordem.
# Se os teus endpoints reais forem diferentes, muda só a lista
# em ENDPOINTS_ON / ENDPOINTS_OFF / ENDPOINTS_BRIGHTNESS / ENDPOINTS_TIMER
# ==================================================

import os
import requests


class WCController:
    def __init__(self, base_url=None, timeout=6):
        self.base_url = (base_url or os.getenv("JARVIS_SMARTHOME_URL", "http://192.168.1.108:5050")).rstrip("/")
        self.timeout = timeout

        self.ENDPOINTS_ON = [
            ("POST", "/smart/wc/light/on", None),
            ("POST", "/smart_home/wc/light/on", None),
            ("POST", "/wc/light/on", None),
            ("POST", "/wc/on", None),
            ("POST", "/comando", {"texto": "acende a luz do wc", "client_id": "jarvis-mk5"}),
        ]

        self.ENDPOINTS_OFF = [
            ("POST", "/smart/wc/light/off", None),
            ("POST", "/smart_home/wc/light/off", None),
            ("POST", "/wc/light/off", None),
            ("POST", "/wc/off", None),
            ("POST", "/comando", {"texto": "apaga a luz do wc", "client_id": "jarvis-mk5"}),
        ]

        self.ENDPOINTS_BRIGHTNESS = [
            ("POST", "/smart/wc/light/brightness", "json_brightness"),
            ("POST", "/smart_home/wc/light/brightness", "json_brightness"),
            ("POST", "/wc/light/brightness", "json_brightness"),
            ("POST", "/comando", "command_brightness"),
        ]

        self.ENDPOINTS_TIMER = [
            ("POST", "/smart/wc/light/timer_off", "json_minutes"),
            ("POST", "/smart_home/wc/light/timer_off", "json_minutes"),
            ("POST", "/wc/light/timer_off", "json_minutes"),
            ("POST", "/comando", "command_timer"),
        ]

    # ------------------------------------------------
    # API PÚBLICA
    # ------------------------------------------------

    def controlar_luz(self, action=None, brightness=None):
        if brightness is not None:
            return self._set_brightness(brightness)

        if action == "turn_on":
            ok, msg = self._try_endpoints(self.ENDPOINTS_ON)
            return msg if ok else f"Falhei ao ligar a luz do WC. {msg}"

        if action == "turn_off":
            ok, msg = self._try_endpoints(self.ENDPOINTS_OFF)
            return msg if ok else f"Falhei ao desligar a luz do WC. {msg}"

        return "Ação da luz do WC inválida."

    def agendar_desligar(self, minutes=None):
        if not minutes:
            return "Não percebi o número de minutos."

        ok, msg = self._try_endpoints(self.ENDPOINTS_TIMER, value=minutes)
        if ok:
            return msg

        return f"Falhei ao agendar o desligar da luz do WC. {msg}"

    # ------------------------------------------------
    # BRILHO
    # ------------------------------------------------

    def _set_brightness(self, brightness):
        try:
            brightness = int(brightness)
        except Exception:
            return "Valor de brilho inválido."

        brightness = max(0, min(100, brightness))

        ok, msg = self._try_endpoints(self.ENDPOINTS_BRIGHTNESS, value=brightness)
        if ok:
            return msg

        return f"Falhei ao ajustar o brilho da luz do WC. {msg}"

    # ------------------------------------------------
    # REQUESTS
    # ------------------------------------------------

    def _try_endpoints(self, endpoints, value=None):
        last_error = "Nenhum endpoint respondeu."

        for method, path, payload_mode in endpoints:
            url = f"{self.base_url}{path}"

            try:
                if payload_mode is None:
                    resp = requests.request(
                        method,
                        url,
                        timeout=self.timeout,
                    )

                elif payload_mode == "json_brightness":
                    resp = requests.request(
                        method,
                        url,
                        json={"brightness": value},
                        timeout=self.timeout,
                    )

                elif payload_mode == "json_minutes":
                    resp = requests.request(
                        method,
                        url,
                        json={"minutes": value},
                        timeout=self.timeout,
                    )

                elif payload_mode == "command_brightness":
                    resp = requests.request(
                        method,
                        url,
                        json={
                            "texto": f"mete a luz do wc a {value} por cento",
                            "client_id": "jarvis-mk5",
                        },
                        timeout=self.timeout,
                    )

                elif payload_mode == "command_timer":
                    resp = requests.request(
                        method,
                        url,
                        json={
                            "texto": f"apaga a luz do wc daqui a {value} minutos",
                            "client_id": "jarvis-mk5",
                        },
                        timeout=self.timeout,
                    )

                else:
                    resp = requests.request(
                        method,
                        url,
                        json=payload_mode,
                        timeout=self.timeout,
                    )

                if 200 <= resp.status_code < 300:
                    texto = self._extrair_mensagem(resp)

                    if "/off" in path and "timer" not in path:
                        return True, texto or "Luz do WC desligada."

                    if "/on" in path:
                        return True, texto or "Luz do WC ligada."

                    if "brightness" in path:
                        return True, texto or "Brilho da luz do WC ajustado."

                    if "timer" in path or "daqui a" in str(payload_mode):
                        return True, texto or "Temporizador da luz do WC definido."

                    return True, texto or "Comando do WC executado."

                last_error = f"{url} respondeu {resp.status_code}"

            except Exception as e:
                last_error = f"{url}: {e}"

        return False, last_error

    def _extrair_mensagem(self, resp):
        try:
            data = resp.json()

            if isinstance(data, dict):
                for chave in ["message", "mensagem", "resposta", "status"]:
                    if chave in data and data[chave]:
                        return str(data[chave]).strip()
        except Exception:
            pass

        try:
            txt = resp.text.strip()
            if txt:
                return txt
        except Exception:
            pass

        return None