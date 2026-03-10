# ==================================================
# 🎤 STT - Faster Whisper (Jarvis MK4 GPU OTIMIZADO)
# ==================================================

import tempfile
import wave
import os

from faster_whisper import WhisperModel

from core.logger import log
from config.configuracoes import CHUNK_SIZE


class STT:

    def __init__(self, audio_manager):

        self.audio_manager = audio_manager
        self.model = None
        self.sample_rate = 16000

        os.makedirs("models", exist_ok=True)

    # ==================================================
    # 🚀 CARREGAR MODELO
    # ==================================================

    def carregar_modelo(self):

        log("🚀 A carregar Faster-Whisper...")

        try:

            # GPU RTX
            self.model = WhisperModel(
                model_size_or_path="base",
                device="cuda",
                compute_type="float16",
                download_root="models"
            )

            log("✅ Whisper GPU carregado.")

        except Exception:

            log("⚠️ GPU não disponível. A usar CPU.")

            self.model = WhisperModel(
                model_size_or_path="tiny",
                device="cpu",
                compute_type="int8",
                download_root="models"
            )

            log("✅ Whisper CPU carregado.")

    # ==================================================
    # 🎤 GRAVAR ÁUDIO
    # ==================================================

    def gravar_audio(self, duracao=2):

        frames = []

        total_chunks = int((self.sample_rate / CHUNK_SIZE) * duracao)

        for _ in range(total_chunks):

            chunk = self.audio_manager.get_latest_chunk()

            if chunk:
                frames.append(chunk)

        if not frames:
            return None

        return b"".join(frames)

    # ==================================================
    # 🧠 TRANSCRIÇÃO
    # ==================================================

    def transcrever(self):

        if self.model is None:
            log("⚠️ Whisper não carregado.")
            return None

        tmp_path = None

        try:

            audio_bytes = self.gravar_audio()

            if not audio_bytes:
                return None

            # criar wav temporário
            with tempfile.NamedTemporaryFile(
                suffix=".wav",
                delete=False
            ) as tmp:

                tmp_path = tmp.name

            with wave.open(tmp_path, "wb") as wf:

                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)

                wf.writeframes(audio_bytes)

            # transcrição rápida
            segments, _ = self.model.transcribe(
                tmp_path,
                beam_size=1,
                language="pt",
                vad_filter=True,            # 🔥 remove silêncio
                vad_parameters=dict(
                    min_silence_duration_ms=300
                )
            )

            texto_final = ""

            for segment in segments:
                texto_final += segment.text

            texto_final = texto_final.strip()

            if texto_final:
                log(f"🎤 STT: {texto_final}")

            return texto_final

        except Exception as e:

            log(f"❌ ERRO STT: {e}")
            return None

        finally:

            # limpar ficheiro temporário
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except:
                    pass