# ==================================================
# 🎤 STT - JARVIS MK5 (ULTRA OTIMIZADO)
# Faster Whisper + Silero VAD
# ==================================================

import os
import time
import numpy as np
import torch
import scipy.signal as signal

from faster_whisper import WhisperModel
from silero_vad import load_silero_vad, get_speech_timestamps

from core.logger import log


class STT:

    def __init__(self, audio_manager):

        self.audio_manager = audio_manager
        self.model = None
        self.sample_rate = 16000

        log("🧠 A carregar Silero VAD...")
        self.vad_model = load_silero_vad()

        os.makedirs("models", exist_ok=True)

    # ==================================================
    # 🚀 CARREGAR WHISPER
    # ==================================================

    def carregar_modelo(self):

        log("🚀 A carregar Faster-Whisper...")

        try:

            if torch.cuda.is_available():

                gpu = torch.cuda.get_device_name(0)
                log(f"🔥 GPU detectada: {gpu}")

                self.model = WhisperModel(
                    "medium",
                    device="cuda",
                    compute_type="float16",
                    cpu_threads=6,
                    num_workers=1,
                    download_root="models"
                )

                log("✅ Whisper GPU otimizado carregado.")

            else:
                raise Exception("CUDA não disponível")

        except Exception as e:

            log(f"⚠️ GPU indisponível ({e})")

            self.model = WhisperModel(
                "large-v3",
                device="cpu",
                compute_type="int8",
                cpu_threads=8,
                download_root="models"
            )

            log("✅ Whisper CPU carregado.")

    # ==================================================
    # 🔊 FILTRO MICROFONE
    # ==================================================

    def filtrar_audio(self, audio_np):

        b, a = signal.butter(
            2,
            80 / (self.sample_rate / 2),
            btype="highpass"
        )

        audio_np = signal.lfilter(b, a, audio_np)

        max_val = np.max(np.abs(audio_np))

        if max_val > 0:
            audio_np = audio_np / max_val

        return audio_np.astype(np.float32)

    # ==================================================
    # 🎤 CAPTURA DE VOZ
    # ==================================================

    def capturar_audio(self):

        frames = []

        speech_started = False
        silence_count = 0

        energia_inicio = 120
        energia_silencio = 40

        silence_limit = 8
        max_chunks = 160

        start = time.time()

        try:
            self.audio_manager.clear_buffer()
            time.sleep(0.05)
        except:
            pass

        last_chunk = None

        while True:

            chunk = self.audio_manager.get_latest_chunk()

            if chunk is None:
                time.sleep(0.002)
                continue

            if chunk == last_chunk:
                continue

            last_chunk = chunk

            pcm = np.frombuffer(chunk, dtype=np.int16)

            energia = np.abs(pcm).mean()

            # ------------------------------------------------
            # DETEÇÃO INICIAL DE VOZ (rápida)
            # ------------------------------------------------

            if not speech_started:

                if energia > energia_inicio:

                    speech_started = True
                    frames.append(chunk)

            else:

                frames.append(chunk)

                if energia < energia_silencio:
                    silence_count += 1
                else:
                    silence_count = 0

            if silence_count > silence_limit:
                break

            if len(frames) > max_chunks:
                break

            if time.time() - start > 4:
                break

        if not frames:
            return None

        audio = b"".join(frames)

        audio_np = np.frombuffer(
            audio,
            dtype=np.int16
        ).astype(np.float32)

        audio_np = audio_np / 32768.0

        audio_np = self.filtrar_audio(audio_np)

        # ------------------------------------------------
        # SILERO VAD FINAL (mais preciso)
        # ------------------------------------------------

        speech = get_speech_timestamps(
            audio_np,
            self.vad_model,
            sampling_rate=16000
        )

        if not speech:
            return None

        return audio_np

    # ==================================================
    # 🧠 TRANSCRIÇÃO
    # ==================================================

    def transcrever(self):

        if self.model is None:

            log("⚠️ Whisper não carregado.")
            return None

        try:

            audio = self.capturar_audio()

            if audio is None:
                return None

            segments, info = self.model.transcribe(

                audio,

                beam_size=2,
                best_of=2,

                temperature=0,

                language="pt",
                task="transcribe"
            )

            texto = ""

            for segment in segments:

                frase = segment.text.strip()

                if len(frase) < 2:
                    continue

                texto += " " + frase

            texto = texto.strip()

            if not texto:
                return None

            log(f"🎤 STT: {texto}")

            return texto

        except Exception as e:

            log(f"❌ ERRO STT: {e}")

            return None