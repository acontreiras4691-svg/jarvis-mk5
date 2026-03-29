# ==================================================
# 🎤 STT - JARVIS MK5
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
                    download_root="models",
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
                num_workers=1,
                download_root="models",
            )

            log("✅ Whisper CPU carregado.")

    # ==================================================
    # 🔊 FILTRO MICROFONE
    # ==================================================

    def filtrar_audio(self, audio_np):
        if audio_np is None or len(audio_np) == 0:
            return np.array([], dtype=np.float32)

        try:
            b, a = signal.butter(
                2,
                80 / (self.sample_rate / 2),
                btype="highpass",
            )
            audio_np = signal.lfilter(b, a, audio_np)
        except Exception as e:
            log(f"⚠️ Falha no filtro highpass: {e}")

        max_val = float(np.max(np.abs(audio_np))) if len(audio_np) else 0.0
        if max_val > 0:
            audio_np = audio_np / max_val

        return audio_np.astype(np.float32)

    # ==================================================
    # 🎤 CAPTURA DE VOZ
    # ==================================================

    def capturar_audio(self):
        frames = []
        pre_roll = []

        speech_started = False
        silence_count = 0
        voiced_chunks = 0

        energia_inicio = 85
        energia_silencio = 35

        pre_roll_chunks = 8
        silence_limit = 14
        max_chunks = 240

        max_wait_start = 3.0
        max_total_time = 8.0

        start = time.time()

        try:
            self.audio_manager.clear_buffer()
            time.sleep(0.10)
        except Exception as e:
            log(f"⚠️ clear_buffer falhou: {e}")

        last_chunk_id = 0

        while True:
            chunk_id, chunk = self.audio_manager.get_next_chunk_after(last_chunk_id)

            if chunk is None:
                time.sleep(0.005)

                if not speech_started and (time.time() - start > max_wait_start):
                    break

                if time.time() - start > max_total_time:
                    break

                continue

            last_chunk_id = chunk_id

            pcm = np.frombuffer(chunk, dtype=np.int16)
            if pcm.size == 0:
                continue

            energia = float(np.abs(pcm).mean())

            # --------------------------------------------
            # DETEÇÃO INICIAL DE VOZ
            # --------------------------------------------
            if not speech_started:
                pre_roll.append(chunk)
                if len(pre_roll) > pre_roll_chunks:
                    pre_roll.pop(0)

                if energia > energia_inicio:
                    speech_started = True
                    frames.extend(pre_roll)
                    voiced_chunks += 1

            else:
                frames.append(chunk)

                if energia < energia_silencio:
                    silence_count += 1
                else:
                    silence_count = 0
                    voiced_chunks += 1

            if speech_started and silence_count > silence_limit:
                break

            if len(frames) > max_chunks:
                break

            if time.time() - start > max_total_time:
                break

        if not frames:
            return None

        if voiced_chunks < 2:
            return None

        audio = b"".join(frames)

        audio_np = np.frombuffer(audio, dtype=np.int16).astype(np.float32)
        if audio_np.size == 0:
            return None

        audio_np = audio_np / 32768.0
        audio_np = self.filtrar_audio(audio_np)

        if audio_np.size == 0:
            return None

        # --------------------------------------------
        # SILERO VAD FINAL
        # --------------------------------------------
        try:
            speech = get_speech_timestamps(
                audio_np,
                self.vad_model,
                sampling_rate=16000,
                threshold=0.45,
                min_speech_duration_ms=180,
                min_silence_duration_ms=250,
                speech_pad_ms=120,
            )
        except TypeError:
            speech = get_speech_timestamps(
                audio_np,
                self.vad_model,
                sampling_rate=16000,
            )
        except Exception as e:
            log(f"⚠️ Falha no Silero VAD: {e}")
            speech = None

        if not speech:
            duracao = len(audio_np) / float(self.sample_rate)
            if duracao < 0.45:
                return None
            return audio_np

        partes = []

        for seg in speech:
            start_idx = int(seg.get("start", 0))
            end_idx = int(seg.get("end", 0))

            if end_idx > start_idx:
                partes.append(audio_np[start_idx:end_idx])

        if not partes:
            return None

        final_audio = np.concatenate(partes).astype(np.float32)

        duracao_final = len(final_audio) / float(self.sample_rate)
        if duracao_final < 0.25:
            return None

        return final_audio

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
                temperature=0.0,
                language="pt",
                task="transcribe",
                condition_on_previous_text=False,
                vad_filter=False,
            )

            texto = ""

            for segment in segments:
                frase = (segment.text or "").strip()

                if len(frase) < 2:
                    continue

                texto += " " + frase

            texto = texto.strip()

            if not texto:
                return None

            texto = self._limpar_texto(texto)

            log(f"🎤 STT: {texto}")

            return texto

        except Exception as e:
            log(f"❌ ERRO STT: {e}")
            return None

    # ==================================================
    # HELPERS
    # ==================================================

    def _limpar_texto(self, texto: str) -> str:
        texto = (texto or "").strip()

        if not texto:
            return ""

        substituicoes = {
            "  ": " ",
            " .": ".",
            " ,": ",",
            " !": "!",
            " ?": "?",
            "abdo ": "abre ",
            "abadi ": "abre ",
            "abro ": "abre ",
            "you tube": "youtube",
            "appletv": "apple tv",
        }

        for errado, correto in substituicoes.items():
            texto = texto.replace(errado, correto)

        return texto.strip()