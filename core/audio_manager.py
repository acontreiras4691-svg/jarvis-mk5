import pyaudio
import threading
import numpy as np
import collections
import time

from config.configuracoes import (
    MIC_INPUT_INDEX,
    SAMPLE_RATE,
    CHUNK_SIZE,
    CHANNELS
)


class AudioManager:

    def __init__(self):

        print("🎤 A iniciar AudioManager...")

        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(
            rate=SAMPLE_RATE,
            channels=CHANNELS,
            format=pyaudio.paInt16,
            input=True,
            input_device_index=MIC_INPUT_INDEX,
            frames_per_buffer=CHUNK_SIZE
        )

        # ------------------------------------------------
        # BUFFER CIRCULAR DE ÁUDIO
        # ------------------------------------------------

        # 200 chunks ≈ vários segundos de áudio
        self.buffer_queue = collections.deque(maxlen=200)

        self.lock = threading.Lock()
        self.running = True

        # Thread de captura contínua
        self.thread = threading.Thread(
            target=self._capture_loop,
            daemon=True
        )

        self.thread.start()

        print(f"Sample Rate: {SAMPLE_RATE}")
        print(f"Chunk Size: {CHUNK_SIZE}")
        print(f"Device Index: {MIC_INPUT_INDEX}")

    # ==================================================
    # CAPTURA CONTÍNUA DO MICROFONE
    # ==================================================

    def _capture_loop(self):

        while self.running:

            try:

                data = self.stream.read(
                    CHUNK_SIZE,
                    exception_on_overflow=False
                )

                with self.lock:
                    self.buffer_queue.append(data)

            except Exception as e:
                print("Erro audio:", e)

            # pequeno sleep evita CPU 100%
            time.sleep(0.001)

    # ==================================================
    # LIMPAR BUFFER (ANTES DO STT)
    # ==================================================

    def clear_buffer(self):

        with self.lock:
            self.buffer_queue.clear()

    # ==================================================
    # OBTER ÚLTIMO CHUNK (WAKEWORD)
    # ==================================================

    def get_latest_chunk(self):

        with self.lock:

            if len(self.buffer_queue) == 0:
                return None

            return self.buffer_queue[-1]

    # ==================================================
    # OBTER VÁRIOS CHUNKS (STT)
    # ==================================================

    def get_audio_frames(self, num_chunks=30):

        with self.lock:

            if len(self.buffer_queue) < num_chunks:
                return None

            frames = list(self.buffer_queue)[-num_chunks:]

        return b"".join(frames)

    # ==================================================
    # NÍVEL DE ÁUDIO (HUD)
    # ==================================================

    def get_audio_level(self):

        with self.lock:

            if len(self.buffer_queue) == 0:
                return 0

            pcm = np.frombuffer(
                self.buffer_queue[-1],
                dtype=np.int16
            )

        if len(pcm) == 0:
            return 0

        level = np.abs(pcm).mean() / 32768

        return float(level)

    # ==================================================
    # ENCERRAR AUDIO
    # ==================================================

    def stop(self):

        self.running = False

        try:
            self.stream.stop_stream()
            self.stream.close()
        except:
            pass

        try:
            self.p.terminate()
        except:
            pass