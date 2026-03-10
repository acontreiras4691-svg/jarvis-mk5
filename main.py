# ==================================================
# IMPORTS
# ==================================================

import os
import sys
import time
import datetime
import winsound
import requests

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from core.logger import log

log(f"RUNNING: {os.path.abspath(__file__)}")

from core.audio_manager import AudioManager
from core.stt import STT
from core.stt_worker import STTWorker
from core.tts import TTS
from core.gestor_conversa import GestorConversa
from core.estado import EstadoJarvis
from core.correcao_stt import corrigir_texto_stt

from voz.wakeword_engine import WakeWordEngine

from memoria.memoria_manager import MemoriaManager
from memoria.memoria_rag import MemoriaRAG

from interface.hud import iniciar_hud

from brain.brain_engine import BrainEngine


# ==================================================
# SERVIDOR JARVIS (LINUX)
# ==================================================

def perguntar_servidor_jarvis(texto):

    try:

        url = "http://192.168.1.108:5000/comando"

        resposta = requests.post(
            url,
            json={"texto": texto},
            timeout=20
        )

        return resposta.json()["resposta"]

    except Exception as e:

        log(f"❌ ERRO servidor Jarvis: {e}")

        return "Não consegui contactar o cérebro do Jarvis."


# ==================================================
# IMPORTS
# ==================================================

import os
import sys
import time
import winsound
import requests

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from core.logger import log

log(f"RUNNING: {os.path.abspath(__file__)}")

from core.audio_manager import AudioManager
from core.stt import STT
from core.stt_worker import STTWorker
from core.tts import TTS
from core.gestor_conversa import GestorConversa
from core.estado import EstadoJarvis
from core.correcao_stt import corrigir_texto_stt

from voz.wakeword_engine import WakeWordEngine

from memoria.memoria_manager import MemoriaManager
from memoria.memoria_rag import MemoriaRAG

from interface.hud import iniciar_hud

from brain.brain_engine import BrainEngine


# ==================================================
# SERVIDOR JARVIS (LINUX)
# ==================================================

def perguntar_servidor_jarvis(texto):

    try:

        url = "http://192.168.1.108:5000/comando"

        resposta = requests.post(
            url,
            json={"texto": texto},
            timeout=20
        )

        return resposta.json()["resposta"]

    except Exception as e:

        log(f"❌ ERRO servidor Jarvis: {e}")

        return "Não consegui contactar o cérebro do Jarvis."


# ==================================================
# IMPORTS
# ==================================================

import os
import sys
import time
import winsound
import requests

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from core.logger import log

log(f"RUNNING: {os.path.abspath(__file__)}")

from core.audio_manager import AudioManager
from core.stt import STT
from core.stt_worker import STTWorker
from core.tts import TTS
from core.gestor_conversa import GestorConversa
from core.estado import EstadoJarvis
from core.correcao_stt import corrigir_texto_stt

from voz.wakeword_engine import WakeWordEngine

from memoria.memoria_manager import MemoriaManager
from memoria.memoria_rag import MemoriaRAG

from interface.hud import iniciar_hud

from brain.brain_engine import BrainEngine


# ==================================================
# SERVIDOR JARVIS
# ==================================================

def perguntar_servidor_jarvis(texto):

    try:

        url = "http://192.168.1.108:5000/comando"

        resposta = requests.post(
            url,
            json={"texto": texto},
            timeout=20
        )

        return resposta.json()["resposta"]

    except Exception as e:

        log(f"❌ ERRO servidor Jarvis: {e}")

        return "Não consegui contactar o cérebro do Jarvis."


# ==================================================
# MAIN
# ==================================================

def main():

    log("==== JARVIS MK5 INICIADO ====")

    app = QApplication(sys.argv)

    # ------------------------------------------------
    # AUDIO
    # ------------------------------------------------

    audio_manager = AudioManager()

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
    app.stt_ativo = False
    app.jarvis_ocupado = False

    last_wake_time = 0

    app.setQuitOnLastWindowClosed(False)

# ==================================================
# STT
# ==================================================

    def iniciar_stt():

        if app.stt_ativo:
            return

        if tts.is_speaking:
            return

        if app.jarvis_ocupado:
            return

        log("🎤 Iniciar STT")

        hud.set_estado("OUVINDO")
        hud.set_texto("A ouvir...")

        try:

            # parar worker antigo
            if app.stt_worker:
                try:
                    app.stt_worker.stop()
                except:
                    pass

            app.stt_worker = STTWorker(stt)

            app.stt_worker.resultado.connect(processar_resultado_ui)

            app.stt_worker.start()

            app.stt_ativo = True

        except Exception as e:

            log(f"❌ ERRO STT: {e}")
            app.stt_ativo = False


# ==================================================
# PROCESSAR RESULTADO
# ==================================================

    def processar_resultado_ui(texto):

        app.stt_ativo = False

        try:

            if not texto or len(texto.strip()) < 2:

                log("⚠️ STT vazio")

                hud.set_estado("OUVINDO")
                hud.set_texto("Não ouvi bem...")

                QTimer.singleShot(400, iniciar_stt)
                return

            texto_original = corrigir_texto_stt(texto.strip())

            gestor.atualizar_interacao()

            log(f"🎤 STT: {texto_original}")

            # ------------------------------------------------
            # BRAIN ENGINE
            # ------------------------------------------------

            resposta_comando = brain.processar(texto_original)

            if resposta_comando:

                gestor.atualizar_interacao()

                hud.set_estado("RESPONDENDO")
                hud.set_texto(resposta_comando)

                tts.falar(resposta_comando)

                QTimer.singleShot(300, iniciar_stt)

                return

            # ------------------------------------------------
            # SERVIDOR JARVIS
            # ------------------------------------------------

            app.jarvis_ocupado = True

            hud.set_estado("PROCESSANDO")
            hud.set_texto("A pensar...")

            resposta_final = perguntar_servidor_jarvis(texto_original)

            def voltar():

                gestor.atualizar_interacao()

                app.jarvis_ocupado = False

                hud.set_estado("OUVINDO")

                QTimer.singleShot(300, iniciar_stt)

            tts.on_end_speak = voltar

            hud.set_estado("RESPONDENDO")

            tts.falar(resposta_final)

        except Exception as e:

            log(f"❌ ERRO processamento: {e}")

            app.jarvis_ocupado = False

            QTimer.singleShot(500, iniciar_stt)


# ==================================================
# LOOP PRINCIPAL
# ==================================================

    def ciclo():

        nonlocal last_wake_time

        try:

            gestor.verificar_timeout()

            # evitar wakeword durante STT
            if app.stt_ativo:
                return

            # evitar wakeword durante resposta
            if app.jarvis_ocupado:
                return

            detectado = wake_engine.detectar()

            if detectado:

                agora = time.time()

                if agora - last_wake_time < 1.5:
                    return

                last_wake_time = agora

                log("🔥 WAKE WORD DETECTADA")

                if tts.is_speaking:

                    log("🛑 Interrupção de voz")

                    tts.stop()

                winsound.Beep(1200, 80)

                gestor.ativar()

                hud.set_estado("OUVINDO")
                hud.set_texto("Sim, Dudu?")

                QTimer.singleShot(400, iniciar_stt)

                return

            # ------------------------------------------------
            # CONTINUAR CONVERSA
            # ------------------------------------------------

            if gestor.estado == EstadoJarvis.ATIVO:

                if (
                    not app.stt_ativo
                    and not tts.is_speaking
                    and not app.jarvis_ocupado
                ):

                    iniciar_stt()

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