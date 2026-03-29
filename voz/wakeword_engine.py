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
        self.last_trigger = 0.0
        self.cooldown = 0.8

        self.buffer = np.array([], dtype=np.int16)
        self.last_debug_log = 0.0

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
            log(f"Frame length: {self.frame_length}")
            log(f"Sample rate esperado: {self.sample_rate}")

    def detectar(self):
        try:
            data = self.audio_manager.get_latest_chunk()

            if not data:
                return False

            pcm = np.frombuffer(data, dtype=np.int16)

            if pcm.size == 0:
                return False

            nivel = float(np.abs(pcm).mean() / 32768.0)

            agora_debug = time.time()
            if LOG_ATIVO and (agora_debug - self.last_debug_log > 3):
                log(
                    f"🎙️ Wake debug | samples={pcm.size} | "
                    f"buffer={len(self.buffer)} | nivel={nivel:.4f}"
                )
                self.last_debug_log = agora_debug

            # guardar buffer sem cortar demasiado cedo
            self.buffer = np.concatenate((self.buffer, pcm))

            # manter no máximo 4 frames acumulados
            max_samples = self.frame_length * 4
            if len(self.buffer) > max_samples:
                self.buffer = self.buffer[-max_samples:]

            while len(self.buffer) >= self.frame_length:
                frame = self.buffer[:self.frame_length]
                self.buffer = self.buffer[self.frame_length:]

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

    def terminar(self):
        try:
            if hasattr(self, "porcupine") and self.porcupine is not None:
                self.porcupine.delete()

            if LOG_ATIVO:
                log("🛑 WakeWordEngine encerrado.")

        except Exception as e:
            if LOG_ATIVO:
                log(f"❌ Erro ao encerrar WakeWordEngine: {e}")