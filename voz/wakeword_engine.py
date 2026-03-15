import time
import numpy as np
import pvporcupine

from core.logger import log
from config.configuracoes import (
    ACCESS_KEY,
    LOG_ATIVO,
    WAKEWORD_KEYWORD,
    WAKEWORD_SENSIBILIDADE
)


class WakeWordEngine:

    def __init__(self, audio_manager):
        self.audio_manager = audio_manager
        self.last_trigger = 0
        self.cooldown = 1.2
        self.buffer = np.array([], dtype=np.int16)
        self.last_debug_log = 0

        if LOG_ATIVO:
            log("🔹 A iniciar WakeWordEngine...")

        try:
            self.porcupine = pvporcupine.create(
                access_key=ACCESS_KEY,
                keywords=[WAKEWORD_KEYWORD],
                sensitivities=[WAKEWORD_SENSIBILIDADE]
            )

        except Exception as e:
            log(f"❌ Erro ao inicializar Porcupine: {e}")
            raise

        self.frame_length = self.porcupine.frame_length
        self.sample_rate = self.porcupine.sample_rate

        if LOG_ATIVO:
            log("✅ WakeWordEngine pronto.")
            log(f"Keyword: {WAKEWORD_KEYWORD}")
            log(f"Sensibilidade: {WAKEWORD_SENSIBILIDADE}")
            log(f"Sample rate Porcupine: {self.sample_rate}")
            log(f"Frame length Porcupine: {self.frame_length}")

    # ==================================================
    # DETETAR WAKE WORD
    # ==================================================

    def detectar(self):
        try:
            data = self.audio_manager.get_latest_chunk()

            if data is None:
                return False

            if len(data) == 0:
                return False

            pcm = np.frombuffer(data, dtype=np.int16)

            if pcm.size == 0:
                return False

            # debug leve de tempos a tempos
            agora_debug = time.time()
            if LOG_ATIVO and (agora_debug - self.last_debug_log > 5):
                nivel = float(np.abs(pcm).mean() / 32768.0) if pcm.size > 0 else 0.0
                log(
                    f"🎙️ Wake debug | samples={pcm.size} | "
                    f"buffer={len(self.buffer)} | nivel={nivel:.4f}"
                )
                self.last_debug_log = agora_debug

            self.buffer = np.concatenate((self.buffer, pcm))

            while len(self.buffer) >= self.frame_length:
                frame = self.buffer[:self.frame_length]
                self.buffer = self.buffer[self.frame_length:]

                frame = np.asarray(frame, dtype=np.int16)

                result = self.porcupine.process(frame)

                if result >= 0:
                    agora = time.time()

                    if agora - self.last_trigger < self.cooldown:
                        return False

                    self.last_trigger = agora

                    if LOG_ATIVO:
                        log("🔥 WAKE WORD DETETADA")

                    self.buffer = np.array([], dtype=np.int16)
                    return True

        except Exception as e:
            if LOG_ATIVO:
                log(f"❌ Erro WakeWord: {e}")

        return False

    # ==================================================
    # ENCERRAR
    # ==================================================

    def terminar(self):
        try:
            if hasattr(self, "porcupine") and self.porcupine is not None:
                self.porcupine.delete()

            if LOG_ATIVO:
                log("🛑 WakeWordEngine encerrado.")

        except Exception as e:
            if LOG_ATIVO:
                log(f"❌ Erro ao encerrar WakeWordEngine: {e}")