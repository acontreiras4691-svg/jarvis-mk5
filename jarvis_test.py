import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

print("🚀 A carregar Whisper...")

model = WhisperModel("base", device="cuda", compute_type="float16")

print("✅ Pronto.")
print("Fala alguma coisa...")

samplerate = 16000
duration = 3

while True:

    print("\n🎤 A ouvir...")

    audio = sd.rec(int(duration * samplerate),
                   samplerate=samplerate,
                   channels=1,
                   dtype="float32")

    sd.wait()

    audio = np.squeeze(audio)

    segments, _ = model.transcribe(
        audio,
        language="pt",
        beam_size=1
    )

    texto = "".join([seg.text for seg in segments]).strip()

    if texto:
        print("🧠 Ouvi:", texto)