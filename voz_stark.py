import asyncio
import edge_tts
from pydub import AudioSegment
from pydub.effects import normalize

TEXTO = "Dudu. Sistema totalmente operacional."
VOICE = "pt-PT-DuarteNeural"

# ==========================================
# 1️⃣ Gerar áudio base
# ==========================================
async def gerar_audio():
    comunicar = edge_tts.Communicate(
        text=TEXTO,
        voice=VOICE,
        rate="-10%",
        pitch="-8Hz",
        volume="+10%"
    )
    await comunicar.save("temp.wav")

asyncio.run(gerar_audio())

print("Base gerada.")

# ==========================================
# 2️⃣ Pós-processamento
# ==========================================
audio = AudioSegment.from_file("temp.wav")

audio = normalize(audio)

# Corpo
grave = audio.low_pass_filter(200)
audio = audio.overlay(grave - 18)

# Limpeza
audio = audio.high_pass_filter(85)

# Brilho subtil
brilho = audio.high_pass_filter(5000)
audio = audio.overlay(brilho - 22)

# Densidade IA
camada = audio - 26
audio = audio.overlay(camada)

# Micro atraso
delay = audio[3:]
audio = audio.overlay(delay - 30)

audio.export("jarvis_final.wav", format="wav")

print("🔥 Jarvis Stark final gerado.")