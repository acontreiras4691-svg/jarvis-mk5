import pyaudio
import numpy as np

p = pyaudio.PyAudio()

print("Testar microfones...\n")

for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)

    if dev["maxInputChannels"] > 0:
        print(f"\n🎤 TESTAR index={i} | {dev['name']}")

        try:
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                input_device_index=i,
                frames_per_buffer=1024
            )

            print("👉 Fala agora... (2 segundos)")

            frames = []
            for _ in range(30):
                data = stream.read(1024, exception_on_overflow=False)
                frames.append(data)

            stream.stop_stream()
            stream.close()

            audio = np.frombuffer(b"".join(frames), dtype=np.int16)
            volume = np.abs(audio).mean() / 32768.0

            print(f"🔊 Volume detectado: {volume:.4f}")

            if volume > 0.01:
                print("✅ ESTE FUNCIONA")
            else:
                print("❌ Sem som")

        except Exception as e:
            print(f"❌ Erro: {e}")

p.terminate()