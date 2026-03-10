import asyncio
import uuid
import os

import edge_tts
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range

# 🔵 VOZ PORTUGAL
VOICE = "pt-PT-DuarteNeural"

async def gerar_base(texto, ficheiro_saida):
    comunicar = edge_tts.Communicate(
        text=texto,
        voice=VOICE,
        rate="-10%",
        pitch="-6Hz",
        volume="+10%"
    )
    await comunicar.save(ficheiro_saida)


def processar_audio(input_file, output_file):

    audio = AudioSegment.from_file(input_file)

    # 1️⃣ Normalização + Compressão
    audio = normalize(audio)
    audio = compress_dynamic_range(
        audio,
        threshold=-23.0,
        ratio=3.2,
        attack=4,
        release=60
    )

    # 2️⃣ Corpo grave controlado
    grave = audio.low_pass_filter(180)
    audio = audio.overlay(grave - 20)
    audio = audio.high_pass_filter(90)

    # 3️⃣ Presença metálica suave
    presenca = audio.high_pass_filter(3500).low_pass_filter(6000)
    audio = audio.overlay(presenca - 20)

    # 4️⃣ Micro reflexão
    reflexao = audio - 30
    audio = audio.overlay(reflexao, position=8)

    # 5️⃣ Reverb Stark subtil
    reverb = (audio - 28).fade_in(15).fade_out(100)
    audio = audio.overlay(reverb, position=35)

    audio.export(output_file, format="wav")


def main():

    texto = "Boa noite, Dudu. Todos os sistemas estão operacionais."

    base_file = f"temp_{uuid.uuid4().hex}.wav"
    final_file = "jarvis_final.wav"

    asyncio.run(gerar_base(texto, base_file))
    processar_audio(base_file, final_file)

    os.remove(base_file)

    print("🎬 Voz Jarvis PT-PT gerada com sucesso:", final_file)


if __name__ == "__main__":
    main()