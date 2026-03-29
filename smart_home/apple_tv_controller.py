# ==================================================
# APPLE TV CONTROLLER - JARVIS MK5
# VERSÃO ESTÁVEL VIA ATVREMOTE
# MACROS CALIBRADAS AO TEU LAYOUT REAL
# ==================================================

import os
import shutil
import subprocess
import time

from core.logger import log


class AppleTVController:
    def __init__(self):
        self.host = os.getenv("APPLE_TV_HOST", "192.168.1.20")
        self.atvremote_path = shutil.which("atvremote") or "atvremote"

    # ==================================================
    # API PÚBLICA
    # ==================================================

    def executar(self, action=None, app_name=None):
        if not action:
            return "Não percebi o comando da Apple TV."

        if not self._atvremote_disponivel():
            return "Não encontrei o comando atvremote no sistema."

        try:
            log(f"📺 Apple TV @ {self.host} | action={action} | app_name={app_name}")

            if action == "menu":
                self._run("menu")
                return "Menu aberto."

            if action == "home":
                self._run("home")
                return "Ecrã principal aberto."

            if action == "up":
                self._run("up")
                return "Cima."

            if action == "down":
                self._run("down")
                return "Baixo."

            if action == "left":
                self._run("left")
                return "Esquerda."

            if action == "right":
                self._run("right")
                return "Direita."

            if action == "select":
                self._run("select")
                return "Selecionado."

            if action == "play":
                self._run("play")
                return "A reproduzir."

            if action == "pause":
                self._run("pause")
                return "Em pausa."

            if action == "next":
                self._run("next")
                return "A avançar."

            if action == "previous":
                self._run("previous")
                return "A voltar atrás."

            if action == "open_youtube":
                return self._macro_youtube()

            if action == "open_netflix":
                return self._macro_netflix()

            if action == "launch_app":
                nome = (app_name or "").strip().lower()

                if "youtube" in nome:
                    return self._macro_youtube()

                if "netflix" in nome:
                    return self._macro_netflix()

                return f"A macro para {app_name or 'essa app'} ainda não está configurada."

            return "Comando Apple TV não suportado."

        except Exception as e:
            log(f"❌ AppleTV erro: {e}")
            return f"Erro a controlar a Apple TV: {e}"

    # ==================================================
    # HELPERS
    # ==================================================

    def _atvremote_disponivel(self):
        return shutil.which("atvremote") is not None or self.atvremote_path == "atvremote"

    def _base_cmd(self):
        return [self.atvremote_path, "-s", self.host]

    def _run(self, command, timeout=10):
        cmd = self._base_cmd() + [command]
        log(f"📡 ATVREMOTE -> {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
        )

        stdout = (result.stdout or "").strip()
        stderr = (result.stderr or "").strip()

        if stdout:
            log(f"📺 atvremote stdout: {stdout}")
        if stderr:
            log(f"📺 atvremote stderr: {stderr}")

        if result.returncode != 0:
            raise RuntimeError(stderr or stdout or f"atvremote falhou com código {result.returncode}")

        return stdout

    def _step(self, command, sleep_time=0.35):
        self._run(command)
        time.sleep(sleep_time)

    def _go_home_anchor(self):
        # Pela tua foto, o home cai na app Apple TV (canto superior esquerdo)
        self._step("home", 1.0)

    # ==================================================
    # MACROS CALIBRADAS AO TEU LAYOUT
    # ==================================================

    def _macro_youtube(self):
        try:
            # Partida confirmada na tua foto:
            # Apple TV (top-left)
            # YouTube = down, down, right, right
            self._go_home_anchor()

            self._step("down")
            self._step("down")
            self._step("right")
            self._step("right")
            self._run("select")

            return "A abrir YouTube."

        except Exception as e:
            log(f"❌ Macro YouTube erro: {e}")
            return f"Erro ao abrir YouTube: {e}"

    def _macro_netflix(self):
        try:
            # Partida confirmada na tua foto:
            # Apple TV (top-left)
            # Netflix = down, down, right, right, right, right
            self._go_home_anchor()

            self._step("down")
            self._step("down")
            self._step("right")
            self._step("right")
            self._step("right")
            self._step("right")
            self._run("select")

            return "A abrir Netflix."

        except Exception as e:
            log(f"❌ Macro Netflix erro: {e}")
            return f"Erro ao abrir Netflix: {e}"