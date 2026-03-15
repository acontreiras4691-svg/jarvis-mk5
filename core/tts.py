import edge_tts
import asyncio
import threading
import io

from PyQt6.QtCore import QObject, pyqtSignal

from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range
import simpleaudio as sa

from core.logger import log
from config.configuracoes import (
    VOICE_TTS,
    TTS_RATE,
    TTS_PITCH,
    TTS_VOLUME,
    TTS_MODO_STARK
)


class TTS(QObject):

    callback_signal = pyqtSignal(object)

    def __init__(self):
        super().__init__()

        log("🔊 TTS Stark Production Ready inicializado.")

        self.voice = VOICE_TTS
        self.rate = TTS_RATE
        self.pitch = TTS_PITCH
        self.volume = TTS_VOLUME

        self.on_start_speak = None
        self.on_end_speak = None

        self.play_obj = None
        self.is_speaking = False

        self.lock = threading.Lock()
        self._stop_requested = False

        self.callback_signal.connect(self._executar_callback_main_thread)

    # ==================================================
    # 🎤 FALAR
    # ==================================================

    def falar(self, texto: str):

        if not texto or not texto.strip():
            return

        if self.is_speaking:
            self.stop()

        self._stop_requested = False

        inicio_cb = self.on_start_speak
        fim_cb = self.on_end_speak

        thread = threading.Thread(
            target=self._executar_tts,
            args=(texto, inicio_cb, fim_cb),
            daemon=True
        )
        thread.start()

    # ==================================================
    # 🔥 EXECUÇÃO
    # ==================================================

    def _executar_tts(self, texto, inicio_cb, fim_cb):

        with self.lock:
            self.is_speaking = True

        try:
            if callable(inicio_cb):
                self.callback_signal.emit(inicio_cb)

            audio_bytes = self._gerar_audio_sync(texto)

            if self._stop_requested:
                return

            audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
            audio = self._processar_stark(audio)

            if self._stop_requested:
                return

            self.play_obj = sa.play_buffer(
                audio.raw_data,
                num_channels=audio.channels,
                bytes_per_sample=audio.sample_width,
                sample_rate=audio.frame_rate
            )

            self.play_obj.wait_done()

        except Exception as e:
            log(f"❌ Erro TTS: {e}")

        finally:
            self.play_obj = None
            self.is_speaking = False

            if (not self._stop_requested) and callable(fim_cb):
                self.callback_signal.emit(fim_cb)

    # ==================================================
    # 🔹 CALLBACK MAIN THREAD
    # ==================================================

    def _executar_callback_main_thread(self, callback):
        try:
            if callable(callback):
                callback()
        except Exception as e:
            log(f"❌ Erro callback TTS: {e}")

    # ==================================================
    # 🔹 GERAR ÁUDIO (SAFE LOOP)
    # ==================================================

    def _gerar_audio_sync(self, texto):

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            audio = loop.run_until_complete(
                self._gerar_audio_bytes(texto)
            )
        finally:
            loop.close()

        return audio

    # ==================================================
    # 🔹 EDGE TTS
    # ==================================================

    async def _gerar_audio_bytes(self, texto):

        comunicar = edge_tts.Communicate(
            text=texto,
            voice=self.voice,
            rate=self.rate,
            pitch=self.pitch,
            volume=self.volume
        )

        chunks = []

        async for chunk in comunicar.stream():
            if self._stop_requested:
                break

            if chunk["type"] == "audio":
                chunks.append(chunk["data"])

        return b"".join(chunks)

    # ==================================================
    # 🔹 PROCESSAMENTO STARK
    # ==================================================

    def _processar_stark(self, audio):

        audio = normalize(audio)

        audio = compress_dynamic_range(
            audio,
            threshold=-23.0,
            ratio=3.2,
            attack=4,
            release=60
        )

        if TTS_MODO_STARK:

            grave = audio.low_pass_filter(180)
            audio = audio.overlay(grave - 20)

            audio = audio.high_pass_filter(90)

            presenca = audio.high_pass_filter(3500).low_pass_filter(6000)
            audio = audio.overlay(presenca - 20)

            reflexao = audio - 35
            audio = audio.overlay(reflexao, position=8)

        return audio

    # ==================================================
    # 🛑 STOP
    # ==================================================

    def stop(self):

        self._stop_requested = True

        try:
            if self.play_obj and self.is_speaking:
                log("🛑 TTS interrompido")
                self.play_obj.stop()
        except Exception:
            pass

        self.play_obj = None
        self.is_speaking = False