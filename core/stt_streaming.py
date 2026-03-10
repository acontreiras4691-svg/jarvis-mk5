import queue
import numpy as np
import sounddevice as sd

from faster_whisper import WhisperModel
from silero_vad import load_silero_vad, get_speech_timestamps

from core.logger import log


class STTStreaming:

    def __init__(self):

        log("🚀 A iniciar STT Streaming")

        self.sample_rate = 16000
        self.audio_queue = queue.Queue()

        self.model = WhisperModel(
            "medium",
            device="cuda",
            compute_type="float16"
        )

        self.vad_model = load_silero_vad()

    # ------------------------------------------------

    def audio_callback(self, indata, frames, time, status):

        if status:
            print(status)

        self.audio_queue.put(indata.copy())

    # ------------------------------------------------

    def iniciar_microfone(self):

        self.stream = sd.InputStream(

            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            callback=self.audio_callback,
            blocksize=512

        )

        self.stream.start()

        log("🎤 Microfone streaming iniciado")

    # ------------------------------------------------

    def ouvir(self):

        buffer = []

        while True:

            data = self.audio_queue.get()

            buffer.append(data)

            audio = np.concatenate(buffer, axis=0)

            speech = get_speech_timestamps(

                audio.flatten(),
                self.vad_model,
                sampling_rate=self.sample_rate

            )

            if speech:

                segments, _ = self.model.transcribe(

                    audio.flatten(),

                    beam_size=2,
                    language="pt"
                )

                texto = ""

                for seg in segments:
                    texto += seg.text

                texto = texto.strip()

                if texto:
                    return texto