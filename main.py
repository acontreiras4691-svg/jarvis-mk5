# ==================================================
# IMPORTS
# ==================================================

import os
import sys
import time
import requests
import winsound

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, QThread, pyqtSignal

from core.logger import log
from core.audio_manager import AudioManager
from core.stt import STT
from core.stt_worker import STTWorker
from core.tts import TTS
from core.gestor_conversa import GestorConversa

from voz.wakeword_engine import WakeWordEngine

from memoria.memoria_manager import MemoriaManager
from memoria.memoria_rag import MemoriaRAG

from interface.hud import iniciar_hud

from brain.brain_engine import BrainEngine


log(f"RUNNING: {os.path.abspath(__file__)}")


# ==================================================
# CONFIG
# ==================================================

JARVIS_SERVER_URL = "http://192.168.1.108:5000/comando"
SERVER_TIMEOUT = 10

WAKE_COOLDOWN = 1.5
DEBUG_WAKEWORD = True

FOLLOWUP_WINDOW = 10.0
FOLLOWUP_MAX_RETRIES = 2


# ==================================================
# WORKER SERVIDOR
# ==================================================

class ServerWorker(QThread):

    resultado = pyqtSignal(str)
    erro = pyqtSignal(str)

    def __init__(self, texto):
        super().__init__()
        self.texto = texto

    def run(self):
        try:
            resposta = requests.post(
                JARVIS_SERVER_URL,
                json={"texto": self.texto},
                timeout=SERVER_TIMEOUT
            )

            resposta.raise_for_status()

            data = resposta.json()
            resposta_texto = data.get("resposta", "").strip()

            if not resposta_texto:
                resposta_texto = "O cérebro respondeu sem conteúdo."

            self.resultado.emit(resposta_texto)

        except Exception as e:
            log(f"❌ ERRO servidor Jarvis: {e}")
            self.erro.emit("Não consegui contactar o cérebro do Jarvis.")


# ==================================================
# MAIN
# ==================================================

