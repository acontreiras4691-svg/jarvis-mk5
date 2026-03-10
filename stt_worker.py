from PyQt6.QtCore import QThread, pyqtSignal

class STTWorker(QThread):

    resultado = pyqtSignal(str)

    def __init__(self, stt_instance):
        super().__init__()
        self.stt = stt_instance
        self._running = True

    def run(self):
        texto = self.stt.ouvir()
        if self._running:
            self.resultado.emit(texto)

    def parar(self):
        self._running = False