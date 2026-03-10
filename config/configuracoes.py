# ==================================================
# 🧠 IDENTIDADE
# ==================================================

NOME_ASSISTENTE = "jarvis"


# ==================================================
# 🔐 WAKE WORD (Porcupine)
# ==================================================

ACCESS_KEY = "E6Vz5M9m6Uwc3EbVA7Df3eJ8qaa6dJMxx/4iwU9LwjV3/DV377Llyg=="
WAKEWORD_KEYWORD = "Jarvis"

# ==================================================
# 🧠 JARVIS STARK MODE — CONFIGURAÇÃO GLOBAL
# ==================================================


# ==================================================
# 🎙️ MICROFONE & WAKE WORD
# ==================================================

# ⚠️ Verifica sempre se o índice corresponde ao micro correto
MIC_INPUT_INDEX = 1

# palavra que o Porcupine vai detectar
WAKEWORD_KEYWORD = "jarvis"

# ==================================================
# 🔊 WAKE WORD
# ==================================================

# 0.0 → 1.0 (mais alto = mais sensível)
WAKEWORD_SENSIBILIDADE = 0.72


# ==================================================
# 🎧 ÁUDIO (AUDIO MANAGER)
# ==================================================

SAMPLE_RATE = 16000

# Porcupine usa 512
CHUNK_SIZE = 512

CHANNELS = 1
AUDIO_FORMAT = "int16"

# 🔊 Detecção de fala (ajustada para micro USB)
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

OLLAMA_BASE_URL = "http://localhost:11434/api"

OLLAMA_CHAT_ENDPOINT = "/chat"
OLLAMA_GENERATE_ENDPOINT = "/generate"

# modelo principal
MODELO_LLM = "llama3:8b"

# classificador rápido
MODELO_CLASSIFICADOR = "phi3:mini"

TEMPERATURA = 0.45
TEMPERATURA_CLASSIFICADOR = 0

TIMEOUT_OLLAMA = 45

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

# tempo que Jarvis fica em conversa ativa
TEMPO_TIMEOUT_CONVERSA = 60

INTERVALO_CHECK_PROATIVO = 120

LOG_ATIVO = True
MODO_DEBUG = False

# produção
MEDIR_LATENCIA = False


# ==================================================
# 🔒 SEGURANÇA
# ==================================================

CONFIRMAR_ACOES_CRITICAS = True


# ==================================================
# 🤖 MODELOS MK4
# ==================================================

MODELO_RAPIDO = "llama3"
MODELO_INTELIGENTE = "mistral:7b-instruct"