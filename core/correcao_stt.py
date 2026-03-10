# ==================================================
# 🔧 CORREÇÃO DE ERROS DO STT
# ==================================================

def corrigir_texto_stt(texto: str) -> str:

    texto = texto.lower()

    correcoes = {
        "jarvas": "jarvis",
        "jalves": "jarvis",
        "javis": "jarvis",
        "celular": "solar",
        "selular": "solar",
    }

    palavras = texto.split()

    palavras = [correcoes.get(p, p) for p in palavras]

    return " ".join(palavras)