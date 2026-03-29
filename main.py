# ==================================================
# MAIN - JARVIS MK5
# Wakeword + STT + Follow-up por deteção de voz
# ==================================================

import os
import sys
import time
import winsound

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

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

INITIAL_STT_DELAY = 0.40
WAKE_COOLDOWN = 1.0

FOLLOWUP_WINDOW = 8.0
FOLLOWUP_MAX_RETRIES = 1

DEBUG_WAKEWORD = True

# follow-up por voz
FOLLOWUP_VOICE_LEVEL = 0.030
FOLLOWUP_VOICE_HITS_REQUIRED = 4
FOLLOWUP_ARM_DELAY = 1.00


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
    try:
        gestor = GestorConversa()
        memoria = MemoriaManager()
        memoria_rag = MemoriaRAG()
        smart_home = HybridSmartHome()

        brain = BrainEngine(
            memoria,
            memoria_rag,
            smart_home=smart_home
        )

        log("✅ BrainEngine pronto.")

    except Exception as e:
        log(f"❌ ERRO BrainEngine/Core: {e}")
        return

    hud.set_texto("Jarvis MK5 online.")
    hud.set_estado("IDLE")

    # ------------------------------------------------
    # ESTADO GLOBAL
    # ------------------------------------------------
    app.stt_worker = None

    app.stt_ativo = False
    app.jarvis_ocupado = False
    app.aguardando_stt = False

    app.modo_conversa = False
    app.conversa_ate = 0.0
    app.followup_retries = 0
    app.followup_arm_time = 0.0
    app.followup_voice_hits = 0

    app.next_stt_time = 0.0
    app.force_end_conversation = False
    app.encerrar = False

    last_wake_time = 0.0
    ultimo_log_wake = 0.0

    # ==================================================
    # HELPERS
    # ==================================================

    def pode_ouvir():
        return (
            not app.encerrar
            and not app.stt_ativo
            and not app.jarvis_ocupado
            and not app.aguardando_stt
            and not getattr(tts, "is_speaking", False)
        )

    def ativar_modo_conversa():
        app.modo_conversa = True
        app.conversa_ate = time.time() + FOLLOWUP_WINDOW
        app.followup_retries = 0
        app.followup_arm_time = time.time() + FOLLOWUP_ARM_DELAY
        app.followup_voice_hits = 0

    def desativar_modo_conversa():
        app.modo_conversa = False
        app.conversa_ate = 0.0
        app.followup_retries = 0
        app.followup_arm_time = 0.0
        app.followup_voice_hits = 0

    def agendar_stt(delay_segundos: float):
        app.aguardando_stt = True
        app.next_stt_time = time.time() + delay_segundos

    def limpar_agendamento_stt():
        app.next_stt_time = 0.0
        app.aguardando_stt = False

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
            winsound.Beep(1200, 60)
        except Exception as e:
            log(f"⚠️ beep falhou: {e}")

    def limpar_stt_worker():
        worker = app.stt_worker
        if not worker:
            return

        try:
            if hasattr(worker, "stop"):
                worker.stop()
        except Exception as e:
            log(f"⚠️ erro ao parar STTWorker: {e}")

        try:
            worker.wait(300)
        except Exception as e:
            log(f"⚠️ erro ao esperar STTWorker: {e}")

        app.stt_worker = None

    def on_stt_finished():
        app.stt_ativo = False

    def finalizar_resposta():
        try:
            gestor.atualizar_interacao()
        except Exception as e:
            log(f"⚠️ erro atualizar interação: {e}")

        app.jarvis_ocupado = False
        app.stt_ativo = False

        resetar_para_idle()

        if app.force_end_conversation:
            resetar_para_idle()
            return

        ativar_modo_conversa()

        hud.set_estado("IDLE")
        hud.set_texto("Aguardando comando...")

    def falar_resposta(resposta: str, end_conversation: bool = False):
        resposta = str(resposta or "").strip()

        if not resposta:
            resetar_para_idle()
            return

        app.force_end_conversation = bool(end_conversation)
        app.jarvis_ocupado = True
        app.stt_ativo = False
        limpar_agendamento_stt()

        hud.set_estado("RESPONDENDO")
        hud.set_texto(resposta)

        try:
            tts.on_end_speak = finalizar_resposta
        except Exception:
            pass

        try:
            tts.falar(resposta)
        except Exception as e:
            log(f"❌ ERRO TTS falar: {e}")
            resetar_para_idle()

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
            if getattr(tts, "is_speaking", False):
                tts.stop()
        except Exception:
            pass

        try:
            if hasattr(wake_engine, "terminar"):
                wake_engine.terminar()
        except Exception:
            pass

        try:
            if hasattr(audio_manager, "stop"):
                audio_manager.stop()
        except Exception:
            pass

    app.aboutToQuit.connect(cleanup)

    # ==================================================
    # STT
    # ==================================================

    def iniciar_stt():
        if app.encerrar or app.stt_ativo or app.jarvis_ocupado or getattr(tts, "is_speaking", False):
            return

        log("🎤 Iniciar STT")

        hud.set_estado("OUVINDO")
        hud.set_texto("A ouvir...")

        limpar_stt_worker()

        app.aguardando_stt = False
        app.followup_voice_hits = 0

        app.stt_worker = STTWorker(stt)
        app.stt_worker.resultado.connect(processar_resultado_ui)
        app.stt_worker.finished.connect(on_stt_finished)

        app.stt_ativo = True
        limpar_agendamento_stt()

        app.stt_worker.start()

    # ==================================================
    # RESPOSTA LOCAL
    # ==================================================

    def responder_localmente(resposta: str, end_conversation: bool = False):
        falar_resposta(resposta, end_conversation=end_conversation)

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
                        hud.set_estado("IDLE")
                        hud.set_texto("Aguardando comando...")
                        return

                resetar_para_idle()
                return

            texto_original = corrigir_texto_stt(texto)
            log(f"🎤 STT final: {texto_original}")

            app.followup_retries = 0

            resposta_brain = brain.processar(texto_original)

            if resposta_brain:
                if isinstance(resposta_brain, dict):
                    resposta_texto = str(resposta_brain.get("text", "")).strip()
                    end_conversation = bool(
                        resposta_brain.get("end_conversation", False)
                    )
                else:
                    resposta_texto = str(resposta_brain).strip()
                    end_conversation = False

                if resposta_texto:
                    responder_localmente(
                        resposta_texto,
                        end_conversation=end_conversation
                    )
                    return

            responder_localmente("Não percebi.", end_conversation=False)

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

            # STT agendado pela wakeword
            if app.aguardando_stt:
                if (
                    app.next_stt_time > 0
                    and time.time() >= app.next_stt_time
                    and not app.stt_ativo
                    and not app.jarvis_ocupado
                    and not getattr(tts, "is_speaking", False)
                ):
                    iniciar_stt()
                return

            if app.stt_ativo or app.jarvis_ocupado:
                return

            # FOLLOW-UP: ouvir voz sem nova wakeword
            if app.modo_conversa:
                if time.time() >= app.conversa_ate:
                    resetar_para_idle()
                    return

                if time.time() < app.followup_arm_time:
                    return

                nivel = audio_manager.get_audio_level()

                if nivel >= FOLLOWUP_VOICE_LEVEL:
                    app.followup_voice_hits += 1
                else:
                    app.followup_voice_hits = 0

                if app.followup_voice_hits >= FOLLOWUP_VOICE_HITS_REQUIRED:
                    log(f"🗣️ Voz detetada em follow-up (nível={nivel:.4f})")
                    iniciar_stt()

                return

            if DEBUG_WAKEWORD:
                agora_log = time.time()
                if agora_log - ultimo_log_wake > 2:
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
    # TIMER
    # ==================================================

    app.timer = QTimer()
    app.timer.timeout.connect(ciclo)
    app.timer.start(35)

    log(">>> SISTEMA MK5 OPERACIONAL <<<")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()