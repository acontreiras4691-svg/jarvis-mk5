import pvporcupine
import numpy as np
import time

from config.configuracoes import (
    ACCESS_KEY,
    LOG_ATIVO
)


class WakeWordEngine:

    def __init__(self, audio_manager):

        if LOG_ATIVO:
            print("🔹 A iniciar WakeWordEngine...")

        self.audio_manager = audio_manager

        try:

            self.porcupine = pvporcupine.create(
                access_key=ACCESS_KEY,
                keywords=["jarvis"],
                sensitivities=[0.65]  # melhor equilíbrio
            )

        except Exception as e:
            print("❌ Erro ao inicializar Porcupine:", e)
            raise

        self.frame_length = self.porcupine.frame_length
        self.sample_rate = self.porcupine.sample_rate

        self.buffer = np.array([], dtype=np.int16)

        # evitar triggers repetidos
        self.last_trigger = 0
        self.cooldown = 1.2

        if LOG_ATIVO:
            print("✅ WakeWordEngine pronto.")
            print(f"Sample rate: {self.sample_rate}")
            print(f"Frame length: {self.frame_length}")

    # ==================================================
    # DETETAR WAKE WORD
    # ==================================================

    def detectar(self):

        data = self.audio_manager.get_latest_chunk()

        if data is None:
            return False

        try:

            pcm = np.frombuffer(data, dtype=np.int16)

            self.buffer = np.concatenate((self.buffer, pcm))

            while len(self.buffer) >= self.frame_length:

                frame = self.buffer[:self.frame_length]
                self.buffer = self.buffer[self.frame_length:]

                result = self.porcupine.process(frame)

                if result >= 0:

                    agora = time.time()

                    # evitar triggers duplicados
                    if agora - self.last_trigger < self.cooldown:
                        return False

                    self.last_trigger = agora

                    if LOG_ATIVO:
                        print("🔥 WAKE WORD DETECTADA")

                    # limpar buffer
                    self.buffer = np.array([], dtype=np.int16)

                    return True

        except Exception as e:

            if LOG_ATIVO:
                print(f"❌ Erro WakeWord: {e}")

        return False

    # ==================================================
    # ENCERRAR
    # ==================================================

    def terminar(self):

        try:

            if self.porcupine:
                self.porcupine.delete()

            if LOG_ATIVO:
                print("🛑 WakeWordEngine encerrado.")

        except Exception as e:

            if LOG_ATIVO:
                print(f"Erro ao encerrar WakeWordEngine: {e}")