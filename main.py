# ==================================================
# MAIN - JARVIS MK5
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
from core.correcao_stt import corrigir_texto_stt

from voz.wakeword_engine import WakeWordEngine

from memoria.memoria_manager import MemoriaManager
from memoria.memoria_rag import MemoriaRAG

from interface.hud import iniciar_hud
from brain.brain_engine import BrainEngine
from smart_home.hybrid_smart_home import HybridSmartHome


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

INITIAL_STT_DELAY = 0.50
FOLLOWUP_STT_DELAY = 0.70
EMPTY_RETRY_DELAY = 0.90


# ==================================================
# WORKER SERVIDOR
# ==================================================

class ServerWorker(QThread):
    resultado = pyqtSignal(str)
    erro = pyqtSignal(str)

    def __init__(self, texto: str):
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
            resposta_texto = str(data.get("resposta", "")).strip()

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
    # INIT BASE
    # ------------------------------------------------
    try:
        audio_manager = AudioManager()

        for d in audio_manager.listar_dispositivos():
            if d["maxInputChannels"] > 0:
                log(f"MIC -> index={d['index']} | name={d['name']}")

        hud = iniciar_hud(audio_manager)
        hud.show()
        hud.set_texto("A carregar sistemas...")
        hud.set_estado("PROCESSANDO")

    except Exception as e:
        log(f"❌ ERRO init base: {e}")
        return

    # ------------------------------------------------
    # WAKE WORD
    # ------------------------------------------------
    try:
        wake_engine = WakeWordEngine(audio_manager)
        log("✅ WakeWordEngine pronto.")
    except Exception as e:
        log(f"❌ ERRO WakeWordEngine: {e}")
        return

    # ------------------------------------------------
    # STT
    # ------------------------------------------------
    try:
        stt = STT(audio_manager)
        log("🔄 A carregar Whisper...")
        stt.carregar_modelo()
        log("✅ Whisper pronto.")
    except Exception as e:
        log(f"❌ ERRO STT/Whisper: {e}")
        return

    # ------------------------------------------------
    # TTS
    # ------------------------------------------------
    try:
        tts = TTS()
        log("✅ TTS pronto.")
    except Exception as e:
        log(f"❌ ERRO TTS: {e}")
        return

    # ------------------------------------------------
    # CORE
    # ------------------------------------------------
    gestor = GestorConversa()
    memoria = MemoriaManager()
    memoria_rag = MemoriaRAG()
    smart_home = HybridSmartHome()

    try:
        brain = BrainEngine(
            memoria,
            memoria_rag,
            smart_home=smart_home
        )
        log("✅ BrainEngine pronto.")
    except Exception as e:
        log(f"❌ ERRO BrainEngine: {e}")
        return

    hud.set_texto("Jarvis MK5 online.")
    hud.set_estado("IDLE")

    # ------------------------------------------------
    # ESTADO GLOBAL APP
    # ------------------------------------------------
    app.stt_worker = None
    app.server_worker = None

    app.stt_ativo = False
    app.jarvis_ocupado = False

    app.modo_conversa = False
    app.conversa_ate = 0.0
    app.followup_retries = 0
    app.next_stt_time = 0.0
    app.force_end_conversation = False

    app.encerrar = False

    last_wake_time = 0.0
    ultimo_log_wake = 0.0

    # ==================================================
    # HELPERS
    # ==================================================

    def pode_ouvir() -> bool:
        return (
            not app.encerrar
            and not app.stt_ativo
            and not app.jarvis_ocupado
            and not getattr(tts, "is_speaking", False)
        )

    def ativar_modo_conversa():
        app.modo_conversa = True
        app.conversa_ate = time.time() + FOLLOWUP_WINDOW
        app.followup_retries = 0

    def desativar_modo_conversa():
        app.modo_conversa = False
        app.conversa_ate = 0.0
        app.followup_retries = 0

    def agendar_stt(delay_segundos: float):
        app.next_stt_time = time.time() + delay_segundos

    def limpar_agendamento_stt():
        app.next_stt_time = 0.0

    def resetar_para_idle():
        app.jarvis_ocupado = False
        app.stt_ativo = False
        app.force_end_conversation = False
        limpar_agendamento_stt()
        desativar_modo_conversa()

        if not app.encerrar:
            hud.set_estado("IDLE")
            hud.set_texto("Jarvis MK5 online.")

    def beep_wake():
        try:
            winsound.Beep(1200, 80)
        except Exception as e:
            log(f"⚠️ beep falhou: {e}")

    def limpar_stt_worker():
        if app.stt_worker:
            try:
                if hasattr(app.stt_worker, "stop"):
                    app.stt_worker.stop()
            except Exception as e:
                log(f"⚠️ erro ao parar STTWorker: {e}")

            try:
                app.stt_worker.wait(500)
            except Exception as e:
                log(f"⚠️ erro ao esperar STTWorker: {e}")

            app.stt_worker = None

    def limpar_server_worker():
        app.server_worker = None

    def on_stt_finished():
        app.stt_ativo = False

    def finalizar_resposta():
        try:
            gestor.atualizar_interacao()
        except Exception as e:
            log(f"⚠️ erro atualizar interação: {e}")

        app.jarvis_ocupado = False
        app.stt_ativo = False

        if app.force_end_conversation:
            resetar_para_idle()
            return

        ativar_modo_conversa()

        hud.set_estado("OUVINDO")
        hud.set_texto("Estou a ouvir...")

        agendar_stt(FOLLOWUP_STT_DELAY)

    def cleanup():
        log("🛑 A encerrar Jarvis MK5...")
        app.encerrar = True

        try:
            if hasattr(app, "timer") and app.timer:
                app.timer.stop()
        except Exception:
            pass

        try:
            limpar_agendamento_stt()
            desativar_modo_conversa()
        except Exception:
            pass

        try:
            limpar_stt_worker()
        except Exception:
            pass

        try:
            if app.server_worker and app.server_worker.isRunning():
                app.server_worker.quit()
                app.server_worker.wait(500)
        except Exception:
            pass

        try:
            if getattr(tts, "is_speaking", False):
                tts.stop()
        except Exception:
            pass

    app.aboutToQuit.connect(cleanup)

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
        app.stt_worker.finished.connect(on_stt_finished)
        app.stt_worker.start()

        app.stt_ativo = True
        limpar_agendamento_stt()

    # ==================================================
    # RESPOSTA LOCAL
    # ==================================================

    def responder_localmente(resposta: str):
        resposta = str(resposta).strip()

        if not resposta:
            resetar_para_idle()
            return

        app.jarvis_ocupado = True

        hud.set_estado("RESPONDENDO")
        hud.set_texto(resposta)

        tts.on_end_speak = finalizar_resposta
        tts.falar(resposta)

    # ==================================================
    # SERVIDOR
    # ==================================================

    def perguntar_servidor_async(texto: str):
        app.jarvis_ocupado = True

        hud.set_estado("PROCESSANDO")
        hud.set_texto("A pensar...")

        if app.server_worker and app.server_worker.isRunning():
            log("⚠️ Já existe ServerWorker ativo.")
            return

        app.server_worker = ServerWorker(texto)
        app.server_worker.resultado.connect(processar_resposta_servidor)
        app.server_worker.erro.connect(processar_erro_servidor)
        app.server_worker.finished.connect(limpar_server_worker)
        app.server_worker.start()

    def processar_resposta_servidor(resposta: str):
        resposta = str(resposta).strip()

        if not resposta:
            resposta = "Não consegui gerar uma resposta."

        hud.set_estado("RESPONDENDO")
        hud.set_texto(resposta)

        tts.on_end_speak = finalizar_resposta
        tts.falar(resposta)

    def processar_erro_servidor(msg: str):
        msg = str(msg).strip() or "Erro no servidor."

        hud.set_estado("RESPONDENDO")
        hud.set_texto(msg)

        app.force_end_conversation = True
        tts.on_end_speak = finalizar_resposta
        tts.falar(msg)

    # ==================================================
    # PROCESSAR STT
    # ==================================================

    def processar_resultado_ui(texto: str):
        app.stt_ativo = False

        try:
            texto = (texto or "").strip()

            if len(texto) < 2:
                log("⚠️ STT vazio")

                if app.modo_conversa and time.time() < app.conversa_ate:
                    if app.followup_retries < FOLLOWUP_MAX_RETRIES:
                        app.followup_retries += 1
                        hud.set_estado("OUVINDO")
                        hud.set_texto("Estou a ouvir...")
                        agendar_stt(EMPTY_RETRY_DELAY)
                        return

                resetar_para_idle()
                return

            ativar_modo_conversa()
            app.followup_retries = 0

            texto_original = corrigir_texto_stt(texto)
            log(f"🎤 STT: {texto_original}")

            resposta_brain = brain.processar(texto_original)

            if resposta_brain:
                if isinstance(resposta_brain, dict):
                    resposta_texto = str(resposta_brain.get("text", "")).strip()
                    app.force_end_conversation = bool(
                        resposta_brain.get("end_conversation", False)
                    )
                else:
                    resposta_texto = str(resposta_brain).strip()
                    app.force_end_conversation = False

                if resposta_texto:
                    responder_localmente(resposta_texto)
                    return

            app.force_end_conversation = False
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
            if app.encerrar:
                return

            if app.stt_ativo or app.jarvis_ocupado:
                return

            if (
                app.next_stt_time > 0
                and time.time() >= app.next_stt_time
                and pode_ouvir()
            ):
                iniciar_stt()
                return

            if app.modo_conversa:
                if time.time() >= app.conversa_ate:
                    resetar_para_idle()
                    return
                return

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

                log("🔥 WAKE WORD DETETADA")

                try:
                    if getattr(tts, "is_speaking", False):
                        tts.stop()
                except Exception:
                    pass

                try:
                    audio_manager.clear_buffer()
                except Exception:
                    pass

                beep_wake()

                hud.set_estado("OUVINDO")
                hud.set_texto("Sim, Dudu?")

                desativar_modo_conversa()
                app.followup_retries = 0
                app.force_end_conversation = False
                agendar_stt(INITIAL_STT_DELAY)

        except Exception as e:
            log(f"❌ ERRO ciclo: {e}")

    # ==================================================
    # TIMER LOOP
    # ==================================================

    app.timer = QTimer()
    app.timer.timeout.connect(ciclo)
    app.timer.start(40)

    log(">>> SISTEMA MK5 OPERACIONAL <<<")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()