import edge_tts
import asyncio
import threading
import io
import time

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


class TTS:

    def __init__(self):

        log("🔊 TTS Stark Production Ready inicializado.")

        self.voice = VOICE_TTS
        self.rate = TTS_RATE
        self.pitch = TTS_PITCH
        self.volume = TTS_VOLUME

        self.on_start_speak = None
        self.on_end_speak = None

        self.play_obj = None
        self.is_speaking = False
        self.stop_requested = False

        self.lock = threading.Lock()

    # ==================================================
    # 🎤 FALAR
    # ==================================================

    def falar(self, texto: str):

        if not texto.strip():
            return

        if self.is_speaking:
            self.stop()

        thread = threading.Thread(
            target=self._executar_tts,
            args=(texto,),
            daemon=True
        )

        thread.start()

    # ==================================================
    # 🔥 EXECUÇÃO
    # ==================================================

    def _executar_tts(self, texto):

        with self.lock:
            self.is_speaking = True
            self.stop_requested = False

        try:

            if self.on_start_speak:
                self.on_start_speak()

            audio_bytes = self._gerar_audio_sync(texto)

            if self.stop_requested:
                return

            audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
            audio = self._processar_stark(audio)

            self.play_obj = sa.play_buffer(
                audio.raw_data,
                num_channels=audio.channels,
                bytes_per_sample=audio.sample_width,
                sample_rate=audio.frame_rate
            )

            # 🔥 monitorizar playback para permitir interrupção
            while self.play_obj.is_playing():

                if self.stop_requested:

                    self.play_obj.stop()
                    break

                time.sleep(0.01)

        except Exception as e:

            log(f"❌ Erro TTS: {e}")

        finally:

            self.is_speaking = False
            self.stop_requested = False

            if self.on_end_speak:
                self.on_end_speak()

    # ==================================================
    # 🔹 GERAR ÁUDIO (SAFE LOOP)
    # ==================================================

    def _gerar_audio_sync(self, texto):

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        audio = loop.run_until_complete(
            self._gerar_audio_bytes(texto)
        )

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

            if self.stop_requested:
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
    # 🛑 STOP (INTERRUPÇÃO INTELIGENTE)
    # ==================================================

    def stop(self):

        try:

            if self.is_speaking:

                log("🛑 TTS interrompido")

                self.stop_requested = True

                if self.play_obj:
                    self.play_obj.stop()

        except:
            pass

        self.is_speaking = False