import pyaudio
import threading
import numpy as np
import collections
import time

from core.logger import log
from config.configuracoes import (
    MIC_INPUT_INDEX,
    SAMPLE_RATE,
    CHUNK_SIZE,
    CHANNELS
)


class AudioManager:

    def __init__(self):
        log("🎤 A iniciar AudioManager...")

        self.p = pyaudio.PyAudio()
        self.stream = None
        self.running = False
        self.lock = threading.Lock()

        self.buffer_queue = collections.deque(maxlen=200)

        self.device_index = self._resolver_dispositivo()

        self._abrir_stream()

        self.running = True

        self.thread = threading.Thread(
            target=self._capture_loop,
            daemon=True,
            name="AudioCaptureThread"
        )
        self.thread.start()

        log("✅ AudioManager pronto.")
        log(f"Sample Rate: {SAMPLE_RATE}")
        log(f"Chunk Size: {CHUNK_SIZE}")
        log(f"Channels: {CHANNELS}")
        log(f"Device Index: {self.device_index}")

        try:
            info = self.p.get_device_info_by_index(self.device_index)
            log(f"Microfone ativo: {info.get('name', 'Desconhecido')}")
        except Exception as e:
            log(f"⚠️ Não foi possível obter nome do microfone: {e}")

    # ==================================================
    # RESOLVER DISPOSITIVO
    # ==================================================

    def _resolver_dispositivo(self):
        try:
            info = self.p.get_device_info_by_index(MIC_INPUT_INDEX)

            if int(info.get("maxInputChannels", 0)) > 0:
                return MIC_INPUT_INDEX

            log(f"⚠️ Device index {MIC_INPUT_INDEX} não é uma entrada válida.")

        except Exception as e:
            log(f"⚠️ MIC_INPUT_INDEX inválido ({MIC_INPUT_INDEX}): {e}")

        try:
            default_info = self.p.get_default_input_device_info()
            idx = int(default_info["index"])
            log(f"🔄 A usar microfone default: {default_info.get('name', 'Desconhecido')}")
            return idx
        except Exception as e:
            log(f"❌ Não foi possível obter microfone default: {e}")
            raise

    # ==================================================
    # ABRIR STREAM
    # ==================================================

    def _abrir_stream(self):
        try:
            self.stream = self.p.open(
                rate=SAMPLE_RATE,
                channels=CHANNELS,
                format=pyaudio.paInt16,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=CHUNK_SIZE,
                start=True
            )
        except Exception as e:
            log(f"❌ Erro ao abrir stream de áudio: {e}")
            raise

    # ==================================================
    # CAPTURA CONTÍNUA
    # ==================================================

    def _capture_loop(self):
        log("🎧 Thread de captura de áudio iniciada.")

        while self.running:
            try:
                if self.stream is None:
                    time.sleep(0.05)
                    continue

                if not self.stream.is_active():
                    time.sleep(0.01)
                    continue

                data = self.stream.read(
                    CHUNK_SIZE,
                    exception_on_overflow=False
                )

                if data:
                    with self.lock:
                        self.buffer_queue.append(data)

            except Exception as e:
                log(f"❌ Erro audio: {e}")
                time.sleep(0.05)

        log("🛑 Thread de captura de áudio terminada.")

    # ==================================================
    # LIMPAR BUFFER
    # ==================================================

    def clear_buffer(self):
        with self.lock:
            self.buffer_queue.clear()

    # ==================================================
    # ÚLTIMO CHUNK
    # ==================================================

    def get_latest_chunk(self):
        with self.lock:
            if not self.buffer_queue:
                return None
            return self.buffer_queue[-1]

    # ==================================================
    # VÁRIOS CHUNKS
    # ==================================================

    def get_audio_frames(self, num_chunks=30):
        with self.lock:
            if len(self.buffer_queue) < num_chunks:
                return None

            frames = list(self.buffer_queue)[-num_chunks:]

        return b"".join(frames)

    # ==================================================
    # NÍVEL DE ÁUDIO
    # ==================================================

    def get_audio_level(self):
        with self.lock:
            if not self.buffer_queue:
                return 0.0

            pcm = np.frombuffer(self.buffer_queue[-1], dtype=np.int16)

        if len(pcm) == 0:
            return 0.0

        level = np.abs(pcm).mean() / 32768.0
        return float(level)

    # ==================================================
    # LISTAR DISPOSITIVOS
    # ==================================================

    def listar_dispositivos(self):
        dispositivos = []

        for i in range(self.p.get_device_count()):
            try:
                info = self.p.get_device_info_by_index(i)
                dispositivos.append({
                    "index": i,
                    "name": info.get("name", ""),
                    "maxInputChannels": int(info.get("maxInputChannels", 0))
                })
            except Exception:
                pass

        return dispositivos

    # ==================================================
    # ENCERRAR
    # ==================================================

    def stop(self):
        self.running = False

        try:
            if hasattr(self, "thread") and self.thread is not None:
                self.thread.join(timeout=0.5)
        except Exception:
            pass

        try:
            if self.stream is not None:
                if self.stream.is_active():
                    self.stream.stop_stream()
                self.stream.close()
        except Exception:
            pass

        try:
            self.p.terminate()
        except Exception:
            pass