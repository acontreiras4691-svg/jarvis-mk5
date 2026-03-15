# ==================================================
# 🧠 JARVIS STARK MODE — CONFIGURAÇÃO GLOBAL
# ==================================================


# ==================================================
# 🔑 PICOVOICE / WAKE WORD
# ==================================================

# mete aqui a tua AccessKey do Picovoice
ACCESS_KEY = "E6Vz5M9m6Uwc3EbVA7Df3eJ8qaa6dJMxx/4iwU9LwjV3/DV377Llyg=="

# palavra que o Porcupine vai detetar
WAKEWORD_KEYWORD = "jarvis"

# 0.0 → 1.0 (mais alto = mais sensível)
WAKEWORD_SENSIBILIDADE = 0.72


# ==================================================
# 🎙️ MICROFONE
# ==================================================

# confirma depois no terminal qual é o índice certo
MIC_INPUT_INDEX = 2


# ==================================================
# 🎧 ÁUDIO (AUDIO MANAGER)
# ==================================================

# Porcupine funciona melhor com 16000 Hz, mono, int16
SAMPLE_RATE = 16000
CHUNK_SIZE = 512
CHANNELS = 1
AUDIO_FORMAT = "int16"

# deteção de fala
VOLUME_MINIMO = 0.025
SILENCIO_LIMITE = 1.25
TEMPO_MAXIMO_ESPERA_FALA = 9


# ==================================================
# 🎙️ STT — Whisper (FasterWhisper)
# ==================================================

# tiny | base | small | medium
MODELO_STT = "base"

# auto tenta GPU primeiro
DISPOSITIVO_STT = "auto"

# float16 GPU / int8 CPU
TIPO_COMPUTE_STT = "auto"


# ==================================================
# 🔊 TTS — Edge Neural (PT-PT)
# ==================================================

VOICE_TTS = "pt-PT-DuarteNeural"

# voz Stark mais natural
TTS_RATE = "-8%"
TTS_PITCH = "-6Hz"
TTS_VOLUME = "+5%"

TTS_MODO_STARK = True


# ==================================================
# 🤖 LLM — OLLAMA
# ==================================================

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_CHAT_ENDPOINT = "/api/chat"
OLLAMA_GENERATE_ENDPOINT = "/api/generate"

# modelo principal
MODELO_LLM = "mistral:7b-instruct"

# classificador rápido
MODELO_CLASSIFICADOR = "phi3:mini"

TEMPERATURA = 0.45
TEMPERATURA_CLASSIFICADOR = 0

TIMEOUT_OLLAMA = 25
MAX_HISTORICO_CURTO = 6


# ==================================================
# 🧠 MEMÓRIA — RAG
# ==================================================

TOP_K_MEMORIA = 3
PRIORIDADE_MINIMA_AUTO = 2

CAMINHO_MEMORIA = "./memoria_jarvis"
MODELO_EMBEDDING = "all-MiniLM-L6-v2"


# ==================================================
# ⚙️ SISTEMA
# ==================================================

# tempo que o Jarvis fica em conversa ativa
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
# 🤖 MODELOS AUXILIARES
# ==================================================

MODELO_RAPIDO = "llama3"
MODELO_INTELIGENTE = "mistral:7b-instruct"