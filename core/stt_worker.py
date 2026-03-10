# ==================================================
# STT WORKER (THREAD SEGURA PARA QT)
# ==================================================

from PyQt6.QtCore import QThread, pyqtSignal
from core.logger import log


class STTWorker(QThread):

    resultado = pyqtSignal(str)

    def __init__(self, stt):

        super().__init__()

        self.stt = stt
        self.running = True

    # ==================================================
    # THREAD
    # ==================================================

    def run(self):

        if not self.running:
            return

        try:

            log("🎤 STTWorker iniciado")

            texto = self.stt.transcrever()

            if not self.running:
                return

            if texto and len(texto.strip()) > 0:

                log(f"🧠 STTWorker resultado: {texto}")

                self.resultado.emit(texto)

            else:

                self.resultado.emit("")

        except Exception as e:

            log(f"❌ Erro STTWorker: {e}")

            try:
                self.resultado.emit("")
            except:
                pass

    # ==================================================
    # PARAR THREAD
    # ==================================================

    def stop(self):

        self.running = False

        try:
            self.quit()
        except:
            pass

        try:
            self.wait(100)
        except:
            pass