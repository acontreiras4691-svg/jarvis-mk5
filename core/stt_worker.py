# ==================================================
# STT WORKER - THREAD SEGURA
# ==================================================

from PyQt6.QtCore import QThread, pyqtSignal

from core.logger import log


class STTWorker(QThread):
    resultado = pyqtSignal(str)

    def __init__(self, stt):
        super().__init__()
        self.stt = stt
        self.running = True

    def run(self):
        if not self.running:
            return

        try:
            log("🎙️ STTWorker iniciado")

            texto = self.stt.transcrever()

            if not self.running:
                log("⛔ STTWorker cancelado antes de emitir resultado")
                return

            if texto and str(texto).strip():
                texto = str(texto).strip()
                log(f"✅ STTWorker resultado: {texto}")
                self.resultado.emit(texto)
            else:
                log("⚠️ STTWorker sem texto")
                self.resultado.emit("")

        except Exception as e:
            log(f"❌ STTWorker erro: {e}")
            self.resultado.emit("")

        finally:
            log("🧵 STTWorker terminado")

    def stop(self):
        self.running = False
        log("🛑 STTWorker stop pedido")