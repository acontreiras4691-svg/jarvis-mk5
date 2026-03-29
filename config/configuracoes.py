# ==================================================
# 🔐 PICOVOICE (WAKEWORD)
# ==================================================

ACCESS_KEY = "E6Vz5M9m6Uwc3EbVA7Df3eJ8qaa6dJMxx/4iwU9LwjV3/DV377Llyg=="


# ==================================================
# 🎤 WAKEWORD
# ==================================================

WAKEWORD_KEYWORD = "jarvis"
WAKEWORD_SENSIBILIDADE = 0.72


# ==================================================
# 🎙️ MICROFONE
# ==================================================

MIC_INPUT_INDEX = 1  # Voicemod


# ==================================================
# 🎧 ÁUDIO
# ==================================================

SAMPLE_RATE = 16000
CHUNK_SIZE = 512
CHANNELS = 1
AUDIO_FORMAT = "int16"

VOLUME_MINIMO = 0.010
SILENCIO_LIMITE = 2.5
TEMPO_MAXIMO_ESPERA_FALA = 14


# ==================================================
# 🎙️ STT
# ==================================================

MODELO_STT = "base"
DISPOSITIVO_STT = "auto"
TIPO_COMPUTE_STT = "auto"


# ==================================================
# 🔊 TTS
# ==================================================

VOICE_TTS = "pt-PT-DuarteNeural"
TTS_RATE = "-8%"
TTS_PITCH = "-6Hz"
TTS_VOLUME = "+5%"
TTS_MODO_STARK = True


# ==================================================
# 🌐 SERVIDOR (LINUX)
# ==================================================

USAR_SERVIDOR_REMOTO = True

JARVIS_SERVER_URL = "http://192.168.1.108:5050/comando"
TIMEOUT_SERVER = 12


# ==================================================
# 🤖 FALLBACK LOCAL
# ==================================================

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_CHAT_ENDPOINT = "/api/chat"

MODELO_LLM = "qwen3:4b"
MODELO_CLASSIFICADOR = "phi3:mini"

TEMPERATURA = 0.45
TEMPERATURA_CLASSIFICADOR = 0

TIMEOUT_OLLAMA = 25
MAX_HISTORICO_CURTO = 6


# ==================================================
# 🧠 MEMÓRIA
# ==================================================

TOP_K_MEMORIA = 3
PRIORIDADE_MINIMA_AUTO = 2

CAMINHO_MEMORIA = "./memoria_jarvis"
MODELO_EMBEDDING = "all-MiniLM-L6-v2"


# ==================================================
# ⚙️ SISTEMA
# ==================================================

TEMPO_TIMEOUT_CONVERSA = 60
INTERVALO_CHECK_PROATIVO = 120

LOG_ATIVO = True
MODO_DEBUG = False
MEDIR_LATENCIA = False


# ==================================================
# 🔒 SEGURANÇA
# ==================================================

CONFIRMAR_ACOES_CRITICAS = True


# ==================================================
# 🤖 AUX
# ==================================================

MODELO_RAPIDO = "qwen3:4b"
MODELO_INTELIGENTE = "qwen3:8b"