def main():

    log("==== JARVIS MK5 INICIADO ====")

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # ------------------------------------------------
    # AUDIO
    # ------------------------------------------------

    audio_manager = AudioManager()

    for d in audio_manager.listar_dispositivos():
        if d["maxInputChannels"] > 0:
            log(f"MIC -> index={d['index']} | name={d['name']}")

    # ------------------------------------------------
    # HUD
    # ------------------------------------------------

    hud = iniciar_hud(audio_manager)
    hud.show()
    hud.set_texto("A carregar sistemas...")
    hud.set_estado("PROCESSANDO")

    # ------------------------------------------------
    # MÓDULOS
    # ------------------------------------------------

    wake_engine = WakeWordEngine(audio_manager)

    stt = STT(audio_manager)
    log("🔄 A carregar Whisper...")
    stt.carregar_modelo()
    log("✅ Whisper pronto.")

    tts = TTS()

    gestor = GestorConversa()

    memoria = MemoriaManager()
    memoria_rag = MemoriaRAG()

    brain = BrainEngine(memoria, memoria_rag)

    hud.set_texto("Jarvis MK5 online.")
    hud.set_estado("IDLE")

    # ------------------------------------------------
    # FLAGS
    # ------------------------------------------------

    app.stt_worker = None
    app.server_worker = None

    app.stt_ativo = False
    app.jarvis_ocupado = False

    app.modo_conversa = False
    app.conversa_ate = 0.0
    app.followup_retries = 0
    app.next_stt_time = 0.0

    last_wake_time = 0
    ultimo_log_wake = 0

    # ==================================================
    # HELPERS
    # ==================================================

    def pode_ouvir():
        return (
            not app.stt_ativo
            and not app.jarvis_ocupado
            and not tts.is_speaking
        )

    def ativar_modo_conversa():
        app.modo_conversa = True
        app.conversa_ate = time.time() + FOLLOWUP_WINDOW
        app.followup_retries = 0

    def desativar_modo_conversa():
        app.modo_conversa = False
        app.conversa_ate = 0.0
        app.followup_retries = 0
        app.next_stt_time = 0.0

    def agendar_stt(delay_segundos: float):
        app.next_stt_time = time.time() + delay_segundos

    def resetar_para_idle():
        app.jarvis_ocupado = False
        app.stt_ativo = False
        desativar_modo_conversa()
        hud.set_estado("IDLE")
        hud.set_texto("Jarvis MK5 online.")

    def beep_wake():
        try:
            winsound.Beep(1200, 80)
        except Exception as e:
            log(f"⚠️ beep falhou: {e}")

    def stt_finalizado():
        app.stt_ativo = False

    def limpar_stt_worker():
        if app.stt_worker:
            try:
                app.stt_worker.stop()
            except Exception:
                pass

            try:
                app.stt_worker.wait(300)
            except Exception:
                pass

            app.stt_worker = None

    def limpar_server_worker():
        app.server_worker = None

    def finalizar_resposta():
        gestor.atualizar_interacao()

        app.jarvis_ocupado = False
        app.stt_ativo = False

        ativar_modo_conversa()

        hud.set_estado("OUVINDO")
        hud.set_texto("Estou a ouvir...")

        agendar_stt(0.7)

    # ==================================================
    # STT
    # ==================================================

    def iniciar_stt():

        if not pode_ouvir():
            return

        log("🎤 Iniciar STT")

        try:
            audio_manager.clear_buffer()
        except Exception:
            pass

        hud.set_estado("OUVINDO")
        hud.set_texto("A ouvir...")

        limpar_stt_worker()

        app.stt_worker = STTWorker(stt)
        app.stt_worker.resultado.connect(processar_resultado_ui)
        app.stt_worker.finished.connect(stt_finalizado)
        app.stt_worker.start()

        app.stt_ativo = True
        app.next_stt_time = 0.0

    # ==================================================
    # RESPOSTA LOCAL
    # ==================================================

    def responder_localmente(resposta):

        app.jarvis_ocupado = True

        hud.set_estado("RESPONDENDO")
        hud.set_texto(resposta)

        tts.on_end_speak = finalizar_resposta
        tts.falar(resposta)

    # ==================================================
    # SERVIDOR
    # ==================================================

    def perguntar_servidor_async(texto):

        app.jarvis_ocupado = True

        hud.set_estado("PROCESSANDO")
        hud.set_texto("A pensar...")

        app.server_worker = ServerWorker(texto)
        app.server_worker.resultado.connect(processar_resposta_servidor)
        app.server_worker.erro.connect(processar_erro_servidor)
        app.server_worker.finished.connect(limpar_server_worker)
        app.server_worker.start()

    def processar_resposta_servidor(resposta):

        hud.set_estado("RESPONDENDO")
        hud.set_texto(resposta)

        tts.on_end_speak = finalizar_resposta
        tts.falar(resposta)

    def processar_erro_servidor(msg):

        hud.set_estado("RESPONDENDO")
        hud.set_texto(msg)

        tts.on_end_speak = resetar_para_idle
        tts.falar(msg)

    # ==================================================
    # PROCESSAR STT
    # ==================================================

    def processar_resultado_ui(texto):

        app.stt_ativo = False

        try:
            if not texto or len(texto.strip()) < 2:

                log("⚠️ STT vazio")

                if app.modo_conversa and time.time() < app.conversa_ate:
                    if app.followup_retries < FOLLOWUP_MAX_RETRIES:
                        app.followup_retries += 1
                        hud.set_estado("OUVINDO")
                        hud.set_texto("Estou a ouvir...")
                        agendar_stt(0.8)
                        return

                resetar_para_idle()
                return

            app.followup_retries = 0

            texto_original = texto.strip()

            log(f"🎤 STT: {texto_original}")

            resposta_comando = brain.processar(texto_original)

            if resposta_comando:
                responder_localmente(resposta_comando)
                return

            perguntar_servidor_async(texto_original)

        except Exception as e:
            log(f"❌ ERRO processamento: {e}")
            resetar_para_idle()

    # ==================================================
    # LOOP PRINCIPAL
    # ==================================================

    def ciclo():

        nonlocal last_wake_time, ultimo_log_wake

        try:
            if app.stt_ativo or app.jarvis_ocupado:
                return

            # ------------------------------------------
            # FOLLOW-UP CONTROLADO
            # ------------------------------------------

            if app.modo_conversa:

                if time.time() >= app.conversa_ate:
                    resetar_para_idle()
                    return

                if app.next_stt_time > 0 and time.time() >= app.next_stt_time and pode_ouvir():
                    iniciar_stt()
                    return

                return

            # ------------------------------------------
            # WAKEWORD NORMAL
            # ------------------------------------------

            if DEBUG_WAKEWORD:
                agora_log = time.time()
                if agora_log - ultimo_log_wake > 3:
                    log("🔄 ciclo wakeword ativo")
                    ultimo_log_wake = agora_log

            detectado = wake_engine.detectar()

            if DEBUG_WAKEWORD and detectado:
                log("🟢 wake_engine.detectar() devolveu True")

            if detectado:
                agora = time.time()

                if agora - last_wake_time < WAKE_COOLDOWN:
                    return

                last_wake_time = agora

                log("🔥 WAKE WORD DETECTADA")

                try:
                    audio_manager.clear_buffer()
                except Exception:
                    pass

                beep_wake()

                hud.set_estado("OUVINDO")
                hud.set_texto("Sim, Dudu?")

                desativar_modo_conversa()
                agendar_stt(0.5)

        except Exception as e:
            log(f"❌ ERRO ciclo: {e}")

    # ==================================================
    # TIMER
    # ==================================================

    app.timer = QTimer()
    app.timer.timeout.connect(ciclo)
    app.timer.start(40)

    log(">>> SISTEMA MK5 OPERACIONAL <<<")

    sys.exit(app.exec())


# ==================================================
# START
# ==================================================

if __name__ == "__main__":
    main()