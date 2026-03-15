# ==================================================
# STT WORKER (THREAD SEGURA)
# ==================================================

from PyQt6.QtCore import QThread, pyqtSignal


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
            texto = self.stt.transcrever()

            if not self.running:
                return

            if texto and texto.strip():
                self.resultado.emit(texto.strip())
            else:
                self.resultado.emit("")

        except Exception:
            self.resultado.emit("")

    def stop(self):
        self.running = False